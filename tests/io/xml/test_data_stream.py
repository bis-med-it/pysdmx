import re
import threading
from io import BytesIO
from pathlib import Path

import httpx
import pandas as pd
import pytest
from lxml import etree

import pysdmx.io.xml.__data_aux as data_aux
from pysdmx.errors import Invalid
from pysdmx.io import read_sdmx
from pysdmx.io.xml.doc_validation import validate_doc
from pysdmx.io.xml.header import parse_header
from pysdmx.io.xml.header import read as read_header
from pysdmx.io.xml.sdmx21.reader.generic import read as read_generic
from pysdmx.io.xml.sdmx21.reader.generic import read_stream
from pysdmx.io.xml.sdmx21.reader.structure_specific import (
    read as read_str_spe_21,
)
from pysdmx.io.xml.sdmx30.reader.structure_specific import (
    read as read_str_spe_30,
)
from tests.io.byte_chunks import ByteChunks, split

SAMPLES_21 = Path(__file__).parent / "sdmx21" / "reader" / "samples"
SAMPLES_30 = Path(__file__).parent / "sdmx30" / "reader" / "samples"
SAMPLES_31 = Path(__file__).parent / "sdmx31" / "reader" / "samples"
URL = "https://sdmx.example.org/data"
FIRST_OBS_21 = (
    '<Obs TIME_PERIOD="2002" OBS_VALUE="" OBS_STATUS="M" OBS_CONF="F"/>'
)
UNKNOWN_IN_HEADER = (
    "</message:Header>",
    "<message:Unknown/></message:Header>",
)


def sample(name, folder=SAMPLES_21):
    return (folder / name).read_text(encoding="utf-8")


def dataset_bounds(text):
    start = text.index("<message:DataSet")
    end = text.index("</message:DataSet>") + len("</message:DataSet>")
    return start, end


def assert_same_datasets(actual, expected):
    assert len(actual) == len(expected)
    for a, e in zip(actual, expected):
        assert (a.structure, a.attributes, a.action) == (
            e.structure,
            e.attributes,
            e.action,
        )
        pd.testing.assert_frame_equal(a.data, e.data)


@pytest.mark.parametrize(
    ("name", "old", "new"),
    [
        ("gen_all.xml", *UNKNOWN_IN_HEADER),
        ("gen_ser.xml", "<generic:Obs>", "<generic:Obs><generic:Unknown/>"),
    ],
)
def test_validation_matches_validate_doc(name, old, new):
    text = sample(name).replace(old, new, 1)
    with pytest.raises(Invalid) as expected:
        validate_doc(text)
    with pytest.raises(Invalid) as actual:
        read_generic(text, validate=True)
    assert actual.value.description == expected.value.description


def test_validate_doc_accepts_allowed_errors():
    # The xsi:type of a StructureSpecific DataSet cannot be resolved
    assert validate_doc(sample("str_ser.xml")) is None


def test_validation_errors_come_first():
    text = (
        sample("gen_ser.xml")
        .replace('structureRef="BIS_BIS_DER_1_0"', 'structureRef="ZZZ"')
        .replace(*UNKNOWN_IN_HEADER, 1)
    )
    with pytest.raises(Invalid, match="Validation Error"):
        read_generic(text, validate=True)
    with pytest.raises(Invalid, match="Dataset Structure Reference ZZZ"):
        read_generic(text, validate=False)


@pytest.mark.parametrize("validate", [True, False])
@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda t: t[: len(t) // 2], "Couldn't find end of Start Tag"),
        (lambda t: t.rstrip() + "<!--", "Comment not terminated"),
        (
            lambda t: t.replace("</generic:Series>", "</generic:Seriez>", 1),
            "Opening and ending tag mismatch",
        ),
    ],
)
def test_malformed_xml(change, message, validate):
    text = change(sample("gen_ser.xml"))
    with pytest.raises(etree.XMLSyntaxError, match=message):
        read_generic(text, validate=validate)


@pytest.mark.parametrize("validate", [True, False])
def test_wrong_message_generic(validate):
    with pytest.raises(
        Invalid, match="This SDMX document is not SDMX-ML 2.1 Generic."
    ):
        read_generic(sample("str_ser.xml"), validate=validate)


def test_validation_is_thread_safe():
    valid = sample("gen_ser.xml")
    invalid = valid.replace(*UNKNOWN_IN_HEADER, 1)
    failures = []

    def read(text, should_fail):
        for _ in range(10):
            try:
                read_generic(text, validate=True)
                failed = False
            except Invalid as e:
                failed = "Unknown" in str(e)
            if failed != should_fail:
                failures.append(text)

    threads = [
        threading.Thread(target=read, args=(valid, False)),
        threading.Thread(target=read, args=(invalid, True)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert failures == []


@pytest.mark.parametrize(
    ("name", "element"),
    [
        ("gen_ser.xml", "<generic:SeriesKey>"),
        ("gen_all.xml", "<generic:ObsKey>"),
    ],
)
def test_generic_comments_and_pis_ignored(name, element):
    text = sample(name)
    noisy = text.replace(
        "<generic:Obs>", "<generic:Obs><!-- c --><?pi x?>", 1
    ).replace(element, f"{element}<!-- k --><?pi y?>", 1)
    assert_same_datasets(read_generic(noisy), read_generic(text))


def test_generic_dataset_attributes():
    dataset = read_generic(sample("gen_ser.xml"))[0]
    assert dataset.attributes == {
        "DECIMALS": "3",
        "UNIT_MULT": "6",
        "UNIT_MEASURE": "USD",
    }


def test_generic_other_children_of_a_key_are_ignored():
    text = sample("gen_all.xml")
    extra = text.replace(
        "<generic:ObsKey>", "<generic:ObsKey><generic:Extra/>", 1
    )
    assert_same_datasets(
        read_generic(extra, validate=False), read_generic(text)
    )


@pytest.mark.parametrize(
    ("name", "pattern", "key"),
    [
        ("gen_ser.xml", r"<generic:ObsDimension[^>]*/>", "ObsDimension"),
        ("gen_all.xml", r"<generic:ObsKey>.*?</generic:ObsKey>", "ObsKey"),
    ],
)
def test_generic_obs_without_dimension_or_key(name, pattern, key):
    # As reading the whole message did, with its dictionary lookups
    text = re.sub(pattern, "", sample(name), count=1, flags=re.DOTALL)
    with pytest.raises(KeyError, match=key):
        read_generic(text, validate=False)


def test_generic_missing_obs_value():
    text = sample("gen_all.xml").replace('<generic:ObsValue value=""/>', "", 1)
    data = read_generic(text)[0].data
    assert data["OBS_VALUE"].iloc[0] == ""


def test_generic_all_dimensions_without_obs():
    text = re.sub(
        r"<generic:Obs>.*?</generic:Obs>",
        "",
        sample("gen_all.xml"),
        flags=re.DOTALL,
    )
    dataset = read_generic(text)[0]
    pd.testing.assert_frame_equal(dataset.data, pd.DataFrame())
    assert dataset.attributes == {
        "DECIMALS": "3",
        "UNIT_MULT": "6",
        "UNIT_MEASURE": "USD",
    }


def test_generic_default_namespace():
    # The unprefixed Ref elements move to the message namespace, which the
    # XSD rejects: the names are what matters here
    text = sample("gen_ser.xml")
    default = (
        text.replace("xmlns:message=", "xmlns=")
        .replace("<message:", "<")
        .replace("</message:", "</")
    )
    assert_same_datasets(
        read_generic(default, validate=False),
        read_generic(text, validate=False),
    )


def test_generic_two_datasets():
    text = sample("gen_ser.xml")
    start, end = dataset_bounds(text)
    twice = text[:end] + text[start:end] + text[end:]
    datasets = read_generic(twice)
    assert_same_datasets(datasets[:1], datasets[1:])
    assert_same_datasets(datasets[:1], read_generic(text))


def test_generic_header_only():
    text = sample("gen_ser.xml")
    start, end = dataset_bounds(text)
    header, datasets = read_stream([text[:start] + text[end:]])
    assert datasets == []
    assert parse_header(header) == read_header(text, validate=False)


def test_read_stream_returns_the_header():
    text = sample("gen_ser.xml")
    header, datasets = read_stream([text])
    assert parse_header(header) == read_header(text, validate=False)
    assert_same_datasets(datasets, read_generic(text))


def test_header_not_first_child():
    text = sample("gen_ser.xml")
    extra = text.replace(
        "<message:Header>", "<message:Extra/><message:Header>", 1
    )
    header, datasets = read_stream([extra], validate=False)
    assert header is None
    assert_same_datasets(datasets, read_generic(text))


def test_data_elements_outside_a_dataset_are_ignored():
    text = sample("gen_ser.xml")
    noisy = text.replace(
        "</message:Header>", "<message:Obs/></message:Header>", 1
    ).replace("<message:DataSet", "<message:Group/><message:DataSet", 1)
    header, datasets = read_stream([noisy], validate=False)
    assert parse_header(header) == read_header(text, validate=False)
    assert_same_datasets(datasets, read_generic(text))


def test_no_header():
    text = sample("gen_ser.xml")
    start = text.index("<message:Header>")
    end = text.index("</message:Header>") + len("</message:Header>")
    with pytest.raises(KeyError, match="Header"):
        read_generic(text[:start] + text[end:], validate=False)


def test_empty_header():
    text = sample("gen_ser.xml")
    start = text.index("<message:Header>")
    end = text.index("</message:Header>") + len("</message:Header>")
    with pytest.raises(TypeError):
        read_generic(
            text[:start] + "<message:Header/>" + text[end:], validate=False
        )


def test_empty_header_without_namespaces():
    with pytest.raises(TypeError):
        read_generic(
            '<?xml version="1.0"?><GenericData><Header/></GenericData>',
            validate=False,
        )


def test_missing_structure_ref():
    text = sample("gen_ser.xml").replace(
        'structureRef="BIS_BIS_DER_1_0" ', "", 1
    )
    with pytest.raises(KeyError, match="structureRef"):
        read_generic(text, validate=False)


def test_severe_error_kept_after_many_allowed_errors():
    # Each DataSet adds 2 allowed xsi:type errors after the severe one: 600
    # errors, while lxml only keeps the last 100 of the thread
    text = sample("str_ser.xml")
    start, end = dataset_bounds(text)
    tiny = (
        '<message:DataSet ss:structureRef="BIS_DER" '
        'xsi:type="ns1:DataSetType"/>'
    )
    message = (text[:start] + tiny * 300 + text[end:]).replace(
        *UNKNOWN_IN_HEADER, 1
    )
    with pytest.raises(Invalid) as expected:
        validate_doc(message)
    with pytest.raises(Invalid) as actual:
        read_str_spe_21(message, validate=True)
    assert actual.value.description == expected.value.description
    datasets = read_str_spe_21(message, validate=False)
    assert len(datasets) == 300
    assert all(dataset.data.empty for dataset in datasets)


def test_ss_series_missing_values_are_null():
    text = sample("str_ser.xml").replace(
        FIRST_OBS_21, FIRST_OBS_21.replace(' OBS_CONF="F"', ""), 1
    )
    data = read_str_spe_21(text)[0].data
    assert pd.isna(data["OBS_CONF"].iloc[0])
    assert data["OBS_CONF"].iloc[1] == "F"


def test_ss_attribute_first_reported_in_a_later_batch(monkeypatch):
    # The rows of the batches already built get a null value
    monkeypatch.setattr(data_aux, "READING_CHUNKSIZE", 100)
    text = sample("str_ser.xml")
    last = text.rindex("<Obs ")
    late = text[:last] + '<Obs OBS_PRE_BREAK="9" ' + text[last + 5 :]
    data = read_str_spe_21(late)[0].data
    assert len(data) == 1000
    assert data["OBS_PRE_BREAK"].iloc[-1] == "9"
    assert data["OBS_PRE_BREAK"].iloc[:-1].isna().all()


def test_ss_all_dimensions_missing_values_are_empty():
    text = sample("str_all.xml").replace(' DER_RATING="A"', "", 1)
    data = read_str_spe_21(text)[0].data
    assert data["DER_RATING"].iloc[0] == ""
    assert data["DER_RATING"].iloc[1] == "A"


def test_ss_series_win_over_top_level_obs():
    text = sample("str_ser.xml")
    mixed = text.replace(
        "</message:DataSet>",
        '<Obs TIME_PERIOD="1999" OBS_VALUE="1"/></message:DataSet>',
        1,
    )
    assert_same_datasets(
        read_str_spe_21(mixed, validate=False), read_str_spe_21(text)
    )


def test_ss_default_namespace():
    text = sample("str_ser.xml")
    default = (
        text.replace("xmlns:message=", "xmlns=")
        .replace("<message:", "<")
        .replace("</message:", "</")
    )
    assert_same_datasets(
        read_str_spe_21(default, validate=False),
        read_str_spe_21(text, validate=False),
    )


def test_ss_30_reader_reads_21_message():
    # The namespaces come from the message, not from the reader
    text = sample("str_ser.xml")
    assert_same_datasets(read_str_spe_30(text), read_str_spe_21(text))


def test_ss_namespace_declarations_ignored():
    text = sample("str_ser.xml")
    declared = text.replace(
        "<message:DataSet ", '<message:DataSet xmlns:x="urn:x" ', 1
    ).replace("<Obs ", '<Obs xmlns:o="urn:o" ', 1)
    assert_same_datasets(read_str_spe_21(declared), read_str_spe_21(text))


def test_ss_child_elements_ignored():
    text_21 = sample("str_ser.xml")
    provider = text_21.replace(
        'action="Replace">',
        'action="Replace"><DataProvider><Ref agencyID="BIS" '
        'maintainableParentID="DATA_PROVIDERS" '
        'maintainableParentVersion="1.0" id="P1"/></DataProvider>',
        1,
    )
    assert_same_datasets(read_str_spe_21(provider), read_str_spe_21(text_21))

    text_30 = sample("data_dataflow_3.0.xml", SAMPLES_30)
    component = re.sub(
        r"(<Obs\b[^>]*?)/>",
        r'\1><Comp id="X"><Value>v</Value></Comp></Obs>',
        text_30,
        count=1,
        flags=re.DOTALL,
    )
    assert_same_datasets(
        read_str_spe_30(component, validate=False), read_str_spe_30(text_30)
    )


@pytest.mark.parametrize(
    "path",
    [
        SAMPLES_21 / "gen_ser.xml",
        SAMPLES_21 / "str_ser.xml",
        SAMPLES_30 / "data_dataflow_3.0.xml",
        SAMPLES_31 / "ECB_EXR_data.xml",
    ],
)
def test_read_sdmx_data_same_message_from_every_source(path, respx_mock):
    text = path.read_text(encoding="utf-8")
    body = path.read_bytes()
    stream = ByteChunks(split(body, len(body) // 3 + 1))
    respx_mock.get(URL).mock(return_value=httpx.Response(200, stream=stream))

    expected = read_sdmx(path)

    assert expected.header == read_header(text, validate=False)
    for source in (str(path), text, BytesIO(body), URL):
        message = read_sdmx(source)
        assert message.header == expected.header
        assert_same_datasets(message.data, expected.data)
    assert stream.closed


def test_read_sdmx_stops_reading_url_on_error(respx_mock):
    text = sample("str_ser.xml").replace(
        'ss:structureRef="BIS_DER"', 'ss:structureRef="ZZZ"', 1
    )
    chunks = split(text.encode("utf-8"), 1024)
    without_validation = ByteChunks(chunks)
    with_validation = ByteChunks(chunks)
    respx_mock.get(URL).mock(
        side_effect=[
            httpx.Response(200, stream=without_validation),
            httpx.Response(200, stream=with_validation),
        ]
    )
    reference = "Dataset Structure Reference ZZZ"

    with pytest.raises(Invalid, match=reference):
        read_sdmx(URL, validate=False)
    assert without_validation.closed
    assert without_validation.yielded < len(chunks)

    # The validation goes to the end of the message before reporting it
    with pytest.raises(Invalid, match=reference):
        read_sdmx(URL, validate=True)
    assert with_validation.closed
    assert with_validation.yielded == len(chunks)

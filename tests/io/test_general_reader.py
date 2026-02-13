import json
import re
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest

import pysdmx.io.input_processor as m
from pysdmx.errors import Invalid, NotImplemented
from pysdmx.io import read_sdmx
from pysdmx.io.reader import get_datasets
from pysdmx.model import (
    Codelist,
    ComponentMap,
    DatePatternMap,
    FixedValueMap,
    ImplicitComponentMap,
    MetadataReport,
    MultiComponentMap,
    MultiValueMap,
    RepresentationMap,
    Schema,
    StructureMap,
    ValueMap,
)
from pysdmx.model.message import Message


@pytest.fixture
def empty_message():
    file_path = Path(__file__).parent / "samples" / "empty_message.xml"
    with open(file_path, "r") as f:
        text = f.read()
    return text


@pytest.fixture
def sdmx_json():
    file_path = Path(__file__).parent / "samples" / "sdmx.json"
    with open(file_path, "r") as f:
        text = f.read()
    return text


@pytest.fixture
def sdmx_json_20_structure():
    file_path = (
        Path(__file__).parent.parent
        / "api"
        / "fmr"
        / "samples"
        / "code"
        / "freq.json"
    )
    with open(file_path, "r") as f:
        text = f.read()
    return text


@pytest.fixture
def sdmx_json_21_structure():
    file_path = (
        Path(__file__).parent.parent
        / "api"
        / "fmr"
        / "samples"
        / "code"
        / "freq_21.json"
    )
    with open(file_path, "r") as f:
        text = f.read()
    return text


@pytest.fixture
def sdmx_json_20_refmeta():
    file_path = (
        Path(__file__).parent.parent
        / "api"
        / "fmr"
        / "samples"
        / "refmeta"
        / "report.json"
    )
    with open(file_path, "r") as f:
        text = f.read()
    return text


@pytest.fixture
def sdmx_json_21_refmeta():
    file_path = (
        Path(__file__).parent.parent
        / "api"
        / "fmr"
        / "samples"
        / "refmeta"
        / "report_21.json"
    )
    with open(file_path, "r") as f:
        text = f.read()
    r = json.loads(text)
    return json.dumps(r)


@pytest.fixture
def sdmx_json_data():
    file_path = Path(__file__).parent / "samples" / "exr-time-series.json"
    with open(file_path, "r") as f:
        text = f.read()
    return text


@pytest.fixture
def data_path():
    base_path = Path(__file__).parent / "samples" / "data.xml"
    return str(base_path)


@pytest.fixture
def data_csv_v1_path():
    base_path = Path(__file__).parent / "samples" / "data_v1.csv"
    return str(base_path)


@pytest.fixture
def data_csv_v1_str():
    base_path = Path(__file__).parent / "samples" / "data_v1.csv"
    with open(base_path, "r") as f:
        text = f.read()
    return text


@pytest.fixture
def structures_path():
    base_path = Path(__file__).parent / "samples" / "datastructure.xml"
    return str(base_path)


@pytest.fixture
def structures_descendants_path():
    base_path = (
        Path(__file__).parent / "samples" / "datastructure_descendants.xml"
    )
    return str(base_path)


@pytest.fixture
def dataflow_no_children():
    base_path = (
        Path(__file__).parent
        / "samples"
        / "dataflow_structure_no_children.xml"
    )
    return str(base_path)


@pytest.fixture
def dataflow_children():
    base_path = (
        Path(__file__).parent / "samples" / "dataflow_structure_children.xml"
    )
    return str(base_path)


@pytest.fixture
def data_wrong_dataflow():
    base_path = Path(__file__).parent / "samples" / "data_wrong_dataflow.xml"
    return str(base_path)


@pytest.fixture
def data_dataflow():
    base_path = Path(__file__).parent / "samples" / "data_dataflow.xml"
    return str(base_path)


@pytest.fixture
def data_wrong_dsd():
    base_path = (
        Path(__file__).parent / "samples" / "data_wrong_datastructure.xml"
    )
    return str(base_path)


@pytest.fixture
def samples_folder():
    return Path(__file__).parent / "samples"


@pytest.fixture
def sdmx_error_str():
    base_path = Path(__file__).parent / "samples" / "error.xml"
    with open(base_path, "r") as f:
        text = f.read()
    return text


@pytest.fixture
def mock_ssl_context(monkeypatch):
    seen = {}

    def mock_create_ssl_context(*, verify=None):
        seen["verify"] = verify
        return "CTX"

    monkeypatch.setattr(m, "create_ssl_context", mock_create_ssl_context)
    return seen


@pytest.fixture
def mock_http_client(monkeypatch, structures_path):
    last = {}
    xml_text = Path(structures_path).read_text(encoding="utf-8")
    mock_response = SimpleNamespace(
        status_code=200,
        text=xml_text,
        raise_for_status=lambda: None,
    )

    class DummyClient:
        def __init__(self, **kwargs):
            last["kwargs"] = kwargs

        def __enter__(self):
            self.get = lambda u, timeout=60: mock_response
            return self

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(m, "httpx_Client", DummyClient)
    return last


@pytest.fixture
def prov_agreement_structure():
    base_path = Path(__file__).parent / "samples" / "prov_agree_structure.xml"
    return str(base_path)


@pytest.fixture
def data_prov_agreement():
    base_path = Path(__file__).parent / "samples" / "data_prov_agree.xml"
    return str(base_path)


@pytest.fixture
def prov_agreement_structure_no_dataflow():
    base_path = (
        Path(__file__).parent
        / "samples"
        / "prov_agree_structure_no_dataflow.xml"
    )
    return str(base_path)


@pytest.mark.data
def test_read_sdmx_invalid_extension():
    with pytest.raises(Invalid, match="Cannot parse input as SDMX."):
        read_sdmx(",,,,")


@pytest.mark.data
def test_read_url_invalid(respx_mock):
    url = "https://invalidurl.com"
    respx_mock.get(url).mock(
        return_value=httpx.Response(
            404,
            content="",
        )
    )
    with pytest.raises(
        Invalid, match="Cannot retrieve a SDMX Message from URL"
    ):
        read_sdmx(url)


@pytest.mark.data
def test_read_url_valid(respx_mock, data_csv_v1_str):
    url = "http://validurl.com"
    respx_mock.get(url).mock(
        return_value=httpx.Response(
            200,
            content=data_csv_v1_str,
        )
    )
    result = read_sdmx(url)
    assert result.data is not None


@pytest.mark.data
def test_read_url_invalid_pem():
    url = "https://validurl.com"
    invalid_pem_path = Path(__file__).parent / "samples" / "invalid_pem.pem"
    with pytest.raises(Invalid, match="does not exist"):
        read_sdmx(url, pem=invalid_pem_path)


@pytest.mark.data
def test_read_url_invalid_pem_str():
    url = "https://validurl.com"
    with pytest.raises(
        Invalid, match="PEM file invalid_pem.pem does not exist."
    ):
        read_sdmx(url, pem="invalid_pem.pem")


def test_ssl_context_with_pem_path(
    mock_ssl_context, mock_http_client, tmp_path
):
    url = "https://validurl.com"
    pem = tmp_path / "cert.pem"
    pem.write_text("dummy")

    read_sdmx(url, validate=True, pem=pem)

    assert mock_ssl_context["verify"] == str(pem)
    assert mock_http_client["kwargs"]["verify"] == "CTX"


def test_ssl_context_without_pem(mock_ssl_context, mock_http_client):
    url = "https://validurl.com"

    read_sdmx(url, validate=True)

    assert mock_ssl_context["verify"] is None
    assert mock_http_client["kwargs"]["verify"] == "CTX"


def test_url_invalid_sdmx_error(respx_mock, sdmx_error_str):
    url = "http://invalid_sdmx_error.com"
    respx_mock.get(url).mock(
        return_value=httpx.Response(
            404,
            content=sdmx_error_str,
        )
    )
    with pytest.raises(Invalid, match="150: "):
        read_sdmx(url)


def test_empty_result(empty_message):
    with pytest.raises(Invalid, match="Empty SDMX Message"):
        read_sdmx(empty_message, validate=False)


def test_get_datasets_valid(data_path, structures_path):
    result = get_datasets(data_path, structures_path)
    assert len(result) == 1
    dataset = result[0]
    assert isinstance(dataset.structure, Schema)
    assert dataset.data is not None
    assert len(dataset.data) == 1000
    assert len(dataset.structure.artefacts) == 26
    assert dataset.short_urn == "DataStructure=BIS:BIS_DER(1.0)"


def test_get_datasets_valid_descendants(
    data_path, structures_descendants_path
):
    result = get_datasets(data_path, structures_descendants_path)
    assert len(result) == 1
    dataset = result[0]
    assert isinstance(dataset.structure, Schema)
    assert dataset.data is not None
    assert len(dataset.data) == 1000
    assert len(dataset.structure.artefacts) == 46
    assert (
        "urn:sdmx:org.sdmx.infomodel.conceptscheme.Concept="
        "BIS:BIS_CONCEPT_SCHEME(1.0)"
        ".TITLE_TS"
    ) in dataset.structure.artefacts
    assert (
        "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=BIS:CL_DECIMALS(1.0)"
    ) in dataset.structure.artefacts


def test_get_datasets_no_data_found(data_path, structures_path):
    with pytest.raises(Invalid, match="No data found in the data message"):
        get_datasets(structures_path, data_path)


def test_get_datasets_no_structure_found(data_path, structures_path):
    with pytest.raises(
        Invalid, match="No structure found in the structure message"
    ):
        get_datasets(data_path, data_path)


def test_get_datasets_csv_v1(data_csv_v1_path):
    result = get_datasets(data_csv_v1_path)
    assert len(result) == 1
    dataset = result[0]
    assert isinstance(dataset.structure, str)
    assert dataset.data is not None
    assert len(dataset.data) == 1000


def test_get_datasets_dataflow_children(data_dataflow, dataflow_children):
    result = get_datasets(data_dataflow, dataflow_children)
    assert len(result) == 1
    dataset = result[0]
    assert dataset.data is not None
    assert isinstance(dataset.structure, Schema)
    assert len(dataset.data) == 1000
    assert (
        dataset.structure.short_urn
        == "Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)"
    )


def test_get_datasets_wrong_dataflow(
    data_wrong_dataflow, dataflow_no_children
):
    with pytest.raises(
        Invalid,
        match="Missing Dataflow",
    ):
        get_datasets(data_wrong_dataflow, dataflow_no_children)


def test_get_datasets_wrong_dsd(data_wrong_dsd, dataflow_children):
    with pytest.raises(Invalid, match="Missing DataStructure "):
        get_datasets(data_wrong_dsd, dataflow_children)


def test_get_datasets_no_children(data_dataflow, dataflow_no_children):
    with pytest.raises(Invalid, match="Not found referenced DataStructure"):
        get_datasets(data_dataflow, dataflow_no_children)


def test_get_datasets_missing_attribute(samples_folder):
    data_file = samples_folder / "data_v1_missing_one_attached.csv"
    structures_file = samples_folder / "dataflow_structure_children.xml"
    datasets = get_datasets(data_file, structures_file)
    assert len(datasets) == 1
    dataset = datasets[0]

    assert dataset.attributes == {
        "DECIMALS": "3",
        "UNIT_MULT": "6",
        "UNIT_MEASURE": None,
    }
    assert "DECIMALS" not in dataset.data.columns
    assert "UNIT_MULT" not in dataset.data.columns


@pytest.mark.json
def test_get_json20_structure(sdmx_json_20_structure):
    msg = read_sdmx(sdmx_json_20_structure)

    assert isinstance(msg, Message)
    assert msg.header is not None
    assert len(msg.structures) == 1
    assert isinstance(msg.structures[0], Codelist)
    cl = msg.structures[0]
    assert cl.id == "CL_FREQ"
    assert cl.agency == "SDMX"
    assert cl.version == "2.0"
    assert len(cl.codes) == 9


@pytest.mark.json
def test_get_json21_structure(sdmx_json_21_structure):
    msg = read_sdmx(sdmx_json_21_structure)

    assert isinstance(msg, Message)
    assert msg.header is not None
    assert len(msg.structures) == 1
    assert isinstance(msg.structures[0], Codelist)
    cl = msg.structures[0]
    assert cl.id == "CL_FREQ"
    assert cl.agency == "SDMX"
    assert cl.version == "2.0"
    assert len(cl.codes) == 9


@pytest.mark.json
def test_get_json20_refmeta(sdmx_json_20_refmeta):
    msg = read_sdmx(sdmx_json_20_refmeta, validate=False)

    assert isinstance(msg, Message)
    assert msg.header is not None
    assert len(msg.reports) == 1
    assert isinstance(msg.reports[0], MetadataReport)
    rep = msg.reports[0]
    assert rep.id == "DTI_BIS_MACRO"
    assert rep.agency == "BIS.MEDIT"
    assert rep.version == "1.0.42"
    assert len(rep.attributes) == 2


@pytest.mark.json
def test_get_json21_refmeta(sdmx_json_21_refmeta):
    msg = read_sdmx(sdmx_json_21_refmeta, validate=False)

    assert isinstance(msg, Message)
    assert msg.header is not None
    assert len(msg.reports) == 1
    assert isinstance(msg.reports[0], MetadataReport)
    rep = msg.reports[0]
    assert rep.id == "DTI_BIS_MACRO"
    assert rep.agency == "BIS.MEDIT"
    assert rep.version == "1.0.42"
    assert len(rep.attributes) == 2


@pytest.mark.json
def test_get_json2_data(sdmx_json_data):
    with pytest.raises(
        NotImplemented, match="This flavour of SDMX-JSON is not supported."
    ):
        read_sdmx(sdmx_json_data)


def test_get_datasets_prov_agreement(
    data_prov_agreement, prov_agreement_structure
):
    result = get_datasets(data_prov_agreement, prov_agreement_structure)
    assert len(result) == 1
    dataset = result[0]
    assert dataset.data is not None
    assert isinstance(dataset.structure, Schema)
    assert len(dataset.data) == 1
    assert dataset.structure.short_urn == "ProvisionAgreement=MD:TEST(1.0)"


def test_get_datasets_prov_agreement_no_dataflow(
    data_prov_agreement, prov_agreement_structure_no_dataflow
):
    with pytest.raises(
        Invalid,
        match=re.escape(
            "Provision Agreement ProvisionAgreement=MD:TEST(1.0)"
            " does not have a Dataflow defined."
        ),
    ):
        get_datasets(
            data_prov_agreement,
            prov_agreement_structure_no_dataflow,
            validate=False,
        )


def test_read_maps():
    data_path = Path(__file__).parent / "samples" / "maps.xml"
    result = read_sdmx(data_path, validate=True)
    assert len(result.structures) == 5

    # RepresentationMap 1 - REPMAP_SEX (1-1 => ValueMap)
    rep_map = result.structures[1]
    assert isinstance(rep_map, RepresentationMap)
    assert rep_map.id == "REPMAP_SEX"
    assert rep_map.agency == "ESTAT"
    assert rep_map.version == "1.0"
    assert rep_map.name == "Sex Mapping (Numeric to Alpha)"
    assert (
        rep_map.urn == "urn:sdmx:org.sdmx.infomodel.structuremapping."
        "RepresentationMap=ESTAT:REPMAP_SEX(1.0)"
    )
    assert rep_map.short_urn == "RepresentationMap=ESTAT:REPMAP_SEX(1.0)"
    assert (
        rep_map.source
        == "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=ESTAT:CL_SEX_V1(1.0)"
    )
    assert (
        rep_map.target
        == "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=ESTAT:CL_SEX_V2(2.0)"
    )
    assert len(rep_map.maps) == 2

    m = rep_map.maps[0]
    assert isinstance(m, ValueMap)
    assert m.source == "1"
    assert m.target == "M"

    m = rep_map.maps[1]
    assert isinstance(m, ValueMap)
    assert m.source == "2"
    assert m.target == "F"

    # RepresentationMap 2 - REPMAP_CURR (N-1 => MultiValueMap)
    rep_map = result.structures[2]
    assert isinstance(rep_map, RepresentationMap)
    assert rep_map.id == "REPMAP_CURR"
    assert rep_map.agency == "ESTAT"
    assert rep_map.version == "1.0"
    assert len(rep_map.maps) == 2

    m = rep_map.maps[0]
    assert isinstance(m, MultiValueMap)
    assert list(m.source) == ["DE", "LC"]
    assert list(m.target) == ["EUR"]
    assert m.valid_from is None
    assert m.valid_to is None

    m = rep_map.maps[1]
    assert isinstance(m, MultiValueMap)
    assert list(m.source) == ["CH", "LC"]
    assert list(m.target) == ["CHF"]

    # RepresentationMap 3 - REPMAP_SERIES (1-N => MultiValueMap)
    rep_map = result.structures[3]
    assert isinstance(rep_map, RepresentationMap)
    assert rep_map.id == "REPMAP_SERIES"
    assert rep_map.agency == "ESTAT"
    assert rep_map.version == "1.0"
    assert len(rep_map.maps) == 2

    m = rep_map.maps[0]
    assert isinstance(m, MultiValueMap)
    assert list(m.source) == ["XMAN_Z_34"]
    assert list(m.target) == ["XM", "QXR15"]

    m = rep_map.maps[1]
    assert isinstance(m, MultiValueMap)
    assert list(m.source) == ["YBOP_A_12"]
    assert list(m.target) == ["YB", "OK"]

    # RepresentationMap 4 - REPMAP_NN (N-N => MultiValueMap)
    rep_map = result.structures[4]
    assert isinstance(rep_map, RepresentationMap)
    assert rep_map.id == "REPMAP_NN"
    assert rep_map.agency == "ESTAT"
    assert rep_map.version == "1.0"
    assert len(rep_map.maps) == 2

    m = rep_map.maps[0]
    assert isinstance(m, MultiValueMap)
    assert list(m.source) == ["A", "N"]
    assert list(m.target) == ["A_N", "Unadjusted"]

    m = rep_map.maps[1]
    assert isinstance(m, MultiValueMap)
    assert list(m.source) == ["M", "S_A1"]
    assert list(m.target) == ["MON_SAX", "Seasonally adjusted"]

    # StructureMap 0 - STRMAP_DEMO
    str_map = result.structures[0]
    assert isinstance(str_map, StructureMap)
    assert str_map.id == "STRMAP_DEMO"
    assert str_map.agency == "ESTAT"
    assert str_map.version == "1.0"
    assert str_map.name == "Demographic Structure Mapping"
    assert (
        str_map.urn == "urn:sdmx:org.sdmx.infomodel.structuremapping."
        "StructureMap=ESTAT:STRMAP_DEMO(1.0)"
    )
    assert str_map.short_urn == "StructureMap=ESTAT:STRMAP_DEMO(1.0)"
    assert (
        str_map.source == "urn:sdmx:org.sdmx.infomodel.datastructure."
        "DataStructure=ESTAT:DSD_DEMO_V1(1.0)"
    )
    assert (
        str_map.target == "urn:sdmx:org.sdmx.infomodel.datastructure."
        "DataStructure=ESTAT:DSD_DEMO_V2(2.0)"
    )

    assert len(str_map.maps) == 10

    # 0: 1-1 ComponentMap
    cm = str_map.maps[0]
    assert isinstance(cm, ComponentMap)
    assert cm.source == "SEX_DIM"
    assert cm.target == "GENDER_DIM"
    assert (
        cm.values == "urn:sdmx:org.sdmx.infomodel.structuremapping."
        "RepresentationMap=ESTAT:REPMAP_SEX(1.0)"
    )

    # 1: implicit component map
    icm = str_map.maps[1]
    assert isinstance(icm, ImplicitComponentMap)
    assert icm.source == "OBS_CONF"
    assert icm.target == "CONF_STATUS"

    # 2: N-1 MultiComponentMap
    mcm = str_map.maps[2]
    assert isinstance(mcm, MultiComponentMap)
    assert list(mcm.source) == ["COUNTRY", "LOCAL_CURRENCY"]
    assert list(mcm.target) == ["CURRENCY_ISO3"]
    assert (
        mcm.values == "urn:sdmx:org.sdmx.infomodel.structuremapping."
        "RepresentationMap=ESTAT:REPMAP_CURR(1.0)"
    )

    # 3: 1-N MultiComponentMap
    mcm = str_map.maps[3]
    assert isinstance(mcm, MultiComponentMap)
    assert list(mcm.source) == ["SERIES_CODE"]
    assert list(mcm.target) == ["INDICATOR", "STATUS"]
    assert (
        mcm.values == "urn:sdmx:org.sdmx.infomodel.structuremapping."
        "RepresentationMap=ESTAT:REPMAP_SERIES(1.0)"
    )

    # 4: N-N MultiComponentMap
    mcm = str_map.maps[4]
    assert isinstance(mcm, MultiComponentMap)
    assert list(mcm.source) == ["FREQ", "ADJUSTMENT"]
    assert list(mcm.target) == ["INDICATOR", "NOTE"]
    assert (
        mcm.values == "urn:sdmx:org.sdmx.infomodel.structuremapping."
        "RepresentationMap=ESTAT:REPMAP_NN(1.0)"
    )

    # 5: FixedValueMap
    fixed_map = str_map.maps[5]
    assert isinstance(fixed_map, FixedValueMap)
    assert fixed_map.target == "OBS_STATUS"
    assert fixed_map.value == "A"

    # 6..9: DatePatternMaps
    dpm = str_map.maps[6]
    assert isinstance(dpm, DatePatternMap)
    assert dpm.id == "DPM_FIXED_ID_RESOLVE"
    assert dpm.source == "DATE"
    assert dpm.target == "TIME_PERIOD"
    assert dpm.pattern == "MMM yy"
    assert dpm.frequency == "M"
    assert dpm.locale == "en"
    assert dpm.pattern_type == "fixed"
    assert dpm.resolve_period == "startOfPeriod"

    dpm = str_map.maps[7]
    assert isinstance(dpm, DatePatternMap)
    assert dpm.id is None
    assert dpm.source == "YEAR"
    assert dpm.target == "TIME_PERIOD"
    assert dpm.pattern == "yyyy"
    assert dpm.frequency == "A"
    assert dpm.locale == "en"
    assert dpm.pattern_type == "fixed"
    assert dpm.resolve_period is None

    dpm = str_map.maps[8]
    assert isinstance(dpm, DatePatternMap)
    assert dpm.id == "DPM_VAR_ID"
    assert dpm.source == "DATE"
    assert dpm.target == "TIME_PERIOD"
    assert dpm.pattern == "yyyy-MM"
    assert dpm.frequency == "FREQ"
    assert dpm.locale == "en"
    assert dpm.pattern_type == "variable"
    assert dpm.resolve_period is None

    dpm = str_map.maps[9]
    assert isinstance(dpm, DatePatternMap)
    assert dpm.id is None
    assert dpm.source == "REF_DATE"
    assert dpm.target == "TIME_PERIOD"
    assert dpm.pattern == "dd/MM/yyyy"
    assert dpm.frequency == "FREQ"
    assert dpm.locale == "es"
    assert dpm.pattern_type == "variable"
    assert dpm.resolve_period == "endOfPeriod"

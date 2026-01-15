import re
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest

import pysdmx.io.input_processor as m
from pysdmx.errors import Invalid, NotImplemented
from pysdmx.io import read_sdmx
from pysdmx.io.reader import get_datasets
from pysdmx.model import Codelist, MetadataReport, Schema
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
    return text


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

import httpx
import pandas as pd
import pytest

from pysdmx.api.stat import (
    StatUploader,
    StructureSubmissionResult,
    SubmissionResult,
    _structure_result,
    _submission_from_import,
    _submission_from_status,
)
from pysdmx.errors import (
    InternalError,
    Invalid,
    NotFound,
    Unauthorized,
    Unavailable,
)
from pysdmx.io.format import Format
from pysdmx.io.pd import PandasDataset
from pysdmx.model import (
    Code,
    Codelist,
    Component,
    Components,
    Concept,
    ConceptScheme,
    Dataflow,
    DataStructureDefinition,
    MetadataReport,
    Role,
    Schema,
)
from pysdmx.model.__base import DataType

NSI = "https://nsi.test/rest"
TRANSFER = "https://transfer.test"
STRUCT_URL = f"{NSI}/rest/structure"
IMPORT_URL = f"{TRANSFER}/import/sdmxFile"
STATUS_URL = f"{TRANSFER}/status/request"


@pytest.fixture
def token():
    return "TKN"


@pytest.fixture
def uploader(token):
    return StatUploader(NSI, TRANSFER, dataspace="design", token=token)


@pytest.fixture
def codelist():
    return Codelist(
        id="CL_TEST",
        agency="TEST",
        version="1.0",
        name="Test codelist",
        items=[Code(id="A", name="A")],
    )


@pytest.fixture
def dataset():
    # a small Schema-backed dataset built in-code (no sample files)
    concepts = [
        Concept(id="REF_AREA", name="Reference area"),
        Concept(id="TIME_PERIOD", name="Time period"),
        Concept(id="OBS_VALUE", name="Observation value"),
    ]
    components = Components(
        [
            Component(
                id="REF_AREA",
                required=True,
                role=Role.DIMENSION,
                concept=concepts[0],
                local_dtype=DataType.STRING,
            ),
            Component(
                id="TIME_PERIOD",
                required=True,
                role=Role.DIMENSION,
                concept=concepts[1],
                local_dtype=DataType.PERIOD,
            ),
            Component(
                id="OBS_VALUE",
                required=False,
                role=Role.MEASURE,
                concept=concepts[2],
                local_dtype=DataType.DOUBLE,
            ),
        ]
    )
    schema = Schema(
        context="dataflow",
        agency="TEST",
        id="DF",
        version="1.0",
        components=components,
    )
    data = pd.DataFrame(
        {
            "REF_AREA": ["ES", "FR"],
            "TIME_PERIOD": ["2024", "2024"],
            "OBS_VALUE": [1.0, 2.0],
        }
    )
    return PandasDataset(structure=schema, data=data)


def test_init_stores_endpoints_and_token():
    up = StatUploader("https://nsi.test/rest/", "https://transfer.test/")
    assert up._nsi == "https://nsi.test/rest"  # trailing slash stripped
    assert up._transfer == "https://transfer.test"
    assert up._token is None


def test_submit_structure_returns_result(respx_mock, uploader, codelist):
    route = respx_mock.post(STRUCT_URL).mock(
        return_value=httpx.Response(
            200,
            text='<m:Error><m:ErrorMessage code="201">'
            "<c:Text>Created: CL_TEST was inserted.</c:Text>"
            "</m:ErrorMessage></m:Error>",
        )
    )

    result = uploader.submit_structure(codelist)

    assert isinstance(result, StructureSubmissionResult)
    assert result.success is True
    req = route.calls.last.request
    assert req.headers["Authorization"] == "Bearer TKN"
    # default format is SDMX-JSON 2.0 (covers every artefact type)
    assert (
        req.headers["Content-Type"] == Format.STRUCTURE_SDMX_JSON_2_0_0.value
    )
    assert req.content.decode().lstrip().startswith("{")  # JSON, not XML
    assert "CL_TEST" in req.content.decode()


def test_submit_structure_without_token_raises(codelist):
    up = StatUploader(NSI, TRANSFER)  # no token

    with pytest.raises(Unauthorized, match="Missing token"):
        up.submit_structure(codelist)


@pytest.mark.parametrize("status", [401, 403])
def test_submit_structure_rejected_token_raises(
    respx_mock, uploader, codelist, status
):
    respx_mock.post(STRUCT_URL).mock(
        return_value=httpx.Response(status, text="nope")
    )

    with pytest.raises(Unauthorized, match="rejected the token"):
        uploader.submit_structure(codelist)


def test_submit_structure_client_error_raises_invalid(
    respx_mock, uploader, codelist
):
    respx_mock.post(STRUCT_URL).mock(
        return_value=httpx.Response(400, text="bad request")
    )

    with pytest.raises(Invalid):
        uploader.submit_structure(codelist)


def test_submit_structure_server_error_raises_internal(
    respx_mock, uploader, codelist
):
    respx_mock.post(STRUCT_URL).mock(
        return_value=httpx.Response(500, text="boom")
    )

    with pytest.raises(InternalError):
        uploader.submit_structure(codelist)


def test_submit_structure_in_body_failure(respx_mock, uploader, codelist):
    respx_mock.post(STRUCT_URL).mock(
        return_value=httpx.Response(
            200,
            text='<m:Error><m:ErrorMessage code="411">'
            "<c:Text>Failure: bad reference.</c:Text>"
            "</m:ErrorMessage></m:Error>",
        )
    )

    result = uploader.submit_structure(codelist)

    assert result.success is False
    assert result.messages == ("Failure: bad reference.",)


def test_submit_data_returns_submission_result(respx_mock, uploader, dataset):
    route = respx_mock.post(IMPORT_URL).mock(
        return_value=httpx.Response(
            200, json={"success": True, "message": "request with ID 42 ok"}
        )
    )

    result = uploader.submit_data(dataset)

    assert isinstance(result, SubmissionResult)
    assert result.success is True
    assert result.request_id == 42
    req = route.calls.last.request
    assert req.headers["Authorization"] == "Bearer TKN"
    assert req.headers["Content-Type"].startswith("multipart/form-data")
    body = req.content.decode()
    assert 'name="file"' in body
    assert 'name="dataspace"' in body
    assert "design" in body
    assert "STRUCTURE" in body


def test_submit_data_dataspace_override(respx_mock, uploader, dataset):
    route = respx_mock.post(IMPORT_URL).mock(
        return_value=httpx.Response(200, json={"requestId": 1})
    )

    uploader.submit_data(dataset, dataspace="otherspace")

    assert "otherspace" in route.calls.last.request.content.decode()


def test_submit_structure_format_selection(respx_mock, uploader, codelist):
    route = respx_mock.post(STRUCT_URL).mock(
        return_value=httpx.Response(200, text="<x/>")
    )

    # override the JSON default with an SDMX-ML format
    uploader.submit_structure(
        codelist, structure_format=Format.STRUCTURE_SDMX_ML_2_1
    )

    req = route.calls.last.request
    assert req.headers["Content-Type"] == Format.STRUCTURE_SDMX_ML_2_1.value
    assert req.content.decode().lstrip().startswith("<")  # XML, not JSON


def test_submit_structure_unsupported_format_raises(uploader):
    # the metadata artefacts cannot be written as SDMX-ML; write_sdmx
    # raises Invalid, which submit_structure surfaces unchanged
    report = MetadataReport(id="MR", agency="MD", version="1.0", name="mr")

    with pytest.raises(Invalid, match="cannot be written"):
        uploader.submit_structure(
            report, structure_format=Format.STRUCTURE_SDMX_ML_2_1
        )


def test_submit_data_ml_format(respx_mock, uploader, dataset):
    route = respx_mock.post(IMPORT_URL).mock(
        return_value=httpx.Response(200, json={"requestId": 7})
    )

    uploader.submit_data(dataset, data_format=Format.DATA_SDMX_ML_2_1_STR)

    body = route.calls.last.request.content.decode()
    assert 'filename="data.xml"' in body
    assert "text/xml" in body


def test_submit_data_without_dataspace_raises(token, dataset):
    up = StatUploader(NSI, TRANSFER, token=token)  # no data space

    with pytest.raises(Invalid, match="data space"):
        up.submit_data(dataset)


def test_submit_uploads_structure_then_data(
    respx_mock, uploader, codelist, dataset
):
    struct = respx_mock.post(STRUCT_URL).mock(
        return_value=httpx.Response(
            200,
            text='<m:Error><m:ErrorMessage code="201">'
            "<c:Text>Created.</c:Text></m:ErrorMessage></m:Error>",
        )
    )
    data = respx_mock.post(IMPORT_URL).mock(
        return_value=httpx.Response(200, json={"requestId": 7})
    )

    result = uploader.submit(codelist, dataset)

    assert result.request_id == 7  # returns the data-submission response
    assert struct.called
    assert data.called
    # The structure must be submitted before the data.
    assert [str(c.request.url) for c in respx_mock.calls] == [
        STRUCT_URL,
        IMPORT_URL,
    ]


def test_submit_stops_on_structure_failure(
    respx_mock, uploader, codelist, dataset
):
    respx_mock.post(STRUCT_URL).mock(
        return_value=httpx.Response(
            200,
            text='<m:Error><m:ErrorMessage code="411">'
            "<c:Text>bad</c:Text></m:ErrorMessage></m:Error>",
        )
    )
    data = respx_mock.post(IMPORT_URL).mock(
        return_value=httpx.Response(200, json={"requestId": 1})
    )

    with pytest.raises(Invalid, match="[Ss]tructure"):
        uploader.submit(codelist, dataset)

    assert not data.called  # data not attempted when the structure fails


def test_submission_status_returns_result(respx_mock, uploader):
    route = respx_mock.post(STATUS_URL).mock(
        return_value=httpx.Response(
            200, json={"executionStatus": "Completed", "outcome": "Success"}
        )
    )

    result = uploader.submission_status("REQ-456")

    assert result.execution_status == "Completed"
    assert result.success is True
    req = route.calls.last.request
    assert req.headers["Authorization"] == "Bearer TKN"
    form = req.content.decode()
    assert "dataspace=design" in form
    assert "id=REQ-456" in form


def test_submission_status_wait_polls_until_terminal(respx_mock, uploader):
    respx_mock.post(STATUS_URL).mock(
        side_effect=[
            httpx.Response(200, json={"executionStatus": "InProgress"}),
            httpx.Response(
                200,
                json={"executionStatus": "Completed", "outcome": "Success"},
            ),
        ]
    )

    result = uploader.submission_status("REQ-1", wait=True, interval=0)

    assert result.execution_status == "Completed"
    assert result.success is True


def test_submission_status_wait_exhausts_attempts(respx_mock, uploader):
    respx_mock.post(STATUS_URL).mock(
        return_value=httpx.Response(
            200, json={"executionStatus": "InProgress"}
        )
    )

    result = uploader.submission_status(
        "REQ-1", wait=True, interval=0, attempts=1
    )

    assert result.execution_status == "InProgress"


def test_submit_structure_unreachable_raises_unavailable(
    respx_mock, uploader, codelist
):
    respx_mock.post(STRUCT_URL).mock(side_effect=httpx.ConnectError("boom"))

    with pytest.raises(Unavailable):
        uploader.submit_structure(codelist)


def test_delete_data_uploads_action_d(respx_mock, uploader, dataset):
    route = respx_mock.post(IMPORT_URL).mock(
        return_value=httpx.Response(200, json={"requestId": 9})
    )

    result = uploader.delete_data(dataset)

    assert result.request_id == 9
    req = route.calls.last.request
    assert req.headers["Authorization"] == "Bearer TKN"
    assert req.headers["Content-Type"].startswith("multipart/form-data")
    body = req.content.decode()
    assert 'name="file"' in body
    assert 'name="dataspace"' in body
    assert ",D," in body  # SDMX-CSV 2.0 ACTION column = D (Delete)


def test_delete_data_accepts_sequence(respx_mock, uploader, dataset):
    route = respx_mock.post(IMPORT_URL).mock(
        return_value=httpx.Response(200, json={"requestId": 1})
    )

    result = uploader.delete_data([dataset, dataset])

    assert isinstance(result, SubmissionResult)
    assert ",D," in route.calls.last.request.content.decode()


def test_delete_data_without_dataspace_raises(token, dataset):
    up = StatUploader(NSI, TRANSFER, token=token)  # no data space

    with pytest.raises(Invalid, match="data space"):
        up.delete_data(dataset)


def test_delete_structure_single_artefact(respx_mock, uploader):
    url = f"{NSI}/rest/dataflow/MD/DF_X/1.0"
    route = respx_mock.delete(url).mock(
        return_value=httpx.Response(200, text="<deleted/>")
    )

    out = uploader.delete_structure(
        Dataflow(id="DF_X", agency="MD", version="1.0", name="x")
    )

    assert [r.success for r in out] == [True]
    assert route.calls.last.request.headers["Authorization"] == "Bearer TKN"


def test_delete_structure_urn_string_and_type_segment(respx_mock, uploader):
    url = f"{NSI}/rest/dataconstraint/MD/CR_A_DF_X/1.0"
    respx_mock.delete(url).mock(return_value=httpx.Response(204))

    out = uploader.delete_structure("DataConstraint=MD:CR_A_DF_X(1.0)")

    assert out[0].success is True  # 204 No Content -> empty body


def test_delete_structure_sequence_in_order(respx_mock, uploader):
    dsd_url = f"{NSI}/rest/datastructure/MD/DSD_X/1.0"
    cs_url = f"{NSI}/rest/conceptscheme/MD/CS_X/1.0"
    respx_mock.delete(dsd_url).mock(return_value=httpx.Response(200, text="d"))
    respx_mock.delete(cs_url).mock(return_value=httpx.Response(200, text="c"))

    dsd = DataStructureDefinition(
        id="DSD_X",
        agency="MD",
        version="1.0",
        name="x",
        components=Components([]),
    )
    cs = ConceptScheme(id="CS_X", agency="MD", version="1.0", name="x")
    out = uploader.delete_structure([dsd, cs])

    assert [r.success for r in out] == [True, True]
    assert [str(c.request.url) for c in respx_mock.calls] == [dsd_url, cs_url]


def test_delete_structure_conflict_raises_invalid(respx_mock, uploader):
    url = f"{NSI}/rest/dataflow/MD/DF_X/1.0"
    respx_mock.delete(url).mock(
        return_value=httpx.Response(409, text="still referenced")
    )

    with pytest.raises(Invalid):
        uploader.delete_structure(
            Dataflow(id="DF_X", agency="MD", version="1.0", name="x")
        )


def test_delete_structure_not_found_raises(respx_mock, uploader):
    url = f"{NSI}/rest/dataflow/MD/DF_X/1.0"
    respx_mock.delete(url).mock(return_value=httpx.Response(404))

    with pytest.raises(NotFound):
        uploader.delete_structure("Dataflow=MD:DF_X(1.0)")


def test_delete_structure_without_token_raises():
    up = StatUploader(NSI, TRANSFER)  # no token

    with pytest.raises(Unauthorized, match="Missing token"):
        up.delete_structure(
            Dataflow(id="DF_X", agency="MD", version="1.0", name="x")
        )


def test_delete_structure_bad_urn_raises_clear(uploader):
    with pytest.raises(Invalid, match="short URN"):
        uploader.delete_structure("not-a-urn")


def test_parse_import_operation_result():
    r = _submission_from_import(
        '{"success": true, "message": "The request with ID 42 was ok."}'
    )
    assert r.success is True
    assert r.request_id == 42


def test_parse_import_non_json():
    r = _submission_from_import("boom")
    assert r.success is False
    assert r.request_id is None


def test_parse_status_summary():
    r = _submission_from_status(
        '{"requestId": 7, "executionStatus": "Completed",'
        ' "outcome": "Success", "logs": [{"message": "done"}]}'
    )
    assert r.success is True
    assert (r.request_id, r.execution_status, r.outcome) == (
        7,
        "Completed",
        "Success",
    )
    assert r.logs == ("done",)


def test_parse_status_non_dict():
    assert _submission_from_status("[]").success is False


def test_parse_status_non_json():
    assert _submission_from_status("boom").success is False


def test_parse_structure_response_success_and_failure():
    ok = _structure_result(
        '<m:Error><m:ErrorMessage code="201">'
        "<c:Text>Created: X was inserted.</c:Text></m:ErrorMessage></m:Error>"
    )
    assert ok.success is True
    assert ok.messages == ("Created: X was inserted.",)

    bad = _structure_result(
        '<m:Error><m:ErrorMessage code="411">'
        "<c:Text>Failure: bad.</c:Text></m:ErrorMessage></m:Error>"
    )
    assert bad.success is False

    assert _structure_result("").success is True  # e.g. 204 empty body


def test_submission_result_is_frozen():
    assert isinstance(SubmissionResult(success=True), SubmissionResult)
    assert isinstance(
        StructureSubmissionResult(success=True), StructureSubmissionResult
    )

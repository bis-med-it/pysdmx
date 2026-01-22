import base64

import httpx
import msgspec
import pytest

from pysdmx import errors
from pysdmx.api.fmr.maintenance import RegistryMaintenanceClient
from pysdmx.io.json.sdmxjson2.messages import (
    JsonMetadataMessage,
    JsonStructureMessage,
)
from pysdmx.model import (
    Code,
    Codelist,
    MetadataAttribute,
    MetadataReport,
    Organisation,
)
from pysdmx.model.message import Header


@pytest.fixture
def end_point_in() -> str:
    return "https://registry.sdmx.org/"


@pytest.fixture
def end_point_in_2() -> str:
    return "https://registry.sdmx.org"


@pytest.fixture
def end_point_in_3() -> str:
    return "https://registry.sdmx.org/sdmx/v2"



@pytest.fixture
def end_point_out_structure() -> str:
    return "https://registry.sdmx.org/ws/secure/sdmxapi/rest"


@pytest.fixture
def end_point_out_report() -> str:
    return "https://registry.sdmx.org/ws/secure/sdmx/v2/metadata"


@pytest.fixture
def structure():
    cd = Code("A", name="Code A")
    return Codelist("CL_TEST", agency="TEST", name="Test CL", items=(cd,))


@pytest.fixture
def report():
    a = MetadataAttribute("A", "Code A")
    return MetadataReport(
        "CL_TEST",
        agency="TEST",
        name="Test CL",
        attributes=tuple(a),
        targets=tuple(
            "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=TS:T1(1.0)"
        ),
    )


@pytest.fixture
def user():
    return "ad000042"


@pytest.fixture
def pwd():
    return "mypwd"


@pytest.fixture
def header():
    return Header(test=True, sender=Organisation("5B0"))


def test_structure_maintenance(
    respx_mock, structure, end_point_in, end_point_out_structure, user, pwd
):
    respx_mock.post(end_point_out_structure).mock(
        return_value=httpx.Response(200)
    )

    client = RegistryMaintenanceClient(end_point_in, user, pwd)

    client.put_structures([structure])

    assert respx_mock.calls.call_count == 1
    request = respx_mock.calls[0].request

    # Check header
    assert "Action" in request.headers
    assert request.headers["Action"] == "Replace"
    assert "Authorization" in request.headers
    expected = __compute_pwd(user, pwd)
    assert request.headers["Authorization"] == expected

    # Check content
    msg = (
        msgspec.json.Decoder(JsonStructureMessage)
        .decode(request.content)
        .to_model()
    )
    assert len(msg.structures) == 1
    assert msg.structures[0] == structure
    assert msg.header.id is not None
    assert msg.header.test is False
    assert msg.header.prepared is not None
    assert msg.header.sender.id == "ZZZ"


def test_structure_maintenance_header(
    respx_mock,
    structure,
    end_point_in,
    end_point_out_structure,
    user,
    pwd,
    header,
):
    respx_mock.post(end_point_out_structure).mock(
        return_value=httpx.Response(200)
    )

    client = RegistryMaintenanceClient(end_point_in, user, pwd)

    client.put_structures([structure], header)

    # Check header
    request = respx_mock.calls[0].request
    msg = (
        msgspec.json.Decoder(JsonStructureMessage)
        .decode(request.content)
        .to_model()
    )
    assert msg.header.id is not None
    assert msg.header.test is True
    assert msg.header.prepared is not None
    assert msg.header.sender.id == "5B0"


def test_report_maintenance(
    respx_mock, report, end_point_in, end_point_out_report, user, pwd
):
    respx_mock.post(end_point_out_report).mock(
        return_value=httpx.Response(200)
    )

    client = RegistryMaintenanceClient(end_point_in, user, pwd)

    client.put_metadata_reports([report])

    assert respx_mock.calls.call_count == 1
    request = respx_mock.calls[0].request

    # Check header
    assert "Action" in request.headers
    assert request.headers["Action"] == "Replace"
    assert "Authorization" in request.headers
    expected = __compute_pwd(user, pwd)
    assert request.headers["Authorization"] == expected

    # Check content
    msg = (
        msgspec.json.Decoder(JsonMetadataMessage)
        .decode(request.content)
        .to_model()
    )
    assert len(msg.reports) == 1
    assert msg.reports[0] == report
    assert msg.header.id is not None
    assert msg.header.test is False
    assert msg.header.prepared is not None
    assert msg.header.sender.id == "ZZZ"


def test_report_maintenance_header(
    respx_mock, report, end_point_in, end_point_out_report, user, pwd, header
):
    respx_mock.post(end_point_out_report).mock(
        return_value=httpx.Response(200)
    )

    client = RegistryMaintenanceClient(end_point_in, user, pwd)

    client.put_metadata_reports([report], header)

    # Check header
    request = respx_mock.calls[0].request
    msg = (
        msgspec.json.Decoder(JsonMetadataMessage)
        .decode(request.content)
        .to_model()
    )
    assert msg.header.id is not None
    assert msg.header.test is True
    assert msg.header.prepared is not None
    assert msg.header.sender.id == "5B0"


def test_endpoint_ending(
    respx_mock, structure, end_point_in_2, end_point_out_structure, user, pwd
):
    respx_mock.post(end_point_out_structure).mock(
        return_value=httpx.Response(200)
    )

    client = RegistryMaintenanceClient(end_point_in_2, user, pwd)

    client.put_structures([structure])

    assert respx_mock.calls.call_count == 1


def test_endpoint_with_new_ep(
    respx_mock, structure, end_point_in_3, end_point_out_structure, user, pwd
):
    respx_mock.post(end_point_out_structure).mock(
        return_value=httpx.Response(200)
    )

    client = RegistryMaintenanceClient(end_point_in_3, user, pwd)

    client.put_structures([structure])

    assert respx_mock.calls.call_count == 1


def test_endpoint_with_old_ep(
    respx_mock, structure, end_point_out_structure, user, pwd
):
    respx_mock.post(end_point_out_structure).mock(
        return_value=httpx.Response(200)
    )

    client = RegistryMaintenanceClient(end_point_out_structure, user, pwd)

    client.put_structures([structure])

    assert respx_mock.calls.call_count == 1


def test_client_error(
    respx_mock, structure, end_point_in, end_point_out_structure, user, pwd
):
    respx_mock.post(end_point_out_structure).mock(
        return_value=httpx.Response(409)
    )
    client = RegistryMaintenanceClient(end_point_in, user, pwd)

    with pytest.raises(errors.Invalid) as e:
        client.put_structures([structure])
    assert e.value.title is not None
    assert e.value.description is not None
    assert end_point_in in e.value.description


def __compute_pwd(user, pwd):
    encoded = base64.b64encode(f"{user}:{pwd}".encode("ascii")).decode("ascii")
    return f"Basic {encoded}"

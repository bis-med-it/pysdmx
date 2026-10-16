import msgspec
import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages import (
    JsonDataflowMessage,
    JsonDataflowsMessage,
)
from pysdmx.model import Components, Dataflow, DataStructureDefinition

_DATAFLOW_URN = (
    "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=TEST:FLOW(1.0)"
)


def _dataflow_message(
    *,
    data_constraints=(),
    availability_constraints=(),
) -> bytes:
    return msgspec.json.encode(
        {
            "data": {
                "dataflows": [
                    {
                        "id": "FLOW",
                        "agencyID": "TEST",
                        "name": "Test flow",
                        "version": "1.0",
                    }
                ],
                "dataConstraints": data_constraints,
                "availabilityConstraints": availability_constraints,
            }
        }
    )


def _availability_constraint(
    *,
    dataflow: str = _DATAFLOW_URN,
    series_count: int = 3,
    obs_count: int = 42,
) -> dict[str, object]:
    return {
        "constraintAttachment": {"dataflow": dataflow},
        "seriesCount": series_count,
        "obsCount": obs_count,
    }


def _data_constraint(
    role: str, *, series_count: int = 3, obs_count: int = 42
) -> dict[str, object]:
    return {
        "id": f"{role}_CONSTRAINT",
        "agencyID": "TEST",
        "name": f"{role} constraint",
        "version": "1.0",
        "role": role,
        "constraintAttachment": {"dataflows": [_DATAFLOW_URN]},
        "annotations": [
            {
                "id": "series_count",
                "title": str(series_count),
                "type": "sdmx_metrics",
            },
            {
                "id": "obs_count",
                "title": str(obs_count),
                "type": "sdmx_metrics",
            },
        ],
    }


@pytest.fixture
def body():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/flows/flows.json", "rb"
    ) as f:
        return f.read()


@pytest.fixture
def body_no_match():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/flows/flows_no_match.json",
        "rb",
    ) as f:
        return f.read()


@pytest.fixture
def body_stubs():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/flows/flows_stubs.json",
        "rb",
    ) as f:
        return f.read()


@pytest.fixture
def body_all_stubs():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/flows/flows_all_stubs.json",
        "rb",
    ) as f:
        return f.read()


def test_dataflows_with_references(body):
    res = msgspec.json.Decoder(JsonDataflowsMessage).decode(body)
    flows = res.to_model()

    assert len(flows) == 1
    flow = flows[0]
    assert isinstance(flow, Dataflow)
    assert isinstance(flow.structure, DataStructureDefinition)
    assert flow.components == flow.structure.components
    assert flow.series_count == 42
    assert flow.obs_count == 42000


def test_dataflows_no_dsd_match(body_no_match):
    res = msgspec.json.Decoder(JsonDataflowsMessage).decode(body_no_match)
    flows = res.to_model()

    assert len(flows) == 1
    flow = flows[0]
    assert isinstance(flow, Dataflow)
    assert isinstance(flow.structure, str)


def test_dataflows_stubs(body_stubs):
    res = msgspec.json.Decoder(JsonDataflowsMessage).decode(body_stubs)
    flows = res.to_model()

    assert len(flows) == 1
    flow = flows[0]
    assert isinstance(flow, Dataflow)
    assert flow.structure is None


def test_dataflows_all_stubs(body_all_stubs):
    res = msgspec.json.Decoder(JsonDataflowsMessage).decode(body_all_stubs)
    flows = res.to_model()

    assert len(flows) == 1
    flow = flows[0]
    assert isinstance(flow, Dataflow)
    assert flow.structure is None


def test_dataflows_uses_native_availability_metrics():
    body = _dataflow_message(
        availability_constraints=(_availability_constraint(),)
    )

    message = msgspec.json.Decoder(JsonDataflowsMessage).decode(body)
    flow = message.to_model()[0]

    assert flow.series_count == 3
    assert flow.obs_count == 42


def test_dataflow_info_uses_native_availability_metrics():
    body = _dataflow_message(
        availability_constraints=(_availability_constraint(),)
    )

    message = msgspec.json.Decoder(JsonDataflowMessage).decode(body)
    info = message.to_model(Components(()), None, "TEST", "FLOW", "1.0")

    assert info.series_count == 3
    assert info.obs_count == 42


def test_dataflows_uses_actual_constraint_after_allowed_constraint():
    body = _dataflow_message(
        data_constraints=(
            _data_constraint("Allowed", series_count=99, obs_count=999),
            _data_constraint("Actual"),
        )
    )

    message = msgspec.json.Decoder(JsonDataflowsMessage).decode(body)
    flow = message.to_model()[0]

    assert flow.series_count == 3
    assert flow.obs_count == 42


def test_dataflows_ignores_availability_for_another_dataflow():
    body = _dataflow_message(
        availability_constraints=(
            _availability_constraint(
                dataflow=(
                    "urn:sdmx:org.sdmx.infomodel.datastructure."
                    "Dataflow=TEST:OTHER(1.0)"
                )
            ),
        )
    )

    message = msgspec.json.Decoder(JsonDataflowsMessage).decode(body)
    flow = message.to_model()[0]

    assert flow.series_count is None
    assert flow.obs_count is None


def test_dataflows_rejects_duplicate_availability_constraints():
    body = _dataflow_message(
        availability_constraints=(
            _availability_constraint(),
            _availability_constraint(series_count=4, obs_count=43),
        )
    )

    message = msgspec.json.Decoder(JsonDataflowsMessage).decode(body)

    with pytest.raises(
        errors.Invalid, match="Two availability constraints for the same"
    ):
        message.to_model()

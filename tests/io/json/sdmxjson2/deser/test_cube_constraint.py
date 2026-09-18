import json

import msgspec
import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages import JsonDataConstraintMessage
from pysdmx.model import AvailabilityConstraint, DataConstraint


@pytest.fixture
def body():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/constraints/cube.json", "rb"
    ) as f:
        return f.read()


def test_cube_deser(body):
    res = msgspec.json.Decoder(JsonDataConstraintMessage).decode(body)

    cubes = res.to_model()

    assert len(cubes) == 1
    cube = cubes[0]
    assert isinstance(cube, DataConstraint)
    assert cube.agency == "IAEG-SDGs"
    assert cube.id == "CN_SDG_GLC"
    assert cube.version == "1.22"
    assert cube.name == "IAEG-SDGs:CN_SDG_GLC"
    assert cube.description is None
    assert cube.valid_from is None
    assert cube.valid_to is None
    assert cube.constraint_attachment.data_provider is None
    assert len(cube.constraint_attachment.data_structures) == 0
    assert len(cube.constraint_attachment.dataflows) == 1
    assert cube.constraint_attachment.dataflows[0] == (
        "urn:sdmx:org.sdmx.infomodel.datastructure."
        "Dataflow=IAEG-SDGs:DF_SDG_GLC(1.22)"
    )
    assert len(cube.constraint_attachment.provision_agreements) == 0
    assert len(cube.cube_regions) == 1
    region = cube.cube_regions[0]
    assert region.is_included is True
    assert len(region.key_values) == 1
    for kv in region.key_values:
        assert kv.id == "REPORTING_TYPE"
        assert len(kv.values) == 1
        for v in kv.values:
            assert v.value == "N"
            assert v.valid_from is None
            assert v.valid_to is None


def test_cube_deser_without_attachment(body):
    data = json.loads(body)
    constraint = data["data"]["dataConstraints"][0]
    del constraint["constraintAttachment"]
    modified_body = json.dumps(data).encode()

    res = msgspec.json.Decoder(JsonDataConstraintMessage).decode(modified_body)
    cubes = res.to_model()

    assert len(cubes) == 1
    cube = cubes[0]
    assert isinstance(cube, DataConstraint)
    assert cube.constraint_attachment is None


def test_cube_deser_role_actual(body):
    data = json.loads(body)
    constraint = data["data"]["dataConstraints"][0]
    constraint["role"] = "Actual"
    modified_body = json.dumps(data).encode()

    res = msgspec.json.Decoder(JsonDataConstraintMessage).decode(modified_body)
    cubes = res.to_model()

    assert len(cubes) == 1
    cube = cubes[0]
    assert isinstance(cube, AvailabilityConstraint)
    assert cube.reference == (
        "urn:sdmx:org.sdmx.infomodel.datastructure."
        "Dataflow=IAEG-SDGs:DF_SDG_GLC(1.22)"
    )
    assert len(cube.cube_region.key_values) == 1
    assert cube.cube_region.key_values[0].id == "REPORTING_TYPE"


def test_cube_deser_role_actual_lifts_metric_annotations(body):
    data = json.loads(body)
    constraint = data["data"]["dataConstraints"][0]
    constraint["role"] = "Actual"
    constraint["annotations"] = [
        {"id": "note", "title": "hi", "type": "text"},
        {"id": "series_count", "title": "3", "type": "sdmx_metrics"},
        {"id": "obs_count", "title": "42", "type": "sdmx_metrics"},
    ]
    modified_body = json.dumps(data).encode()

    res = msgspec.json.Decoder(JsonDataConstraintMessage).decode(modified_body)
    cubes = res.to_model()

    assert len(cubes) == 1
    cube = cubes[0]
    assert isinstance(cube, AvailabilityConstraint)
    # The FMR-style sdmx_metrics annotations are lifted into the
    # counts and excluded from the resulting annotations; any other
    # annotation is left untouched.
    assert cube.series_count == 3
    assert cube.obs_count == 42
    assert len(cube.annotations) == 1
    assert cube.annotations[0].id == "note"


def test_cube_deser_role_actual_ignores_non_numeric_metric_title(body):
    data = json.loads(body)
    constraint = data["data"]["dataConstraints"][0]
    constraint["role"] = "Actual"
    constraint["annotations"] = [
        {
            "id": "series_count",
            "title": "not-a-number",
            "type": "sdmx_metrics",
        },
    ]
    modified_body = json.dumps(data).encode()

    res = msgspec.json.Decoder(JsonDataConstraintMessage).decode(modified_body)
    cubes = res.to_model()

    cube = cubes[0]
    assert isinstance(cube, AvailabilityConstraint)
    # A non-numeric title cannot be a genuine count: the annotation is
    # kept as-is instead of being lifted (and no exception is raised).
    assert cube.series_count is None
    assert len(cube.annotations) == 1
    assert cube.annotations[0].id == "series_count"
    assert cube.annotations[0].title == "not-a-number"


def test_cube_deser_role_actual_ignores_unicode_digit_title(body):
    # str.isdigit() returns True for characters such as the
    # superscript two ("²") that int() still cannot parse; the
    # guard must not crash on those either.
    data = json.loads(body)
    constraint = data["data"]["dataConstraints"][0]
    constraint["role"] = "Actual"
    constraint["annotations"] = [
        {"id": "obs_count", "title": "²", "type": "sdmx_metrics"},
    ]
    modified_body = json.dumps(data).encode()

    res = msgspec.json.Decoder(JsonDataConstraintMessage).decode(modified_body)
    cubes = res.to_model()

    cube = cubes[0]
    assert isinstance(cube, AvailabilityConstraint)
    assert cube.obs_count is None
    assert len(cube.annotations) == 1
    assert cube.annotations[0].title == "²"


def test_cube_deser_role_actual_ignores_unknown_metric_id(body):
    data = json.loads(body)
    constraint = data["data"]["dataConstraints"][0]
    constraint["role"] = "Actual"
    constraint["annotations"] = [
        {"id": "foo", "title": "3", "type": "sdmx_metrics"},
    ]
    modified_body = json.dumps(data).encode()

    res = msgspec.json.Decoder(JsonDataConstraintMessage).decode(modified_body)
    cubes = res.to_model()

    cube = cubes[0]
    assert isinstance(cube, AvailabilityConstraint)
    # type=="sdmx_metrics" alone isn't enough: an id other than
    # series_count/obs_count is not a genuine count, so the
    # annotation must be kept as-is instead of being lifted.
    assert cube.series_count is None
    assert cube.obs_count is None
    assert len(cube.annotations) == 1
    assert cube.annotations[0].id == "foo"
    assert cube.annotations[0].type == "sdmx_metrics"


def test_cube_deser_without_role(body):
    data = json.loads(body)
    constraint = data["data"]["dataConstraints"][0]
    del constraint["role"]
    modified_body = json.dumps(data).encode()

    res = msgspec.json.Decoder(JsonDataConstraintMessage).decode(modified_body)
    cubes = res.to_model()

    assert isinstance(cubes[0], DataConstraint)


def test_cube_deser_role_actual_with_key_sets_is_invalid(body):
    data = json.loads(body)
    constraint = data["data"]["dataConstraints"][0]
    constraint["role"] = "Actual"
    constraint["dataKeySets"] = [
        {
            "isIncluded": True,
            "keys": [
                {"keyValues": [{"id": "REPORTING_TYPE", "value": "N"}]},
            ],
        }
    ]
    modified_body = json.dumps(data).encode()

    res = msgspec.json.Decoder(JsonDataConstraintMessage).decode(modified_body)

    with pytest.raises(errors.Invalid, match="key sets"):
        res.to_model()


def test_cube_deser_role_actual_without_attachment_is_invalid(body):
    data = json.loads(body)
    constraint = data["data"]["dataConstraints"][0]
    constraint["role"] = "Actual"
    del constraint["constraintAttachment"]
    modified_body = json.dumps(data).encode()

    res = msgspec.json.Decoder(JsonDataConstraintMessage).decode(modified_body)

    with pytest.raises(errors.Invalid, match="exactly one cube region"):
        res.to_model()

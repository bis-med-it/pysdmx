import msgspec
import pytest

from pysdmx.io.json.sdmxjson2.messages import JsonDataConstraintMessage
from pysdmx.model import DataConstraint


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

import msgspec
import pytest

from pysdmx.errors import Invalid
from pysdmx.io.json.sdmxjson2.messages import JsonStructureMessage
from pysdmx.io.json.sdmxjson2.reader.structure import read
from pysdmx.model.message import StructureMessage


@pytest.fixture
def body():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/reader/structs.json", "rb"
    ) as f:
        return f.read()


def test_structure_reader(body):
    res = msgspec.json.Decoder(JsonStructureMessage).decode(body)
    msg = res.to_model()

    assert isinstance(msg, StructureMessage)

    assert len(msg.get_agency_schemes()) == 5
    assert len(msg.get_categorisations()) == 6
    assert len(msg.get_category_schemes()) == 1
    assert len(msg.get_codelists()) == 83
    assert len(msg.get_concept_schemes()) == 15
    assert len(msg.get_data_provider_schemes()) == 2
    assert len(msg.get_data_structure_definitions()) == 23
    assert len(msg.get_dataflows()) == 12
    assert len(msg.get_hierarchies()) == 1
    assert len(msg.get_provision_agreements()) == 40
    assert len(msg.get_representation_maps()) == 2
    assert len(msg.get_structure_maps()) == 14
    assert len(msg.get_vtl_mapping_schemes()) == 2
    assert len(msg.get_ruleset_schemes()) == 1
    assert len(msg.get_transformation_schemes()) == 1
    assert len(msg.get_value_lists()) == 0
    assert len(msg.get_hierarchy_associations()) == 0
    assert len(msg.get_custom_type_schemes()) == 0
    assert len(msg.get_name_personalisation_schemes()) == 0


def test_get_json2_invalid_structure():
    with pytest.raises(Invalid, match="as SDMX-JSON 2.0.0 structure message."):
        read("pyproject.toml")

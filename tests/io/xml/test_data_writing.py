import pandas as pd
import pytest
from lxml import etree

from pysdmx.errors import Invalid
from pysdmx.io import read_sdmx, write_sdmx
from pysdmx.io.format import Format
from pysdmx.io.pd import PandasDataset
from pysdmx.model import (
    Component,
    Components,
    Concept,
    Organisation,
    Role,
    Schema,
)
from pysdmx.model.dataflow import Group
from pysdmx.model.dataset import ActionType
from pysdmx.model.message import Header

SCHEMAS = "http://www.sdmx.org/resources/sdmxml/schemas"
STRUCTURE_SPECIFIC = {
    Format.DATA_SDMX_ML_2_1_STR: f"{SCHEMAS}/v2_1/data/structurespecific",
    Format.DATA_SDMX_ML_3_0: f"{SCHEMAS}/v3_0/data/structurespecific",
    Format.DATA_SDMX_ML_3_1: f"{SCHEMAS}/v3_1/data/structurespecific",
}
FORMATS = [Format.DATA_SDMX_ML_2_1_GEN, *STRUCTURE_SPECIFIC]
XSI_TYPE = "{http://www.w3.org/2001/XMLSchema-instance}type"
COLUMNS = [
    "DIM1",
    "DIM2",
    "DIM3",
    "SERIES_ATT",
    "GROUP_ATT",
    "OBS_ATT",
    "OBS_VALUE",
]
# Values that Python's repr quotes or escapes, or that XML must escape
VALUES = [
    "Minority shareholders' equity (+/-)",
    'say "hi"',
    'it\'s "both"',
    "b)\xa0post-retirement",
    "C:\\temp",
    "R&D <total>",
    "&quot;",
    "two\nlines",
    "tab\tseparated",
    "carriage\rreturn",
]


def component(id_, role, attachment_level=None):
    return Component(
        id=id_,
        role=role,
        concept=Concept(id=id_),
        required=False,
        attachment_level=attachment_level,
    )


def dataset(context="datastructure", id_="DSD", values=("A",), attribute="A"):
    schema = Schema(
        context=context,
        agency="MD",
        id=id_,
        version="1.0",
        groups=[Group(id="SIBLING", dimensions=["DIM1"])],
        components=Components(
            [
                component("DIM1", Role.DIMENSION),
                component("DIM2", Role.DIMENSION),
                component("DIM3", Role.DIMENSION),
                component("SERIES_ATT", Role.ATTRIBUTE, "DIM1,DIM2"),
                component("GROUP_ATT", Role.ATTRIBUTE, "DIM1"),
                component("OBS_ATT", Role.ATTRIBUTE, "O"),
                component("DS_ATT", Role.ATTRIBUTE, "D"),
                component("OBS_VALUE", Role.MEASURE),
            ]
        ),
    )
    return PandasDataset(
        structure=schema,
        data=pd.DataFrame({column: list(values) for column in COLUMNS}),
        attributes={"DS_ATT": attribute},
        action=ActionType.Replace,
    )


def parse(message):
    return etree.fromstring(message.encode("utf-8"))


@pytest.mark.parametrize("dimension_at_observation", ["AllDimensions", "DIM3"])
@pytest.mark.parametrize("sdmx_format", FORMATS)
def test_values_round_trip(sdmx_format, dimension_at_observation):
    message = write_sdmx(
        [dataset(values=VALUES, attribute="".join(VALUES))],
        sdmx_format,
        dimension_at_observation=dimension_at_observation,
    )

    result = read_sdmx(message, validate=True).data[0]

    rows = sorted(result.data[COLUMNS].itertuples(index=False, name=None))
    assert rows == sorted((value,) * len(COLUMNS) for value in VALUES)
    assert result.attributes == {"DS_ATT": "".join(VALUES)}


@pytest.mark.parametrize(
    ("values", "attribute"), [(["a\x01b"], "A"), (["A"], "a\x01b")]
)
@pytest.mark.parametrize("sdmx_format", FORMATS)
def test_character_not_allowed_in_xml_raises(sdmx_format, values, attribute):
    data = dataset(values=values, attribute=attribute)

    with pytest.raises(Invalid, match="U\\+0001"):
        write_sdmx([data], sdmx_format)


@pytest.mark.parametrize("sdmx_format", FORMATS)
def test_header_values_round_trip(sdmx_format):
    header = Header(
        id="ID",
        sender=Organisation(id="SENDER", name="Banque d'Italie & Co"),
        receiver=[Organisation(id="RECEIVER", name='The "<receiver>"')],
        source="It's a 'source' & more",
    )

    message = write_sdmx([dataset()], sdmx_format, header=header)

    result = read_sdmx(message, validate=True).header
    assert result.sender.name == "Banque d'Italie & Co"
    assert result.receiver[0].name == 'The "<receiver>"'
    assert result.source == "It's a 'source' & more"


@pytest.mark.parametrize("sdmx_format", STRUCTURE_SPECIFIC)
def test_action_is_qualified(sdmx_format):
    message = write_sdmx([dataset()], sdmx_format)

    data_set = parse(message).find("{*}DataSet")
    action = f"{{{STRUCTURE_SPECIFIC[sdmx_format]}}}action"
    assert data_set.get(action) == "Replace"
    assert "action" not in data_set.attrib


@pytest.mark.parametrize(
    ("context", "scope"),
    [
        ("datastructure", "DataStructure"),
        ("dataflow", "Dataflow"),
        ("provisionagreement", "ProvisionAgreement"),
    ],
)
def test_data_scope_is_the_structure_type(context, scope):
    sdmx_format = Format.DATA_SDMX_ML_2_1_STR

    message = write_sdmx([dataset(context)], sdmx_format)

    data_set = parse(message).find("{*}DataSet")
    data_scope = f"{{{STRUCTURE_SPECIFIC[sdmx_format]}}}dataScope"
    assert data_set.get(data_scope) == scope


@pytest.mark.parametrize(
    ("context", "urn"),
    [
        ("datastructure", "datastructure.DataStructure=MD:DSD(1.0)"),
        ("dataflow", "datastructure.Dataflow=MD:DSD(1.0)"),
        ("provisionagreement", "registry.ProvisionAgreement=MD:DSD(1.0)"),
    ],
)
@pytest.mark.parametrize("sdmx_format", STRUCTURE_SPECIFIC)
def test_header_namespace_is_the_data_set_namespace(sdmx_format, context, urn):
    message = write_sdmx(
        [dataset(context)], sdmx_format, dimension_at_observation="DIM3"
    )

    namespace = f"urn:sdmx:org.sdmx.infomodel.{urn}:ObsLevelDim:DIM3"
    structure = parse(message).find("{*}Header/{*}Structure")
    assert structure.get("namespace") == namespace
    assert f'xmlns:ns1="{namespace}"' in message


@pytest.mark.parametrize("sdmx_format", STRUCTURE_SPECIFIC)
def test_group_type_is_in_the_namespace_of_its_data_set(sdmx_format):
    message = write_sdmx(
        [dataset(id_="DSD1"), dataset(id_="DSD2")],
        sdmx_format,
        dimension_at_observation="DIM3",
    )

    groups = parse(message).iter("Group")
    types = [group.get(XSI_TYPE) for group in groups]
    assert types == ["ns1:SIBLING", "ns2:SIBLING"]

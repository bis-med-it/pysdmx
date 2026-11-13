import pandas as pd
import pytest
from lxml import etree

from pysdmx.errors import Invalid
from pysdmx.io import read_sdmx, write_sdmx
from pysdmx.io.format import Format
from pysdmx.io.pd import PandasDataset
from pysdmx.model import Component, Components, Concept, Role, Schema
from pysdmx.model.dataflow import Group

STRUCTURE_SPECIFIC = [
    Format.DATA_SDMX_ML_2_1_STR,
    Format.DATA_SDMX_ML_3_0,
    Format.DATA_SDMX_ML_3_1,
]
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


def dataset(id_="DSD", values=("A",), attribute="A"):
    schema = Schema(
        context="datastructure",
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
    )


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


@pytest.mark.parametrize("sdmx_format", STRUCTURE_SPECIFIC)
def test_group_type_is_in_the_namespace_of_its_data_set(sdmx_format):
    message = write_sdmx(
        [dataset(id_="DSD1"), dataset(id_="DSD2")],
        sdmx_format,
        dimension_at_observation="DIM3",
    )

    groups = etree.fromstring(message.encode("utf-8")).iter("Group")
    types = [group.get(XSI_TYPE) for group in groups]
    assert types == ["ns1:SIBLING", "ns2:SIBLING"]

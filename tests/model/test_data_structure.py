import pytest

from pysdmx.model import (
    Agency,
    Component,
    Components,
    Concept,
    DataStructureDefinition,
    DataType,
    Role,
)


@pytest.mark.parametrize("agency", ["BIS", Agency("BIS")])
def test_short_urn(agency):
    dsd = DataStructureDefinition(
        "BIS_CBS",
        agency=agency,
        version="1.0",
        components=Components(
            [
                Component(
                    "DIM",
                    True,
                    Role.DIMENSION,
                    Concept("DIM"),
                    DataType.STRING,
                )
            ]
        ),
    )

    assert dsd.short_urn == "DataStructure=BIS:BIS_CBS(1.0)"

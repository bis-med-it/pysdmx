from pysdmx.api.qb.structure import StructureReference, StructureType


def test_expected_references():
    artefacts_types = [
        a.value for a in StructureType if a != StructureType.ALL
    ]
    expected = [
        "none",
        "parents",
        "parentsandsiblings",
        "ancestors",
        "children",
        "descendants",
        "all",
    ]
    expected.extend(artefacts_types)

    assert len(StructureReference) == len(expected)
    for ref in StructureReference:
        assert ref.value in expected

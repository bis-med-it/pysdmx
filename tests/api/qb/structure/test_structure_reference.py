from pysdmx.api.qb.structure import StructureReference


def test_expected_references():
    expected = [
        "none",
        "parents",
        "parentsandsiblings",
        "ancestors",
        "children",
        "descendants",
        "all",
    ]

    assert len(StructureReference) == len(expected)
    for ref in StructureReference:
        assert ref.value in expected

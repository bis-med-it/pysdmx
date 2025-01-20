from pysdmx.api.qb.structure import StructureDetail


def test_expected_details():
    expected = [
        "full",
        "allstubs",
        "referencestubs",
        "allcompletestubs",
        "referencecompletestubs",
        "referencepartial",
        "raw",
    ]

    assert len(StructureDetail) == len(expected)
    for d in StructureDetail:
        assert d.value in expected

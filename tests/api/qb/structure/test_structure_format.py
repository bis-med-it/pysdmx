from pysdmx.api.qb.structure import StructureFormat


def test_expected_formats():
    expected = [
        "application/vnd.sdmx.structure+xml;version=2.1",
        "application/vnd.sdmx.structure+xml;version=3.0.0",
        "application/vnd.sdmx.structure+json;version=1.0.0",
        "application/vnd.sdmx.structure+json;version=2.0.0",
    ]

    assert len(StructureFormat) == len(expected)
    for fmt in StructureFormat:
        assert fmt.value in expected

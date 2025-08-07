from pysdmx.api.qb.schema import SchemaFormat


def test_expected_formats():
    expected = [
        "application/vnd.sdmx.schema+json;version=1.0.0",
        "application/vnd.sdmx.schema+xml;version=2.1",
        "application/vnd.sdmx.schema+json;version=2.0.0",
        "application/vnd.sdmx.schema+xml;version=3.0.0",
        "application/vnd.sdmx.structure+xml;version=2.1",
        "application/vnd.sdmx.structure+json;version=1.0.0",
        "application/vnd.sdmx.structure+xml;version=3.0.0",
        "application/vnd.sdmx.structure+xml;version=3.1.0",
        "application/vnd.sdmx.structure+json;version=2.0.0",
        "application/vnd.fusion.json",
    ]

    assert len(SchemaFormat) == len(expected)
    for fmt in SchemaFormat:
        assert fmt.value in expected

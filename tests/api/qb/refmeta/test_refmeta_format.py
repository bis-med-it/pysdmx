from pysdmx.api.qb.refmeta import RefMetaFormat


def test_expected_formats():
    expected = [
        "application/vnd.sdmx.metadata+xml;version=3.0.0",
        "application/vnd.sdmx.metadata+xml;version=3.1.0",
        "application/vnd.sdmx.metadata+json;version=2.0.0",
        "application/vnd.sdmx.metadata+csv;version=2.0.0",
        "application/vnd.sdmx.metadata+csv;version=2.1.0",
        "application/vnd.fusion.json",
    ]

    assert len(RefMetaFormat) == len(expected)
    for fmt in RefMetaFormat:
        assert fmt.value in expected

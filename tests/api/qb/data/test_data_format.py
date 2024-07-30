from pysdmx.api.qb.data import DataFormat


def test_expected_formats():
    expected = [
        "application/vnd.sdmx.genericdata+xml;version=2.1",
        "application/vnd.sdmx.structurespecificdata+xml;version=2.1",
        "application/vnd.sdmx.generictimeseriesdata+xml;version=2.1",
        "application/vnd.sdmx.structurespecifictimeseriesdata+xml;version=2.1",
        "application/vnd.sdmx.data+json;version=1.0.0",
        "application/vnd.sdmx.data+csv;version=1.0.0",
        "application/vnd.sdmx.data+json;version=2.0.0",
        "application/vnd.sdmx.data+xml;version=3.0.0",
        "application/vnd.sdmx.data+csv;version=2.0.0",
    ]

    assert len(DataFormat) == len(expected)
    for fmt in DataFormat:
        assert fmt.value in expected

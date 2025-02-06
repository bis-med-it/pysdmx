from pysdmx.api.qb.registration import RegistryFormat


def test_expected_formats():
    expected = [
        "application/vnd.sdmx.registry+xml;version=2.1",
        "application/vnd.sdmx.registry+xml;version=3.0",
        "application/vnd.fusion.json",
    ]

    assert len(RegistryFormat) == len(expected)
    for fmt in RegistryFormat:
        assert fmt.value in expected

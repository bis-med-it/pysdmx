from pysdmx.api.qb.util import _ApiVersion, ApiVersion


def test_api_version():
    version = "V1.0.0"
    number = 0
    v = _ApiVersion(version, number)

    assert v.label == version
    assert v.number == number


def test_api_enum():
    expected = [
        "V1.0.0",
        "V1.0.1",
        "V1.0.2",
        "V1.1.0",
        "V1.2.0",
        "V1.3.0",
        "V1.4.0",
        "V1.5.0",
        "V2.0.0",
        "V2.1.0",
    ]

    assert len(ApiVersion) == 10
    prev = None
    for v in ApiVersion:
        assert v.value.label in expected
        if prev is not None:
            v.value.number > prev.value.number
        prev = v

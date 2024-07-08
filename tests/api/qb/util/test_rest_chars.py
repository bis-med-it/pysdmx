from pysdmx.api.qb.util import REST_ALL, REST_LATEST


def test_rest_all():
    assert REST_ALL == "*"


def test_rest_latest():
    assert REST_LATEST == "~"

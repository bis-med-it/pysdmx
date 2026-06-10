from pysdmx.api.stat import StatUploader


def test_init_stores_endpoints_and_token():
    up = StatUploader("https://nsi.test/rest/", "https://transfer.test/")
    assert up._nsi == "https://nsi.test/rest"  # trailing slash stripped
    assert up._transfer == "https://transfer.test"
    assert up._token is None

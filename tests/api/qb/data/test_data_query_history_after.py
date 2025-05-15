import pytest

from pysdmx.api.qb.data import DataQuery
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.fixture
def res():
    return "CBS"


@pytest.fixture
def history():
    return True


@pytest.mark.parametrize("api_version", ApiVersion)
def test_invalid_value(res: str, api_version: ApiVersion):
    q = DataQuery(resource_id=res, include_history=42)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_history_before_2_0_0(
    res: str,
    history: bool,
    api_version: ApiVersion,
):
    expected = (
        f"/data/all,{res},latest/all"
        f"?detail=full&includeHistory={str(history).lower()}"
    )

    q = DataQuery(resource_id=res, include_history=history)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (
        v
        for v in ApiVersion
        if v >= ApiVersion.V2_0_0 and v < ApiVersion.V2_2_0
    ),
)
def test_url_history_since_2_0_0(
    history: bool,
    api_version: ApiVersion,
):
    expected = (
        f"/data/*/*/*/*/*"
        f"?attributes=dsd&measures=all&includeHistory={str(history).lower()}"
    )

    q = DataQuery(include_history=history)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_url_history_since_2_2_0(
    history: bool,
    api_version: ApiVersion,
):
    expected = (
        f"/data/*/*/*/*/*"
        f"?attributes=dsd&measures=all&includeHistory={str(history).lower()}"
        "&offset=0"
    )

    q = DataQuery(include_history=history)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_history_before_2_0_0_short(
    res: str,
    history: bool,
    api_version: ApiVersion,
):
    expected = f"/data/{res}?includeHistory={str(history).lower()}"

    q = DataQuery(resource_id=res, include_history=history)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_history_since_2_0_0_short(
    history: bool,
    api_version: ApiVersion,
):
    expected = f"/data?includeHistory={str(history).lower()}"

    q = DataQuery(include_history=history)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_default_history_before_2_0_0_short(
    res: str,
    api_version: ApiVersion,
):
    expected = f"/data/{res}"

    q = DataQuery(resource_id=res)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_default_history_since_2_0_0_short(
    api_version: ApiVersion,
):
    expected = "/data"

    q = DataQuery()
    url = q.get_url(api_version, True)

    assert url == expected

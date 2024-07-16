import pytest

from pysdmx.api.qb.data import DataQuery
from pysdmx.api.qb.util import ApiVersion


@pytest.fixture()
def res():
    return "CBS"


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("measure", ["all", "OBS_VALUE"])
def test_full(res: str, measure: str, api_version: ApiVersion):
    expected = f"/data/all,{res},latest/all?detail=full&includeHistory=false"

    q = DataQuery(resource_id=res, attributes="dsd", measures=measure)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("measure", ["all", "OBS_VALUE"])
def test_dataonly(res: str, measure: str, api_version: ApiVersion):
    expected = (
        f"/data/all,{res},latest/all?detail=dataonly&includeHistory=false"
    )

    q = DataQuery(resource_id=res, attributes="none", measures=measure)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_serieskeysonly(res: str, api_version: ApiVersion):
    expected = (
        f"/data/all,{res},latest/all?"
        "detail=serieskeysonly&includeHistory=false"
    )

    q = DataQuery(resource_id=res, attributes="series", measures="none")
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_nodata(res: str, api_version: ApiVersion):
    expected = f"/data/all,{res},latest/all?detail=nodata&includeHistory=false"

    q = DataQuery(resource_id=res, attributes="dsd", measures="none")
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("measure", ["all", "OBS_VALUE"])
def test_full_short(res: str, measure: str, api_version: ApiVersion):
    expected = f"/data/{res}"

    q = DataQuery(resource_id=res, attributes="dsd", measures=measure)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("measure", ["all", "OBS_VALUE"])
def test_dataonly_short(res: str, measure: str, api_version: ApiVersion):
    expected = f"/data/{res}?detail=dataonly"

    q = DataQuery(resource_id=res, attributes="none", measures=measure)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_serieskeysonly_short(res: str, api_version: ApiVersion):
    expected = f"/data/{res}?detail=serieskeysonly"

    q = DataQuery(resource_id=res, attributes="series", measures="none")
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_nodata_short(res: str, api_version: ApiVersion):
    expected = f"/data/{res}?detail=nodata"

    q = DataQuery(resource_id=res, attributes="dsd", measures="none")
    url = q.get_url(api_version, True)

    assert url == expected

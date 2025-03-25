from typing import List

import pytest

from pysdmx.api.qb.data import DataQuery
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.fixture
def res():
    return "CBS"


@pytest.fixture
def mult_meas():
    return ["OI", "TO"]


measures = ["all", "none", "OBS_VALUE"]


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_invalid_value(res: str, api_version: ApiVersion):
    q = DataQuery(resource_id=res, measures=42)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version",
    (
        v
        for v in ApiVersion
        if v >= ApiVersion.V2_0_0 and v < ApiVersion.V2_2_0
    ),
)
@pytest.mark.parametrize("measure", measures)
def test_url_measure(
    measure: str,
    api_version: ApiVersion,
):
    expected = (
        f"/data/*/*/*/*/*?attributes=dsd&measures={measure}"
        "&includeHistory=false"
    )
    q = DataQuery(measures=measure)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
@pytest.mark.parametrize("measure", measures)
def test_url_measure_since_2_2_0(
    measure: str,
    api_version: ApiVersion,
):
    expected = (
        f"/data/*/*/*/*/*?attributes=dsd&measures={measure}"
        "&includeHistory=false&offset=0"
    )
    q = DataQuery(measures=measure)
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
def test_url_multi_measures(
    mult_meas: List[str],
    api_version: ApiVersion,
):
    expected = (
        f"/data/*/*/*/*/*?attributes=dsd&measures={','.join(mult_meas)}"
        "&includeHistory=false"
    )
    q = DataQuery(measures=mult_meas)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_url_multi_measures(
    mult_meas: List[str],
    api_version: ApiVersion,
):
    expected = (
        f"/data/*/*/*/*/*?attributes=dsd&measures={','.join(mult_meas)}"
        "&includeHistory=false&offset=0"
    )
    q = DataQuery(measures=mult_meas)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("measure", (m for m in measures if m != "all"))
def test_url_measure_short(
    measure: str,
    api_version: ApiVersion,
):
    expected = f"/data?measures={measure}"

    q = DataQuery(measures=measure)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_multi_measures_short(
    mult_meas: List[str],
    api_version: ApiVersion,
):
    expected = f"/data?measures={','.join(mult_meas)}"
    q = DataQuery(measures=mult_meas)
    url = q.get_url(api_version, True)

    assert url == expected

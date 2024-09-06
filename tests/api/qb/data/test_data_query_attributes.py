from typing import List

import pytest

from pysdmx.api.qb.data import DataQuery
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.fixture()
def res():
    return "CBS"


@pytest.fixture()
def mult_attrs():
    return ["CONF_STATUS", "OBS_STATUS"]


attributes = [
    "dsd",
    "msd",
    "dataset",
    "series",
    "obs",
    "all",
    "none",
    "OBS_STATUS",
]


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_invalid_value(res: str, api_version: ApiVersion):
    q = DataQuery(resource_id=res, attributes=42)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("attr", attributes)
def test_url_attr(
    attr: str,
    api_version: ApiVersion,
):
    expected = (
        f"/data/*/*/*/*/*?attributes={attr}&measures=all"
        "&includeHistory=false"
    )
    q = DataQuery(attributes=attr)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_multi_attributes(
    mult_attrs: List[str],
    api_version: ApiVersion,
):
    expected = (
        f"/data/*/*/*/*/*?attributes={','.join(mult_attrs)}&measures=all"
        "&includeHistory=false"
    )
    q = DataQuery(attributes=mult_attrs)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("attr", (m for m in attributes if m != "dsd"))
def test_url_attr_short(
    attr: str,
    api_version: ApiVersion,
):
    expected = f"/data?attributes={attr}"

    q = DataQuery(attributes=attr)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_multi_attributes_short(
    mult_attrs: List[str],
    api_version: ApiVersion,
):
    expected = f"/data?attributes={','.join(mult_attrs)}"
    q = DataQuery(attributes=mult_attrs)
    url = q.get_url(api_version, True)

    assert url == expected

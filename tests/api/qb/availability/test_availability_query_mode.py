import pytest

from pysdmx.api.qb.availability import AvailabilityMode, AvailabilityQuery
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.fixture()
def res():
    return "CBS"


@pytest.fixture()
def mode():
    return AvailabilityMode.AVAILABLE


@pytest.mark.parametrize(
    "api_version",
    (
        v
        for v in ApiVersion
        if v >= ApiVersion.V1_3_0 and v < ApiVersion.V2_0_0
    ),
)
def test_invalid_value(res: str, api_version: ApiVersion):
    q = AvailabilityQuery(resource_id=res, mode=42)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version",
    (
        v
        for v in ApiVersion
        if v >= ApiVersion.V1_3_0 and v < ApiVersion.V2_0_0
    ),
)
def test_url_mode_before_2_0_0(
    res: str,
    mode: AvailabilityMode,
    api_version: ApiVersion,
):
    expected = (
        f"/availableconstraint/all,{res},latest/all/all"
        f"?references=none&mode={mode.value}"
    )

    q = AvailabilityQuery(resource_id=res, mode=mode)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_mode_since_2_0_0(
    mode: AvailabilityMode,
    api_version: ApiVersion,
):
    expected = f"/availability/*/*/*/*/*/*?references=none&mode={mode.value}"

    q = AvailabilityQuery(mode=mode)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (
        v
        for v in ApiVersion
        if v >= ApiVersion.V1_3_0 and v < ApiVersion.V2_0_0
    ),
)
def test_url_mode_before_2_0_0_short(
    res: str,
    mode: AvailabilityMode,
    api_version: ApiVersion,
):
    expected = f"/availableconstraint/{res}?mode={mode.value}"

    q = AvailabilityQuery(resource_id=res, mode=mode)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_mode_since_2_0_0_short(
    mode: AvailabilityMode, api_version: ApiVersion
):
    expected = f"/availability?mode={mode.value}"

    q = AvailabilityQuery(mode=mode)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (
        v
        for v in ApiVersion
        if v >= ApiVersion.V1_3_0 and v < ApiVersion.V2_0_0
    ),
)
def test_url_default_mode_before_2_0_0_short(
    res: str,
    api_version: ApiVersion,
):
    mode = AvailabilityMode.EXACT
    expected = f"/availableconstraint/{res}"

    q = AvailabilityQuery(resource_id=res, mode=mode)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_default_mode_since_2_0_0_short(api_version: ApiVersion):
    mode = AvailabilityMode.EXACT
    expected = "/availability"

    q = AvailabilityQuery(mode=mode)
    url = q.get_url(api_version, True)

    assert url == expected

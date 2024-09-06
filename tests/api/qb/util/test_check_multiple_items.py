import pytest

from pysdmx.api.qb.util import ApiVersion, check_multiple_items
from pysdmx.errors import Invalid


@pytest.mark.parametrize(
    "api_version", [v for v in ApiVersion if v < ApiVersion.V1_3_0]
)
def test_check_multiple_items_before_1_3_0(api_version):
    with pytest.raises(Invalid):
        check_multiple_items(["A", "B"], api_version)


@pytest.mark.parametrize(
    "api_version", [v for v in ApiVersion if v >= ApiVersion.V1_3_0]
)
def test_check_multiple_items_since_1_3_0(api_version):
    try:
        check_multiple_items(["A", "B"], api_version)
    except Invalid:
        pytest.raises("A Invalid error was received but none was expected.")

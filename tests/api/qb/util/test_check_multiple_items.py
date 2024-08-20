import pytest

from pysdmx.api.qb.util import ApiVersion, check_multiple_items
from pysdmx.errors import Invalid


def test_multiple_items():
    for v in ApiVersion:
        if v.value.number < ApiVersion.V1_3_0.value.number:
            with pytest.raises(Invalid):
                check_multiple_items(["A", "B"], v)

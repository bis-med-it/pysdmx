import pytest

from pysdmx.api.qb.util import ApiVersion, check_multiple_items
from pysdmx.errors import ClientError


def test_check_multiple_items():
    for v in ApiVersion:
        if v < ApiVersion.V1_3_0:
            with pytest.raises(ClientError):
                check_multiple_items(["A", "B"], v)
        else:
            try:
                check_multiple_items(["A", "B"], v)
            except ClientError:
                pytest.raises(
                    "A ClientError was received but none was expected."
                )

import pytest

from pysdmx.api.qb.registration import RegistrationByProviderQuery
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_1_0)
)
def test_registration_query_by_prv_before_2_1_0(api_version: ApiVersion):
    q = RegistrationByProviderQuery()

    with pytest.raises(Invalid):
        q.get_url(api_version)

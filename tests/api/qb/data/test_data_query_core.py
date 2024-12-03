import pytest

from pysdmx.api.qb.data import DataContext, DataQuery
from pysdmx.api.qb.util import REST_ALL, ApiVersion
from pysdmx.errors import Invalid


@pytest.fixture
def agency():
    return "BIS"


@pytest.fixture
def res():
    return "CBS"


@pytest.fixture
def version():
    return "1.0"


def test_expected_defaults():
    q = DataQuery()

    assert q.context == DataContext.ALL
    assert q.agency_id == REST_ALL
    assert q.resource_id == REST_ALL
    assert q.version == REST_ALL
    assert q.key == REST_ALL
    assert q.components is None
    assert q.updated_after is None
    assert q.first_n_obs is None
    assert q.last_n_obs is None
    assert q.obs_dimension is None
    assert q.attributes == "dsd"
    assert q.measures == "all"
    assert q.include_history is False


def test_validate_ok():
    q = DataQuery()

    q.validate()

    assert q.context == DataContext.ALL
    assert q.agency_id == REST_ALL
    assert q.resource_id == REST_ALL
    assert q.version == REST_ALL
    assert q.key == REST_ALL
    assert q.components is None
    assert q.updated_after is None
    assert q.first_n_obs is None
    assert q.last_n_obs is None
    assert q.obs_dimension is None
    assert q.attributes == "dsd"
    assert q.measures == "all"
    assert q.include_history is False


def test_validate_nok():
    q = DataQuery("wrong_context")

    with pytest.raises(Invalid):
        q.validate()


def test_rest_url_for_data_query():
    q = DataQuery()

    url = q.get_url(ApiVersion.V2_0_0)

    assert "/data" in url

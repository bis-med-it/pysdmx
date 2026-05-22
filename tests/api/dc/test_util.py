import pytest

from pysdmx.api.dc.query import Operator, TextFilter
from pysdmx.api.dc.util import prepare_basic_data_query
from pysdmx.api.qb import DataContext, DataQuery
from pysdmx.model import Dataflow, DataflowRef


@pytest.fixture
def df():
    return Dataflow(
        agency="BIS",
        id="CBS",
        version="1.0",
        name="Consolidated Banking Statistics",
        structure="urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=BIS:BIS_CBS(1.0)",
    )


@pytest.fixture
def dfref():
    return DataflowRef("BIS", "CBS", "1.0")


@pytest.fixture
def dfurn():
    return "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:CBS(1.0)"


@pytest.fixture
def filter():
    return TextFilter("L_REP_CTY", Operator.EQUALS, "CH")


@pytest.fixture
def sql_filter():
    return "L_REP_CTY = 'CH'"


@pytest.fixture
def py_filter():
    return "L_REP_CTY == 'CH'"


def test_basic_query_df(df):
    q = prepare_basic_data_query(df)

    __check_query(q)


def test_basic_query_dfref(dfref):
    q = prepare_basic_data_query(dfref)

    __check_query(q)


def test_basic_query_dfurn(dfurn):
    q = prepare_basic_data_query(dfurn)

    __check_query(q)


def test_filtered_query(dfurn, filter):
    q = prepare_basic_data_query(dfurn, filter)

    __check_filtered_query(q, filter)


def test_filtered_sql_query(dfurn, filter, sql_filter):
    q = prepare_basic_data_query(dfurn, sql_filter)

    __check_filtered_query(q, filter)


def test_filtered_py_query(dfurn, filter, py_filter):
    q = prepare_basic_data_query(dfurn, py_filter)

    __check_filtered_query(q, filter)


def __check_query(q: DataQuery):
    assert q.context == DataContext.DATAFLOW
    assert q.agency_id == "BIS"
    assert q.resource_id == "CBS"
    assert q.version == "1.0"
    assert q.key == "*"
    assert q.components is None
    assert q.updated_after is None
    assert q.first_n_obs is None
    assert q.last_n_obs is None
    assert q.obs_dimension == "AllDimensions"
    assert q.attributes == "dsd"
    assert q.measures == "all"
    assert q.include_history is False
    assert q.offset == 0
    assert q.limit is None
    assert q.sort == []
    assert q.as_of is None
    assert q.reporting_year_start_day is None


def __check_filtered_query(q: DataQuery, expected_filter: TextFilter):
    assert q.context == DataContext.DATAFLOW
    assert q.agency_id == "BIS"
    assert q.resource_id == "CBS"
    assert q.version == "1.0"
    assert q.key == "*"
    assert q.components == expected_filter
    assert q.updated_after is None
    assert q.first_n_obs is None
    assert q.last_n_obs is None
    assert q.obs_dimension == "AllDimensions"
    assert q.attributes == "dsd"
    assert q.measures == "all"
    assert q.include_history is False
    assert q.offset == 0
    assert q.limit is None
    assert q.sort == []
    assert q.as_of is None
    assert q.reporting_year_start_day is None

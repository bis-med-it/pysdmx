from pysdmx.model import DataType


def test_dtype_alpha():
    t = DataType.ALPHA

    assert t == "Alpha"


def test_dtype_alphanum():
    t = DataType.ALPHA_NUM

    assert t == "AlphaNumeric"


def test_dtype_basic_time_period():
    t = DataType.BASIC_TIME_PERIOD

    assert t == "BasicTimePeriod"


def test_dtype_bigint():
    t = DataType.BIG_INTEGER

    assert t == "BigInteger"


def test_dtype_bool():
    t = DataType.BOOLEAN

    assert t == "Boolean"


def test_dtype_count():
    t = DataType.COUNT

    assert t == "Count"


def test_dtype_data_set_reference():
    t = DataType.DATA_SET_REFERENCE

    assert t == "DataSetReference"


def test_dtype_date():
    t = DataType.DATE

    assert t == "GregorianDay"


def test_dtype_datetime():
    t = DataType.DATE_TIME

    assert t == "DateTime"


def test_dtype_day():
    t = DataType.DAY

    assert t == "Day"


def test_dtype_decimal():
    t = DataType.DECIMAL

    assert t == "Decimal"


def test_dtype_double():
    t = DataType.DOUBLE

    assert t == "Double"


def test_dtype_duration():
    t = DataType.DURATION

    assert t == "Duration"


def test_dtype_exclusive_value_range():
    t = DataType.EXCLUSIVE_VALUE_RANGE

    assert t == "ExclusiveValueRange"


def test_dtype_float():
    t = DataType.FLOAT

    assert t == "Float"


def test_dtype_geospatial_information():
    t = DataType.GEOSPATIAL_INFORMATION

    assert t == "GeospatialInformation"


def test_dtype_gregorian_time_period():
    t = DataType.GREGORIAN_TIME_PERIOD

    assert t == "GregorianTimePeriod"


def test_dtype_identifiable_reference():
    t = DataType.IDENTIFIABLE_REFERENCE

    assert t == "IdentifiableReference"


def test_dtype_inclusive_value_range():
    t = DataType.INCLUSIVE_VALUE_RANGE

    assert t == "InclusiveValueRange"


def test_dtype_incremental():
    t = DataType.INCREMENTAL

    assert t == "Incremental"


def test_dtype_int():
    t = DataType.INTEGER

    assert t == "Integer"


def test_dtype_key_values():
    t = DataType.KEY_VALUES

    assert t == "KeyValues"


def test_dtype_long():
    t = DataType.LONG

    assert t == "Long"


def test_dtype_month():
    t = DataType.MONTH

    assert t == "Month"


def test_dtype_month_day():
    t = DataType.MONTH_DAY

    assert t == "MonthDay"


def test_dtype_numeric():
    t = DataType.NUMERIC

    assert t == "Numeric"


def test_dtype_period():
    t = DataType.PERIOD

    assert t == "ObservationalTimePeriod"


def test_dtype_rep_day():
    t = DataType.REP_DAY

    assert t == "ReportingDay"


def test_dtype_rep_month():
    t = DataType.REP_MONTH

    assert t == "ReportingMonth"


def test_dtype_rep_quarter():
    t = DataType.REP_QUARTER

    assert t == "ReportingQuarter"


def test_dtype_rep_semester():
    t = DataType.REP_SEMESTER

    assert t == "ReportingSemester"


def test_dtype_rep_trimester():
    t = DataType.REP_TRIMESTER

    assert t == "ReportingTrimester"


def test_dtype_rep_week():
    t = DataType.REP_WEEK

    assert t == "ReportingWeek"


def test_dtype_rep_year():
    t = DataType.REP_YEAR

    assert t == "ReportingYear"


def test_dtype_short():
    t = DataType.SHORT

    assert t == "Short"


def test_dtype_std_time_period():
    t = DataType.STD_TIME_PERIOD

    assert t == "StandardTimePeriod"


def test_dtype_str():
    t = DataType.STRING

    assert t == "String"


def test_time():
    t = DataType.TIME

    assert t == "Time"


def test_dtype_times_range():
    t = DataType.TIMES_RANGE

    assert t == "TimesRange"


def test_dtype_uri():
    t = DataType.URI

    assert t == "URI"


def test_dtype_xhtml():
    t = DataType.XHTML

    assert t == "XHTML"


def test_dtype_year():
    t = DataType.YEAR

    assert t == "GregorianYear"


def test_dtype_year_month():
    t = DataType.YEAR_MONTH

    assert t == "GregorianYearMonth"

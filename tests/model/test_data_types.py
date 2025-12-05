from pysdmx.model import DataType


def test_dtype_alpha():
    t = DataType.ALPHA

    assert t == "Alpha"


def test_dtype_alphanum():
    t = DataType.ALPHA_NUM

    assert t == "AlphaNumeric"


def test_dtype_bigint():
    t = DataType.BIG_INTEGER

    assert t == "BigInteger"


def test_dtype_bool():
    t = DataType.BOOLEAN

    assert t == "Boolean"


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


def test_dtype_float():
    t = DataType.FLOAT

    assert t == "Float"


def test_dtype_incremental():
    t = DataType.INCREMENTAL

    assert t == "Incremental"


def test_dtype_int():
    t = DataType.INTEGER

    assert t == "Integer"


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


def test_dtype_short():
    t = DataType.SHORT

    assert t == "Short"


def test_dtype_str():
    t = DataType.STRING

    assert t == "String"


def test_time():
    t = DataType.TIME

    assert t == "Time"


def test_dtype_uri():
    t = DataType.URI

    assert t == "URI"


def test_dtype_year():
    t = DataType.YEAR

    assert t == "GregorianYear"


def test_dtype_year_month():
    t = DataType.YEAR_MONTH

    assert t == "GregorianYearMonth"

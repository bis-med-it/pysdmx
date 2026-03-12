from pysdmx.toolkit.sqlsrv import get_select_columns


def test_no_columns():
    select = get_select_columns([])

    assert select == "*"


def test_one_column():
    select = get_select_columns(["OBS_VALUE"])

    assert select == '"OBS_VALUE"'


def test_multiple_columns():
    select = get_select_columns(["SKEY", "TIME_PERIOD", "OBS_VALUE"])

    assert select == '"SKEY", "TIME_PERIOD", "OBS_VALUE"'

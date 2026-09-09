from datetime import datetime, timedelta, timezone

from pysdmx.util import to_utc


def test_none_is_returned_as_is():
    assert to_utc(None) is None


def test_naive_datetime_is_assumed_utc():
    naive = datetime(2000, 1, 1, 10, 42, 21)

    out = to_utc(naive)

    assert out == datetime(2000, 1, 1, 10, 42, 21, tzinfo=timezone.utc)
    assert out.tzinfo == timezone.utc


def test_aware_datetime_is_converted_to_utc():
    cet = timezone(timedelta(hours=1))
    aware = datetime(2000, 1, 1, 10, 42, 21, tzinfo=cet)

    out = to_utc(aware)

    assert out == aware
    assert out.tzinfo == timezone.utc
    assert out.hour == 9


def test_utc_datetime_is_returned_unchanged():
    utc = datetime(2000, 1, 1, 10, 42, 21, tzinfo=timezone.utc)

    assert to_utc(utc) == utc

from datetime import datetime, timedelta, timezone, tzinfo

from pysdmx.util import ensure_tz_aware


class _NoOffset(tzinfo):
    """A tzinfo that does not provide a UTC offset."""

    def utcoffset(self, dt):
        return None


def test_none_is_returned_as_is():
    assert ensure_tz_aware(None) is None


def test_naive_datetime_is_assumed_utc():
    naive = datetime(2000, 1, 1, 10, 42, 21)

    out = ensure_tz_aware(naive)

    assert out == datetime(2000, 1, 1, 10, 42, 21, tzinfo=timezone.utc)
    assert out.tzinfo == timezone.utc


def test_datetime_without_utc_offset_is_assumed_utc():
    naive = datetime(2000, 1, 1, 10, 42, 21, tzinfo=_NoOffset())

    out = ensure_tz_aware(naive)

    assert out == datetime(2000, 1, 1, 10, 42, 21, tzinfo=timezone.utc)
    assert out.tzinfo == timezone.utc


def test_aware_datetime_keeps_its_timezone():
    cet = timezone(timedelta(hours=1))
    aware = datetime(2000, 1, 1, 10, 42, 21, tzinfo=cet)

    out = ensure_tz_aware(aware)

    assert out == aware
    assert out.tzinfo == cet
    assert out.hour == 10


def test_utc_datetime_is_returned_unchanged():
    utc = datetime(2000, 1, 1, 10, 42, 21, tzinfo=timezone.utc)

    assert ensure_tz_aware(utc) == utc

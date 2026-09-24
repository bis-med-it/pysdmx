from datetime import datetime, timedelta, timezone

from pysdmx.util import parse_validity_ts


def test_utc_offset_is_kept():
    out = parse_validity_ts("2020-01-01T00:00:00+02:00")

    assert out == datetime(2020, 1, 1, tzinfo=timezone(timedelta(hours=2)))
    assert out.utcoffset() == timedelta(hours=2)


def test_missing_utc_offset_is_assumed_utc():
    out = parse_validity_ts("2020-01-01T00:00:00")

    assert out == datetime(2020, 1, 1, tzinfo=timezone.utc)
    assert out.tzinfo == timezone.utc

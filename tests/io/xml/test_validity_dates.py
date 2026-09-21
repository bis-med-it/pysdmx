from datetime import datetime, timedelta, timezone

import pytest

from pysdmx.io import write_sdmx
from pysdmx.io.format import Format
from pysdmx.io.reader import read_sdmx
from pysdmx.model import Codelist

CET = timezone(timedelta(hours=1))
STRUCTURE_FORMATS = [
    Format.STRUCTURE_SDMX_ML_2_1,
    Format.STRUCTURE_SDMX_ML_3_0,
    Format.STRUCTURE_SDMX_ML_3_1,
]


@pytest.mark.parametrize("fmt", STRUCTURE_FORMATS)
def test_validity_without_timezone_is_written_as_utc(fmt):
    cl = Codelist(
        id="CL",
        agency="TEST",
        name="CL",
        valid_from=datetime(2020, 1, 1, 12),
        valid_to=datetime(2030, 1, 1, 12),
    )

    out = write_sdmx([cl], fmt)

    assert 'validFrom="2020-01-01T12:00:00Z"' in out
    assert 'validTo="2030-01-01T12:00:00Z"' in out
    back = read_sdmx(out).structures[0]
    assert back.valid_from == datetime(2020, 1, 1, 12, tzinfo=timezone.utc)
    assert back.valid_to == datetime(2030, 1, 1, 12, tzinfo=timezone.utc)


@pytest.mark.parametrize("fmt", STRUCTURE_FORMATS)
def test_validity_keeps_its_timezone(fmt):
    cl = Codelist(
        id="CL",
        agency="TEST",
        name="CL",
        valid_from=datetime(2020, 1, 1, 12, tzinfo=CET),
        valid_to=datetime(2030, 1, 1, 12, tzinfo=CET),
    )

    out = write_sdmx([cl], fmt)

    assert 'validFrom="2020-01-01T12:00:00+01:00"' in out
    assert 'validTo="2030-01-01T12:00:00+01:00"' in out
    back = read_sdmx(out).structures[0]
    assert back.valid_from.isoformat() == "2020-01-01T12:00:00+01:00"
    assert back.valid_to.isoformat() == "2030-01-01T12:00:00+01:00"

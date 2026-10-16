from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from pysdmx.io import write_sdmx
from pysdmx.io.format import Format
from pysdmx.io.reader import read_sdmx
from pysdmx.model import (
    Codelist,
    Concept,
    ConceptScheme,
    DataType,
    Facets,
    RepresentationMap,
)

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


@pytest.mark.parametrize("fmt", STRUCTURE_FORMATS)
def test_time_facets_without_timezone_are_written_as_utc(fmt):
    facets = Facets(
        start_time=datetime(2020, 1, 1, 12),
        end_time=datetime(2030, 1, 1, 12, tzinfo=CET),
    )
    concept = Concept(
        id="C", name="C", dtype=DataType.DATE_TIME, facets=facets
    )
    cs = ConceptScheme(id="CS", agency="TEST", name="CS", items=[concept])

    out = write_sdmx([cs], fmt)

    assert 'startTime="2020-01-01T12:00:00Z"' in out
    assert 'endTime="2030-01-01T12:00:00+01:00"' in out
    back = read_sdmx(out).structures[0].items[0].facets
    assert back.start_time == datetime(2020, 1, 1, 12, tzinfo=timezone.utc)
    assert back.end_time.isoformat() == "2030-01-01T12:00:00+01:00"


def test_value_map_validity_is_read_as_timezone_aware_datetimes():
    sample = Path(__file__).parents[1] / "samples" / "maps.xml"
    # Value map validity is an xs:date in SDMX-ML 3.x.
    text = sample.read_text().replace(
        "<str:RepresentationMapping>",
        '<str:RepresentationMapping validFrom="2020-01-01"'
        ' validTo="2021-01-01">',
        1,
    )

    rm = next(
        s
        for s in read_sdmx(text).structures
        if isinstance(s, RepresentationMap)
    )

    vm = rm.maps[0]
    assert vm.valid_from == datetime(2020, 1, 1, tzinfo=timezone.utc)
    assert vm.valid_to == datetime(2021, 1, 1, tzinfo=timezone.utc)

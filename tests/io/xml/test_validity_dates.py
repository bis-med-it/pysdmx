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
    MultiRepresentationMap,
    MultiValueMap,
    RepresentationMap,
    ValueMap,
)

CET = timezone(timedelta(hours=1))
STRUCTURE_FORMATS = [
    Format.STRUCTURE_SDMX_ML_2_1,
    Format.STRUCTURE_SDMX_ML_3_0,
    Format.STRUCTURE_SDMX_ML_3_1,
]
ML_3_FORMATS = [
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


@pytest.mark.parametrize(
    "value", ["2020-01-01Z", "2020-01-01+01:00", "2020-01-01-05:00"]
)
def test_value_map_validity_timezone_is_ignored(value):
    sample = Path(__file__).parents[1] / "samples" / "maps.xml"
    text = sample.read_text().replace(
        "<str:RepresentationMapping>",
        f'<str:RepresentationMapping validFrom="{value}">',
        1,
    )

    rm = next(
        s
        for s in read_sdmx(text).structures
        if isinstance(s, RepresentationMap)
    )

    assert rm.maps[0].valid_from.isoformat() == "2020-01-01T00:00:00+00:00"


def test_time_facet_date_timezone_is_ignored():
    facets = Facets(start_time=datetime(2020, 1, 1, tzinfo=timezone.utc))
    concept = Concept(
        id="C", name="C", dtype=DataType.DATE_TIME, facets=facets
    )
    cs = ConceptScheme(id="CS", agency="TEST", name="CS", items=[concept])
    # Time facets may also hold an xs:date, with an optional timezone.
    out = write_sdmx([cs], Format.STRUCTURE_SDMX_ML_3_0).replace(
        'startTime="2020-01-01T00:00:00Z"', 'startTime="2020-01-01+01:00"'
    )

    back = read_sdmx(out).structures[0].items[0].facets
    assert back.start_time.isoformat() == "2020-01-01T00:00:00+00:00"


@pytest.mark.parametrize("fmt", ML_3_FORMATS)
def test_value_map_validity_is_written_as_dates(fmt):
    valid_from = datetime(2020, 1, 1, tzinfo=timezone.utc)
    valid_to = datetime(2021, 1, 1, tzinfo=timezone.utc)
    rm = RepresentationMap(
        id="RM",
        agency="TEST",
        name="RM",
        source=DataType.STRING,
        target=DataType.STRING,
        maps=[
            ValueMap(
                source="A",
                target="B",
                valid_from=valid_from,
                valid_to=valid_to,
            )
        ],
    )
    mrm = MultiRepresentationMap(
        id="MRM",
        agency="TEST",
        name="MRM",
        source=[DataType.STRING, DataType.STRING],
        target=[DataType.STRING],
        maps=[
            MultiValueMap(
                source=["A", "B"],
                target=["C"],
                valid_from=valid_from,
                valid_to=valid_to,
            )
        ],
    )

    out = write_sdmx([rm, mrm], fmt)

    # Value map validity is an xs:date in SDMX-ML 3.x.
    mapping = (
        '<str:RepresentationMapping validFrom="2020-01-01"'
        ' validTo="2021-01-01">'
    )
    assert out.count(mapping) == 2
    back = read_sdmx(out, validate=True).structures
    assert {s.id: list(s.maps) for s in back} == {
        "RM": list(rm.maps),
        "MRM": list(mrm.maps),
    }


@pytest.mark.parametrize("fmt", ML_3_FORMATS)
def test_value_map_validity_is_written_as_its_own_calendar_date(fmt):
    vm = ValueMap(
        source="A",
        target="B",
        # 2019-12-31T23:30:00Z
        valid_from=datetime(2020, 1, 1, 0, 30, tzinfo=CET),
        valid_to=datetime(2021, 12, 31, 23, 59, 59),
    )
    rm = RepresentationMap(
        id="RM",
        agency="TEST",
        name="RM",
        source=DataType.STRING,
        target=DataType.STRING,
        maps=[vm],
    )

    out = write_sdmx([rm], fmt)

    assert 'validFrom="2020-01-01"' in out
    assert 'validTo="2021-12-31"' in out

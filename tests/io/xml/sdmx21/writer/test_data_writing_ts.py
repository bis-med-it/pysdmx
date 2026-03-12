from datetime import datetime

import pandas as pd
import pytest

from pysdmx.errors import Invalid
from pysdmx.io import read_sdmx, write_sdmx
from pysdmx.io.format import Format
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.sdmx21.writer.generic_ts import write as write_gen_ts
from pysdmx.io.xml.sdmx21.writer.structure_specific_ts import (
    write as write_str_ts,
)
from pysdmx.model import (
    Component,
    Components,
    Concept,
    Organisation,
    Role,
    Schema,
)
from pysdmx.model.message import Header


@pytest.fixture
def header():
    return Header(
        id="ID",
        prepared=datetime.strptime("2021-01-01", "%Y-%m-%d"),
        sender=Organisation(id="SENDER"),
        receiver=Organisation(id="RECEIVER"),
        source="PySDMX",
    )


@pytest.fixture
def ts_content():
    ds = PandasDataset(
        data=pd.DataFrame(
            {
                "FREQ": ["A", "A", "A"],
                "REF_AREA": ["US", "US", "GB"],
                "TIME_PERIOD": ["2020", "2021", "2020"],
                "OBS_VALUE": [100.0, 200.0, 300.0],
            }
        ),
        structure=Schema(
            context="datastructure",
            id="TEST_TS",
            agency="MD",
            version="1.0",
            components=Components(
                [
                    Component(
                        id="FREQ",
                        role=Role.DIMENSION,
                        concept=Concept(id="FREQ"),
                        required=True,
                    ),
                    Component(
                        id="REF_AREA",
                        role=Role.DIMENSION,
                        concept=Concept(id="REF_AREA"),
                        required=True,
                    ),
                    Component(
                        id="TIME_PERIOD",
                        role=Role.DIMENSION,
                        concept=Concept(id="TIME_PERIOD"),
                        required=True,
                    ),
                    Component(
                        id="OBS_VALUE",
                        role=Role.MEASURE,
                        concept=Concept(id="OBS_VALUE"),
                        required=True,
                    ),
                ]
            ),
        ),
    )
    return [ds]


def test_generic_ts_root_element(header, ts_content):
    result = write_gen_ts(ts_content, header=header)
    assert result.startswith(
        '<?xml version="1.0" encoding="UTF-8"?>\n<mes:GenericTimeSeriesData'
    )
    assert result.strip().endswith("</mes:GenericTimeSeriesData>")


def test_structure_specific_ts_root_element(header, ts_content):
    result = write_str_ts(ts_content, header=header)
    assert result.startswith(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<mes:StructureSpecificTimeSeriesData"
    )
    assert result.strip().endswith("</mes:StructureSpecificTimeSeriesData>")


def test_generic_ts_defaults_time_period(header, ts_content):
    result = write_gen_ts(ts_content, header=header)
    assert 'dimensionAtObservation="TIME_PERIOD"' in result


def test_structure_specific_ts_defaults_time_period(header, ts_content):
    result = write_str_ts(ts_content, header=header)
    assert 'dimensionAtObservation="TIME_PERIOD"' in result


def test_generic_ts_explicit_time_period(header, ts_content):
    dim_mapping = {"DataStructure=MD:TEST_TS(1.0)": "TIME_PERIOD"}
    result = write_gen_ts(
        ts_content,
        header=header,
        dimension_at_observation=dim_mapping,
    )
    assert 'dimensionAtObservation="TIME_PERIOD"' in result


def test_structure_specific_ts_explicit_time_period(header, ts_content):
    dim_mapping = {"DataStructure=MD:TEST_TS(1.0)": "TIME_PERIOD"}
    result = write_str_ts(
        ts_content,
        header=header,
        dimension_at_observation=dim_mapping,
    )
    assert 'dimensionAtObservation="TIME_PERIOD"' in result


def test_generic_ts_rejects_non_time_period(header, ts_content):
    dim_mapping = {"DataStructure=MD:TEST_TS(1.0)": "FREQ"}
    with pytest.raises(Invalid):
        write_gen_ts(
            ts_content,
            header=header,
            dimension_at_observation=dim_mapping,
        )


def test_structure_specific_ts_rejects_non_time_period(header, ts_content):
    dim_mapping = {"DataStructure=MD:TEST_TS(1.0)": "FREQ"}
    with pytest.raises(Invalid):
        write_str_ts(
            ts_content,
            header=header,
            dimension_at_observation=dim_mapping,
        )


def test_generic_ts_round_trip(header, ts_content):
    result = write_gen_ts(ts_content, header=header)
    msg = read_sdmx(result, validate=True)
    assert msg.data is not None
    assert len(msg.data) == 1
    assert msg.data[0].data.shape == (3, 4)


def test_structure_specific_ts_round_trip(header, ts_content):
    result = write_str_ts(ts_content, header=header)
    msg = read_sdmx(result, validate=True)
    assert msg.data is not None
    assert len(msg.data) == 1
    assert msg.data[0].data.shape == (3, 4)


@pytest.mark.parametrize(
    "fmt",
    [
        Format.DATA_SDMX_ML_2_1_GENTS,
        Format.DATA_SDMX_ML_2_1_STRTS,
    ],
)
def test_write_sdmx_ts_formats(header, ts_content, fmt):
    result = write_sdmx(
        ts_content,
        sdmx_format=fmt,
        header=header,
    )
    assert result is not None
    msg = read_sdmx(result, validate=True)
    assert msg.data is not None
    assert len(msg.data) == 1
    assert 'dimensionAtObservation="TIME_PERIOD"' in result


def test_generic_ts_series_structure(header, ts_content):
    result = write_gen_ts(ts_content, header=header)
    assert "<gen:Series>" in result
    assert "<gen:SeriesKey>" in result
    assert "<gen:ObsDimension" in result


def test_structure_specific_ts_series_structure(header, ts_content):
    result = write_str_ts(ts_content, header=header)
    assert "<Series" in result
    assert "TIME_PERIOD=" in result

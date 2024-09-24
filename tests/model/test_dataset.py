import pytest

from pysdmx.model import (
    DataAttributeValue,
    Dataset,
    DimensionValue,
    Group,
    MeasureValue,
    Observation,
    Series,
)


@pytest.fixture()
def ds():
    freq = DimensionValue("FREQ", "M")
    cur1 = DimensionValue("CUR1", "XYZ")
    cur2 = DimensionValue("CUR2", "CHF")
    time = DimensionValue("TIME_PERIOD", "2024-09")
    val = MeasureValue("OBS_VALUE", 42)
    conf = DataAttributeValue("CONF_STATUS", "F")
    coll = DataAttributeValue("COLLECTION", "A")
    unit = DataAttributeValue("UNIT", "XYZ")

    obs = Observation(
        key="FREQ.XYZ.CHF.2024-09",
        dimensions=[freq, cur1, cur2, time],
        attributes=[conf],
        measures=[val],
    )
    ser = Series(
        key="FREQ.XYZ.CHF.*",
        dimensions=[freq, cur1, cur2],
        attributes=[coll],
        observations=[obs],
    )
    grp = Group(key="*.XYZ.CHF.*", dimensions=[cur1, cur2], attributes=[unit])
    return Dataset(
        key="*.*.*.*", dimensions=[], packages=[grp, ser], structure="sdmx_urn"
    )


def test_groups(ds: Dataset):
    groups = [p for p in ds.packages if isinstance(p, Group)]

    assert list(ds.groups) == groups


def test_series(ds: Dataset):
    series = [p for p in ds.packages if isinstance(p, Series)]

    assert list(ds.series) == series

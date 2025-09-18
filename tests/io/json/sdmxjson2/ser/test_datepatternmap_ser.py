from pysdmx.io.json.sdmxjson2.messages.map import JsonDatePatternMap
from pysdmx.model import DatePatternMap


def test_dpm_fixed():
    dpm = DatePatternMap(
        source="ACTIVITY_DATE",
        target="TIME_PERIOD",
        pattern="MM/dd/yyyy",
        frequency="M",
        id="DPM_1",
        locale="en",
        pattern_type="fixed",
    )

    sjson = JsonDatePatternMap.from_model(dpm)

    assert sjson.id == "DPM_1"
    assert sjson.locale == "en"
    assert sjson.sourcePattern == "MM/dd/yyyy"
    assert sjson.targetFrequencyID == "M"
    assert sjson.mappedComponents[0].source == "ACTIVITY_DATE"
    assert sjson.mappedComponents[0].target == "TIME_PERIOD"
    assert sjson.resolvePeriod is None
    assert sjson.frequencyDimension is None
    assert sjson.mappedFrequencies is None


def test_dpm_variable():
    dpm = DatePatternMap(
        source="ACTIVITY_DATE",
        target="TIME_PERIOD",
        pattern="MM/dd/yyyy",
        frequency="FREQ",
        id="DPM_1",
        locale="en",
        pattern_type="variable",
    )

    sjson = JsonDatePatternMap.from_model(dpm)

    assert sjson.id == "DPM_1"
    assert sjson.locale == "en"
    assert sjson.sourcePattern == "MM/dd/yyyy"
    assert sjson.targetFrequencyID is None
    assert sjson.mappedComponents[0].source == "ACTIVITY_DATE"
    assert sjson.mappedComponents[0].target == "TIME_PERIOD"
    assert sjson.resolvePeriod is None
    assert sjson.frequencyDimension == "FREQ"
    assert sjson.mappedFrequencies is None

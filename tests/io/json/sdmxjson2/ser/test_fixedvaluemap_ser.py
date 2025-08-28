from datetime import datetime, timezone

from pysdmx.io.json.sdmxjson2.messages.map import JsonFixedValueMap
from pysdmx.model import FixedValueMap


def test_fvm_src():
    fvm = FixedValueMap(target="OBS_CONF", value="R", located_in="source")

    sjson = JsonFixedValueMap.from_model(fvm)

    assert sjson.source == "OBS_CONF"
    assert sjson.target is None
    assert sjson.values == ["R"]


def test_fvm_tgt():
    fvm = FixedValueMap(target="OBS_CONF", value="R", located_in="target")

    sjson = JsonFixedValueMap.from_model(fvm)

    assert sjson.source is None
    assert sjson.target == "OBS_CONF"
    assert sjson.values == ["R"]

from datetime import datetime, timezone

from pysdmx.io.json.sdmxjson2.messages.map import (
    JsonRepresentationMapping,
    JsonSourceValue,
)
from pysdmx.model import MultiValueMap, ValueMap


def test_vm():
    vm = ValueMap(source="056", target="BEL")

    sjson = JsonRepresentationMapping.from_model(vm)

    assert sjson.sourceValues == [JsonSourceValue("056")]
    assert sjson.targetValues == ["BEL"]
    assert sjson.validFrom is None
    assert sjson.validTo is None


def test_vm_with_validity():
    vf = "2003-07-23T00:00:00"
    vt = "2006-06-01T00:00:00"
    vm = ValueMap(
        source="056",
        target="BEL",
        valid_from=datetime.fromisoformat(vf).replace(tzinfo=timezone.utc),
        valid_to=datetime.fromisoformat(vt).replace(tzinfo=timezone.utc),
    )

    sjson = JsonRepresentationMapping.from_model(vm)

    assert sjson.sourceValues == [JsonSourceValue("056")]
    assert sjson.targetValues == ["BEL"]
    assert sjson.validFrom == "2003-07-23T00:00:00"
    assert sjson.validTo == "2006-06-01T00:00:00"


def test_mvm():
    vm = MultiValueMap(source=["056"], target=["BEL", "BE"])

    sjson = JsonRepresentationMapping.from_model(vm)

    assert sjson.sourceValues == [JsonSourceValue("056")]
    assert sjson.targetValues == ["BEL", "BE"]
    assert sjson.validFrom is None
    assert sjson.validTo is None


def test_mvm_with_validity():
    vf = "2003-07-23T00:00:00"
    vt = "2006-06-01T00:00:00"
    vm = MultiValueMap(
        source=["056"],
        target=["BEL", "BE"],
        valid_from=datetime.fromisoformat(vf).replace(tzinfo=timezone.utc),
        valid_to=datetime.fromisoformat(vt).replace(tzinfo=timezone.utc),
    )

    sjson = JsonRepresentationMapping.from_model(vm)

    assert sjson.sourceValues == [JsonSourceValue("056")]
    assert sjson.targetValues == ["BEL", "BE"]
    assert sjson.validFrom == "2003-07-23T00:00:00"
    assert sjson.validTo == "2006-06-01T00:00:00"

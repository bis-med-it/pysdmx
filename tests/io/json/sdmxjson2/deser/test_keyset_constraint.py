import json

import msgspec
import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages import JsonDataConstraintMessage
from pysdmx.io.json.sdmxjson2.reader.structure import read
from pysdmx.model import DataConstraint, DataKeyValue


@pytest.fixture
def body():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/constraints/keyset.json", "rb"
    ) as f:
        return f.read()


def test_keyset_deser(body):
    res = msgspec.json.Decoder(JsonDataConstraintMessage).decode(body)

    keysets = res.to_model()

    assert len(keysets) == 1
    keyset = keysets[0]
    assert isinstance(keyset, DataConstraint)
    assert keyset.agency == "IAEG-SDGs"
    assert keyset.id == "CN_SERIES_SDG_GLH"
    assert keyset.version == "1.22"
    assert keyset.name == "SDG Series Level content constraints"
    assert keyset.description is None
    assert keyset.valid_from is None
    assert keyset.valid_to is None
    assert keyset.constraint_attachment.data_provider is None
    assert len(keyset.constraint_attachment.data_structures) == 0
    assert len(keyset.constraint_attachment.dataflows) == 1
    assert keyset.constraint_attachment.dataflows[0] == (
        "urn:sdmx:org.sdmx.infomodel.datastructure."
        "Dataflow=IAEG-SDGs:DF_SDG_GLH(1.22)"
    )
    assert len(keyset.constraint_attachment.provision_agreements) == 0
    assert len(keyset.key_sets) == 1
    ks = keyset.key_sets[0]
    assert ks.is_included is True
    assert len(ks.keys) == 2
    for k in ks.keys:
        assert len(k.keys_values) == 4
        for v in k.keys_values:
            assert v.id in [
                "SERIES",
                "UNIT_MEASURE",
                "UNIT_MULT",
                "COMPOSITE_BREAKDOWN",
            ]
            if v.id == "SERIES":
                assert v.value == "SI_POV_DAY1"
            elif v.id == "UNIT_MEASURE":
                assert v.value == "PT"
            elif v.id == "UNIT_MULT":
                assert v.value == "0"
            else:
                assert v.value in ["_T", "MS_MIGRANT"]


@pytest.mark.parametrize("validate", [True, False])
def test_keyset_21_values(body, validate):
    # SDMX-JSON 2.1 lists the values of a data key value in ``values``.
    # The sample becomes a 2.1 message (which has no ``role``) whose key
    # values list their single value that way.
    data = json.loads(body)
    data["meta"]["schema"] = (
        "https://json.sdmx.org/2.1/sdmx-json-structure-schema.json"
    )
    constraint = data["data"]["dataConstraints"][0]
    del constraint["role"]
    for key in constraint["dataKeySets"][0]["keys"]:
        for kv in key["keyValues"]:
            kv["values"] = [kv.pop("value")]

    msg = read(json.dumps(data), validate=validate)

    keys = msg.get_data_constraints()[0].key_sets[0].keys
    assert keys[0].keys_values == (
        DataKeyValue("SERIES", "SI_POV_DAY1"),
        DataKeyValue("UNIT_MEASURE", "PT"),
        DataKeyValue("UNIT_MULT", "0"),
        DataKeyValue("COMPOSITE_BREAKDOWN", "_T"),
    )


def test_keyset_deser_several_values(body):
    data = json.loads(body)
    key = data["data"]["dataConstraints"][0]["dataKeySets"][0]["keys"][0]
    key["keyValues"][0] = {
        "id": "SERIES",
        "values": ["SI_POV_DAY1", "SI_POV_DAY2"],
    }
    modified_body = json.dumps(data).encode()

    res = msgspec.json.Decoder(JsonDataConstraintMessage).decode(modified_body)

    with pytest.raises(errors.NotImplemented, match="SERIES"):
        res.to_model()


def test_keyset_deser_without_value(body):
    data = json.loads(body)
    key = data["data"]["dataConstraints"][0]["dataKeySets"][0]["keys"][0]
    key["keyValues"][0] = {"id": "SERIES"}
    modified_body = json.dumps(data).encode()

    res = msgspec.json.Decoder(JsonDataConstraintMessage).decode(modified_body)

    with pytest.raises(errors.Invalid, match="SERIES"):
        res.to_model()

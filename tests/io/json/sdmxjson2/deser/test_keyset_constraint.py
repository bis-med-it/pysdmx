import msgspec
import pytest

from pysdmx.io.json.sdmxjson2.messages import JsonDataConstraintMessage
from pysdmx.model import DataConstraint


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
    assert keyset.role == "Allowed"
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

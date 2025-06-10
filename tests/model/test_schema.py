from datetime import datetime

import msgspec
import pytest

from pysdmx.model import (
    ArrayBoundaries,
    Component,
    Components,
    Concept,
    DataType,
    Facets,
    Role,
    Schema,
    decoders,
    encoders,
)


@pytest.fixture
def id():
    return "5B0"


@pytest.fixture
def agency():
    return "BIS"


@pytest.fixture
def context():
    return "dataflow"


@pytest.fixture
def artefacts():
    return ["urn1", "urn2"]


@pytest.fixture
def version():
    return "1.42"


@pytest.fixture
def components():
    f1 = Component(
        "FREQ",
        True,
        Role.DIMENSION,
        Concept("FREQ", dtype=DataType.STRING),
        DataType.ALPHA,
        Facets(min_length=1, max_length=3),
    )
    f2 = Component(
        "INDICATOR", True, Role.DIMENSION, Concept("IND"), DataType.STRING
    )
    f3 = Component(
        "PERIOD", True, Role.DIMENSION, Concept("PERIOD"), DataType.PERIOD
    )
    f4 = Component(
        "VALUE", False, Role.MEASURE, Concept("VALUE"), DataType.INTEGER
    )
    f5 = Component(
        "CONF",
        True,
        Role.ATTRIBUTE,
        Concept("CONF"),
        DataType.STRING,
        attachment_level="O",
        array_def=ArrayBoundaries(1, 3),
    )
    return Components([f1, f2, f3, f4, f5])


def test_defaults(context, agency, id, components):
    schema = Schema(context, agency, id, components)

    assert schema.context == context
    assert schema.agency == agency
    assert schema.id == id
    assert schema.components == components
    assert schema.version == "1.0"
    assert len(schema.artefacts) == 0
    assert isinstance(schema.generated, datetime)


def test_full_instantiation(
    context, agency, id, components, version, artefacts
):
    schema = Schema(context, agency, id, components, version, artefacts)

    assert schema.context == context
    assert schema.agency == agency
    assert schema.id == id
    assert schema.components == components
    assert schema.version == version
    assert len(schema.artefacts) == 2
    assert schema.artefacts == artefacts
    assert isinstance(schema.generated, datetime)


def test_immutable(context, agency, id, components):
    schema = Schema(context, agency, id, components)
    with pytest.raises(AttributeError):
        schema.version = "0.142"


def test_equal(context, agency, id, components):
    org1 = Schema(context, agency, id, components)
    org2 = Schema(context, agency, id, components)

    assert org1 == org2


def test_not_equal(context, agency, id, components):
    org1 = Schema(context, agency, id, components)
    org2 = Schema(context, agency, id, components, version="1.42")

    assert org1 != org2


def test_tostr(context, agency, id, components, artefacts):
    o = Schema(context, agency, id, components, artefacts=artefacts)

    s = str(o)

    assert s == (
        "context: dataflow, agency: BIS, id: 5B0, components: 5 components, "
        "artefacts: 2 artefacts"
    )


def test_tostr_empty(context, agency, id, components, artefacts):
    o = Schema(context, agency, id, components, artefacts=[])

    s = str(o)

    assert s == (
        "context: dataflow, agency: BIS, id: 5B0, components: 5 components"
    )


def test_torepr(context, agency, id, components, artefacts):
    o = Schema(context, agency, id, components, artefacts=artefacts)

    s = repr(o)

    assert s == (
        "Schema("
        "context='dataflow', "
        "agency='BIS', "
        "id='5B0', "
        "components=Components("
        "data=["
        "Component("
        "id='FREQ', "
        "required=True, "
        "role=Dimension, "
        "concept=Concept(id='FREQ', dtype=String), "
        "local_dtype=Alpha, "
        "local_facets=Facets(min_length=1, max_length=3)), "
        "Component("
        "id='INDICATOR', "
        "required=True, "
        "role=Dimension, "
        "concept=Concept(id='IND'), "
        "local_dtype=String), "
        "Component("
        "id='PERIOD', "
        "required=True, "
        "role=Dimension, "
        "concept=Concept(id='PERIOD'), "
        "local_dtype=ObservationalTimePeriod), "
        "Component("
        "id='VALUE', "
        "required=False, "
        "role=Measure, "
        "concept=Concept(id='VALUE'), "
        "local_dtype=Integer), "
        "Component("
        "id='CONF', "
        "required=True, "
        "role=Attribute, "
        "concept=Concept(id='CONF'), "
        "local_dtype=String, "
        "attachment_level='O', "
        "array_def=ArrayBoundaries(min_size=1, max_size=3))]), "
        "artefacts=['urn1', 'urn2'])"
    )


def test_torepr_empty(context, agency, id, components):
    o = Schema(context, agency, id, components, artefacts=[])

    s = repr(o)

    assert s == (
        "Schema("
        "context='dataflow', "
        "agency='BIS', "
        "id='5B0', "
        "components=Components("
        "data=["
        "Component("
        "id='FREQ', "
        "required=True, "
        "role=Dimension, "
        "concept=Concept(id='FREQ', dtype=String), "
        "local_dtype=Alpha, "
        "local_facets=Facets(min_length=1, max_length=3)), "
        "Component("
        "id='INDICATOR', "
        "required=True, "
        "role=Dimension, "
        "concept=Concept(id='IND'), "
        "local_dtype=String), "
        "Component("
        "id='PERIOD', "
        "required=True, "
        "role=Dimension, "
        "concept=Concept(id='PERIOD'), "
        "local_dtype=ObservationalTimePeriod), "
        "Component("
        "id='VALUE', "
        "required=False, "
        "role=Measure, "
        "concept=Concept(id='VALUE'), "
        "local_dtype=Integer), "
        "Component("
        "id='CONF', "
        "required=True, "
        "role=Attribute, "
        "concept=Concept(id='CONF'), "
        "local_dtype=String, "
        "attachment_level='O', "
        "array_def=ArrayBoundaries(min_size=1, max_size=3))]))"
    )


def test_serialization(context, agency, id, components, version, artefacts):
    schema = Schema(context, agency, id, components, version, artefacts)

    ser = msgspec.msgpack.Encoder(enc_hook=encoders).encode(schema)
    out = msgspec.msgpack.Decoder(Schema, dec_hook=decoders).decode(ser)
    assert out == schema

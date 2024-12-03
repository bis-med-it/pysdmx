from datetime import datetime

import pytest

from pysdmx.model import Component, Components, DataType, Role, Schema


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
def components():
    f1 = Component("FREQ", True, Role.DIMENSION, DataType.STRING)
    f2 = Component("INDICATOR", True, Role.DIMENSION, DataType.STRING)
    f3 = Component("PERIOD", True, Role.DIMENSION, DataType.PERIOD)
    f4 = Component("VALUE", False, Role.MEASURE, DataType.INTEGER)
    f5 = Component(
        "CONF",
        True,
        Role.ATTRIBUTE,
        DataType.STRING,
        attachment_level="O",
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


def test_full_instantiation(context, agency, id, components):
    artefacts = ["urn1", "urn2"]
    v = "1.42"
    schema = Schema(context, agency, id, components, v, artefacts)

    assert schema.context == context
    assert schema.agency == agency
    assert schema.id == id
    assert schema.components == components
    assert schema.version == v
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


def test_tostr(context, agency, id, components):
    o = Schema(context, agency, id, components)

    s = str(o)

    exp = (
        f"context={context}, "
        f"agency={agency}, "
        f"id={id}, "
        f"components={str(components)}, "
        f"version=1.0, "
        f"generated="
    )

    assert s.startswith(exp)

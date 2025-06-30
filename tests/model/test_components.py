import pytest

from pysdmx.errors import Invalid
from pysdmx.model.concept import DataType
from pysdmx.model.dataflow import Component, Components, Role


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


def test_length(components):
    assert len(components) == 5


def test_get_by_name(components):
    exp = Component("FREQ", True, Role.DIMENSION, DataType.STRING)

    rec = components["FREQ"]

    assert rec == exp


def test_get_by_position(components):
    exp = Component("FREQ", True, Role.DIMENSION, DataType.STRING)

    rec = components[0]

    assert rec == exp


def test_get_slice(components):
    exp = [
        Component("FREQ", True, Role.DIMENSION, DataType.STRING),
        Component("INDICATOR", True, Role.DIMENSION, DataType.STRING),
    ]

    rec = components[0:2]

    assert rec == exp


def test_unknown_component(components):
    assert components["0"] is None


def test_append_works(components):
    len1 = len(components)
    nf = Component("ZZZ", False, Role.DIMENSION, DataType.STRING)

    components.append(nf)

    assert len(components) == len1 + 1


def test_append_invalid(components):
    with pytest.raises(
        Invalid,
        match="Unexpected type. Expected Component but got: <class 'int'>$",
    ):
        components.append(202)


def test_append_existing(components):
    with pytest.raises(
        Invalid,
        match="There is already a component with ID: FREQ$",
    ):
        components.append(components[0])


def test_insert_works(components):
    idx = len(components)
    nf = Component("ZZZ", False, Role.DIMENSION, DataType.STRING)

    components.insert(idx, nf)

    assert len(components) == idx + 1


def test_insert_invalid(components):
    idx = len(components)

    with pytest.raises(
        Invalid,
        match="Unexpected type. Expected Component but got: <class 'int'>$",
    ):
        components.insert(idx, 202)


def test_insert_existing(components):
    idx = len(components)

    with pytest.raises(
        Invalid,
        match="There is already a component with ID: FREQ$",
    ):
        components.insert(idx, components[0])


def test_setitem_works(components):
    idx = len(components)
    nf = Component("ZZZ", False, Role.DIMENSION, DataType.STRING)

    components[idx - 1] = nf

    assert len(components) == idx


def test_setitem_invalid(components):
    idx = len(components)

    with pytest.raises(
        Invalid,
        match="Unexpected type. Expected Component but got: <class 'int'>$",
    ):
        components[idx] = 202


def test_setitem_existing(components):
    idx = len(components)

    with pytest.raises(
        Invalid,
        match="There is already a component with ID: FREQ$",
    ):
        components[idx] = components[0]


def test_extend_works(components):
    len1 = len(components)
    nf1 = Component("ZZZ", False, Role.DIMENSION, DataType.STRING)
    nf2 = Component("Z42", False, Role.DIMENSION, DataType.STRING)

    components.extend([nf1, nf2])

    assert len(components) == len1 + 2


def test_extend_invalid(components):
    nf = Component("ZZZ", False, Role.DIMENSION, DataType.STRING)

    with pytest.raises(
        Invalid,
        match="Unexpected type. Expected Component but got: <class 'int'>$",
    ):
        components.extend([nf, 202])


def test_extend_existing(components):
    nf = Component("ZZZ", False, Role.DIMENSION, DataType.STRING)

    with pytest.raises(
        Invalid,
        match="There are duplicates in the collection: \\['ZZZ'\\]$",
    ):
        components.extend([nf, nf])


def test_extend_with_one_is_checked(components):
    with pytest.raises(
        Invalid,
        match="There is already a component with ID: FREQ$",
    ):
        components.extend([components[0]])


def test_extend_with_empty_coll(components):
    count = len(components)

    components.extend([])

    assert len(components) == count


def test_get_dimensions(components):
    expected = ["FREQ", "INDICATOR", "PERIOD"]

    dims = components.dimensions

    assert len(dims) == 3
    for dim in dims:
        assert dim.id in expected


def test_get_measures(components):
    expected = ["VALUE"]

    measures = components.measures

    assert len(measures) == 1
    for m in measures:
        assert m.id in expected


def test_get_attributes(components):
    expected = ["CONF"]

    attrs = components.attributes

    assert len(attrs) == 1
    for attr in attrs:
        assert attr.id in expected


def test_tostr(components):
    expected_str = "data: 5 components"
    assert str(components) == expected_str


def test_torepr(components):
    expected_repr = (
        "Components(data=[Component(id='FREQ', required=True, "
        "role=Role.DIMENSION, "
        "concept=DataType.STRING), Component(id='INDICATOR', required=True, "
        "role=Role.DIMENSION, concept=DataType.STRING), "
        "Component(id='PERIOD', "
        "required=True, role=Role.DIMENSION, "
        "concept=DataType.PERIOD), Component(id='VALUE', "
        "required=False, role=Role.MEASURE, concept=DataType.INTEGER), "
        "Component(id='CONF', required=True, role=Role.ATTRIBUTE, "
        "concept=DataType.STRING, attachment_level='O')])"
    )

    assert repr(components) == expected_repr

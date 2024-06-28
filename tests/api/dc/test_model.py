from pysdmx.api.dc.query._model import Operator


def test_expected_operator():
    expected = [
        "=",
        "<>",
        "<",
        ">",
        "<=",
        ">=",
        "LIKE",
        "NOT LIKE",
        "IN",
        "NOT IN",
        "BETWEEN",
        "NOT BETWEEN",
        "IS NULL",
        "IS NOT NULL",
    ]

    operators = [v.value for v in Operator._member_map_.values()]

    assert len(expected) == len(operators)
    for o in expected:
        assert o in operators

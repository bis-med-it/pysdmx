from pysdmx.model.dataset import ActionType


def test_to_str_action():
    action = ActionType.Information
    assert str(action) == "Information"


def test_to_repr_action():
    action = ActionType.Information
    assert repr(action) == "ActionType.Information"

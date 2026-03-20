import pytest

from pysdmx.util import is_final


@pytest.mark.parametrize(
    ("version", "expected"),
    [
        ("1.0.0", True),
        ("2.3.1", True),
        ("0.0.1", False),
        ("10.20.30", True),
        ("1.0.0-draft", False),
        ("1.0.0-rc1", False),
        ("1.0.0-beta", False),
        ("1.0.0-alpha.1", False),
        ("1.0.0-0.3.7", False),
        ("1.0.0-draft.1", False),
        ("01.0.0", False),
        ("1.01.0", False),
        ("1.0.01", False),
        ("1.0", False),
        ("1", False),
        ("", False),
        ("1.0.0.0", False),
    ],
)
def test_is_final(version, expected):
    assert is_final(version) is expected

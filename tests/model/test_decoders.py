import pytest

from pysdmx.model import decoders


def test_others():
    with pytest.raises(NotImplementedError):
        decoders(int, 42)

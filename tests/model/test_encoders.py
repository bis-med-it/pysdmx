import re
from typing import List

import pytest

from pysdmx.errors import NotImplemented
from pysdmx.model import Component, Components, Concept, encoders, Role


def test_pattern():
    p = re.compile("^[A-Z]{3}$")

    out = encoders(p)

    assert isinstance(out, str)
    assert out == "regex:^[A-Z]{3}$"


def test_components():
    c1 = Component("IND", True, Role.DIMENSION, Concept("IND"))
    c2 = Component("VAL", True, Role.MEASURE, Concept("VAL"))
    comps = Components([c1, c2])

    out = encoders(comps)

    assert isinstance(out, List)
    assert len(out) == 2
    assert out[0] == c1
    assert out[1] == c2


def test_others():
    with pytest.raises(NotImplemented):
        encoders(42)

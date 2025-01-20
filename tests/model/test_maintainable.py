import pytest

from pysdmx.errors import PysdmxError
from pysdmx.model.__base import MaintainableArtefact


def test_empty_agency_not_allowed():
    with pytest.raises(PysdmxError, match="must reference an agency"):
        MaintainableArtefact("ID")

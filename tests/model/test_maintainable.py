import pytest

from pysdmx.errors import Error
from pysdmx.model.__base import MaintainableArtefact


def test_empty_agency_not_allowed():
    with pytest.raises(Error, match="must reference an agency"):
        MaintainableArtefact("ID")

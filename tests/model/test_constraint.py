"""Unit tests for the SDMX data constraint model."""

from pysdmx.model import ConstraintRole, DataConstraint


def test_data_constraint_role_defaults_to_allowed():
    dc = DataConstraint(id="C1", agency="AG")
    assert dc.role == ConstraintRole.ALLOWED


def test_data_constraint_role_actual():
    dc = DataConstraint(id="C1", agency="AG", role=ConstraintRole.ACTUAL)
    assert dc.role is ConstraintRole.ACTUAL


def test_constraint_role_values_match_sdmx():
    assert ConstraintRole.ALLOWED.value == "Allowed"
    assert ConstraintRole.ACTUAL.value == "Actual"
    assert ConstraintRole("Actual") is ConstraintRole.ACTUAL

import httpx
import pytest

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.io.format import Format
from pysdmx.model import DataConstraint


def check_data_constraint(
    mock,
    fmr: RegistryClient,
    query: str,
    body: bytes,
    agency: str,
    id: str,
    cube_values: tuple[tuple[str, tuple[str, ...]], ...],
    is_fusion: bool = False,
) -> None:
    """get_data_constraint() should return one data constraint."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    constraint = fmr.get_data_constraint(agency, id)

    _check_data_constraint(
        mock, constraint, agency, id, cube_values, is_fusion
    )


async def check_data_constraint_async(
    mock,
    fmr: AsyncRegistryClient,
    query: str,
    body: bytes,
    agency: str,
    id: str,
    cube_values: tuple[tuple[str, tuple[str, ...]], ...],
    is_fusion: bool = False,
) -> None:
    """get_data_constraint() should return one data constraint."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    constraint = await fmr.get_data_constraint(agency, id)

    _check_data_constraint(
        mock, constraint, agency, id, cube_values, is_fusion
    )


def check_keyset_constraint(
    mock,
    fmr: RegistryClient,
    query: str,
    body: bytes,
    agency: str,
    id: str,
) -> None:
    """get_data_constraint() may return a keyset constraint."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    constraint = fmr.get_data_constraint(agency, id)

    _check_keyset_constraint(constraint)


def _check_data_constraint(
    mock,
    constraint: DataConstraint,
    agency: str,
    id: str,
    cube_values: tuple[tuple[str, tuple[str, ...]], ...],
    is_fusion: bool,
) -> None:
    assert len(mock.calls) == 1
    expected_format = (
        Format.FUSION_JSON.value
        if is_fusion
        else Format.STRUCTURE_SDMX_JSON_2_0_0.value
    )
    assert mock.calls[0].request.headers["Accept"] == expected_format

    assert isinstance(constraint, DataConstraint)
    assert constraint.id == id
    assert constraint.agency == agency
    assert constraint.version == "1.0"
    assert constraint.name == "Constraints for the CBS dataflow"
    assert constraint.description is None
    assert not constraint.constraint_attachment.data_structures
    assert not constraint.constraint_attachment.data_provider
    assert not constraint.constraint_attachment.provision_agreements
    assert len(constraint.constraint_attachment.dataflows) == 1
    assert (
        constraint.constraint_attachment.dataflows[0]
        == "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow="
        "BIS.CBS:CBS(1.0)"
    )
    assert len(constraint.cube_regions) == 1
    assert constraint.cube_regions[0].is_included is True
    assert (
        tuple(
            (key_value.id, tuple(value.value for value in key_value.values))
            for key_value in constraint.cube_regions[0].key_values
        )
        == cube_values
    )
    assert len(constraint.key_sets) == 0


def _check_keyset_constraint(constraint: DataConstraint) -> None:
    assert len(constraint.cube_regions) == 0
    assert len(constraint.key_sets) == 1
    assert constraint.key_sets[0].is_included is True
    assert len(constraint.key_sets[0].keys) == 2
    for dks in constraint.key_sets[0].keys:
        assert len(dks.keys_values) == 6
        for kv in dks.keys_values:
            if kv.id == "CBS_BASIS":
                assert kv.value == "F"
            elif kv.id == "L_POSITION":
                assert kv.value == "L"
            elif kv.id == "L_INSTR":
                assert kv.value in ["A", "G"]
            elif kv.id in ["REM_MATURITY", "L_CP_SECTOR"]:
                assert kv.value == "A"
            elif kv.id == "CURR_TYPE_BOOK":
                assert kv.value == "TO1"
            else:
                pytest.fail(f"Unexpected component: {kv.id}")
        assert dks.valid_from is None
        assert dks.valid_to is None

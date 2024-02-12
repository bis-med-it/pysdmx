from datetime import datetime

import httpx
import pytest

from pysdmx.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.model import Code, Codelist, Concept, ConceptScheme, DataType


def check_cs(mock, fmr: RegistryClient, query, body):
    """get_concepts() should return a concept scheme."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    cs = fmr.get_concepts("BIS.MEDIT", "MEDIT_CS")

    assert isinstance(cs, ConceptScheme)
    assert len(cs) == 5
    assert cs.id == "MEDIT_CS"
    assert cs.name == "List of concepts used by MED IT"
    assert cs.agency == "BIS.MEDIT"
    assert cs.description is None
    assert cs.version == "1.0"
    for concept in cs:
        assert isinstance(concept, Concept)


async def check_concept_core_info(mock, fmr: AsyncRegistryClient, query, body):
    """Concepts must contain core information such as ID and name."""
    mock.get(query).mock(return_value=httpx.Response(200, content=body))

    cs = await fmr.get_concepts("BIS.MEDIT", "MEDIT_CS")

    for concept in cs:
        assert concept.id in [
            "mapping_mode",
            "default_flow",
            "block_on_error",
            "DIM3",
            "DIM4",
        ]
        assert concept.name is not None
        assert concept.dtype is not None


def check_concept_details(mock, fmr: RegistryClient, query, body):
    """Concepts may have extended information."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    cs = fmr.get_concepts("BIS.MEDIT", "MEDIT_CS")

    for concept in cs:
        if concept.id == "mapping_mode":
            assert concept.description is None
            assert concept.dtype == DataType.STRING
            assert len(concept.codes) == 3
            assert isinstance(concept.codes, Codelist)
            assert concept.codes.id == "MEDAL_NMM"
            assert concept.codes.agency == "BIS.MEDIT"
            assert concept.codes.version == "1.0"
            assert concept.codes.sdmx_type == "codelist"
            assert concept.codes.name == "MEDAL Mapping Modes"
            assert concept.codes.description is not None
            for c in concept.codes:
                isinstance(c, Code)
                assert c.id in ["F", "I", "W"]
            assert concept.facets is not None
            assert concept.facets.min_length == 1
            assert concept.facets.max_length == 1
        elif concept.id == "default_flow":
            assert concept.description is not None
            assert concept.dtype == DataType.STRING
            assert not concept.codes
            assert concept.facets is not None
            assert concept.facets.max_length == 250
        elif concept.id == "block_on_error":
            exp = "Block the flow if there is an error in the submission"
            assert concept.description == exp
            assert concept.dtype == DataType.BOOLEAN
            assert not concept.codes
            assert concept.facets is None
        elif concept.id == "DIM3":
            assert concept.description is None
            assert concept.dtype == DataType.YEAR_MONTH
            assert concept.facets is not None
            assert concept.facets.start_time == datetime(2000, 1, 1, 0, 0, 0)
            assert concept.facets.end_time == datetime(
                2020,
                12,
                31,
                23,
                59,
                59,
            )
            assert concept.facets.is_sequence is True
        elif concept.id == "DIM4":
            assert concept.description is None
            assert concept.dtype == DataType.STRING
            assert concept.facets is None
        else:
            pytest.fail(f"Unexpected concept {concept.id}")

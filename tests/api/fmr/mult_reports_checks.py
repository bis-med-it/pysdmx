from typing import Sequence

import httpx

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.io.format import Format
from pysdmx.model import MetadataAttribute


def check_reports(
    mock, fmr: RegistryClient, query, body, is_fusion: bool = False
):
    """get_reports() should return multiple metadata reports."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    reports = fmr.get_reports("dataflow", "BIS.MACRO", "BIS_MACRO", "1.0")

    assert len(mock.calls) == 1
    if is_fusion:
        assert (
            mock.calls[0].request.headers["Accept"] == Format.FUSION_JSON.value
        )
    else:
        assert (
            mock.calls[0].request.headers["Accept"]
            == Format.REFMETA_SDMX_JSON_2_0_0.value
        )

    assert isinstance(reports, Sequence)
    assert len(reports) == 2
    for r in reports:
        assert "Dataflow=BIS.MACRO:BIS_MACRO(1.0)" in r.targets[0]
        if r.id == "DTI_BIS_MACRO":
            assert r.name == "Technical metadata for BIS.MACRO:BIS_MACRO"
            assert r.metadataflow == (
                "urn:sdmx:org.sdmx.infomodel.metadatastructure.Metadataflow="
                "BIS.MEDIT:DTI(1.0)"
            )
            assert len(r.targets) == 1

            assert len(r) == 5
            for attr in r:
                assert isinstance(attr, MetadataAttribute)
        else:
            assert r.name == "Reference metadata for BIS.MACRO:BIS_MACRO"
            assert r.metadataflow == (
                "urn:sdmx:org.sdmx.infomodel.metadatastructure.Metadataflow="
                "BIS:DF_META(1.0)"
            )
            assert len(r.targets) == 1

            assert len(r) == 1
            for attr in r:
                assert isinstance(attr, MetadataAttribute)


async def check_reports_async(mock, fmr: AsyncRegistryClient, query, body):
    """get_reports() should return multiple metadata reports."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    reports = await fmr.get_reports(
        "dataflow", "BIS.MACRO", "BIS_MACRO", "1.0"
    )

    assert isinstance(reports, Sequence)
    assert len(reports) == 2
    for r in reports:
        assert "Dataflow=BIS.MACRO:BIS_MACRO(1.0)" in r.targets[0]
        if r.id == "DTI_BIS_MACRO":
            assert r.name == "Technical metadata for BIS.MACRO:BIS_MACRO"
            assert r.metadataflow == (
                "urn:sdmx:org.sdmx.infomodel.metadatastructure.Metadataflow="
                "BIS.MEDIT:DTI(1.0)"
            )
            assert len(r.targets) == 1

            assert len(r) == 5
            for attr in r:
                assert isinstance(attr, MetadataAttribute)
        else:
            assert r.name == "Reference metadata for BIS.MACRO:BIS_MACRO"
            assert r.metadataflow == (
                "urn:sdmx:org.sdmx.infomodel.metadatastructure.Metadataflow="
                "BIS:DF_META(1.0)"
            )
            assert len(r.targets) == 1

            assert len(r) == 1
            for attr in r:
                assert isinstance(attr, MetadataAttribute)

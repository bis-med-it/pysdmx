from typing import Sequence

import httpx

from pysdmx.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.model import Category, CategoryScheme


def check_categories(mock, fmr: RegistryClient, query, body):
    """get_categories() should return a category scheme."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    cs = fmr.get_categories("TEST", "TEST_CS")

    assert isinstance(cs, CategoryScheme)
    assert len(cs) == 8
    assert cs.id == "TEST_CS"
    assert cs.name == "Test Category Scheme"
    assert cs.agency == "TEST"
    assert cs.description is None
    assert cs.version == "1.0"
    for cat in cs:
        assert isinstance(cat, Category)


async def check_category_core_info(
    mock,
    fmr: AsyncRegistryClient,
    query,
    body,
):
    """Categories must contain core information such as ID and name."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    cs = await fmr.get_categories("TEST", "TEST_CS")

    __check_core_info(cs.categories)


def check_category_details(mock, fmr: RegistryClient, query, body):
    """Categories may have extended information."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    cs = fmr.get_categories("TEST", "TEST_CS")

    for cat in cs:
        if cat.id == "ONE":
            assert cat.description is None
            assert not cat.categories
            assert len(cat.dataflows) == 3
        elif cat.id == "TWO":
            assert cat.description is None
            assert not cat.dataflows
            assert len(cat.categories) == 1
            child = cat.categories[0]
            assert child.id == "TWO_KID"
            assert child.description is None
            assert not child.categories
            assert len(child.dataflows) == 2
        elif cat.id == "THREE":
            assert cat.description is not None
            assert not cat.dataflows
            assert len(cat.categories) == 1
            child = cat.categories[0]
            assert child.id == "THREE_KID"
            assert child.description is None
            assert not child.categories
            assert not child.dataflows

        else:
            assert cat.id in ["FOUR", "FIVE", "SIX"]
            assert cat.description is None
            assert not cat.categories
            assert not cat.dataflows


def __check_core_info(categories: Sequence[Category]):
    for cat in categories:
        assert cat.id in [
            "ONE",
            "TWO",
            "THREE",
            "FOUR",
            "FIVE",
            "SIX",
            "TWO_KID",
            "THREE_KID",
        ]
        assert cat.name.upper().replace(" ", "_") == cat.id
        if cat.categories:
            __check_core_info(cat.categories)

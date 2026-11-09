from datetime import datetime, timezone

import httpx
import pytest

from pysdmx.api.fmr.maintenance import (
    RegistryMaintenanceClient,
    RegistryTransactionsClient,
)
from pysdmx.errors import InternalError, Invalid
from pysdmx.model.message import Message, MetadataMessage, StructureMessage


@pytest.mark.parametrize(
    ("endpoint", "expected_endpoint"),
    [
        ("https://registry.sdmx.org/", "https://registry.sdmx.org"),
        (
            "https://registry.sdmx.org/sdmx/v2",
            "https://registry.sdmx.org",
        ),
        (
            "https://registry.sdmx.org/ws/secure/sdmxapi/rest",
            "https://registry.sdmx.org",
        ),
    ],
)
def test_transactions_client_sanitizes_endpoint(
    endpoint: str, expected_endpoint: str
) -> None:
    client = RegistryTransactionsClient(endpoint, timeout=30.0)

    assert client._api_endpoint == expected_endpoint
    assert client._timeout == 30.0


def test_maintenance_client_is_transactions_client() -> None:
    client = RegistryMaintenanceClient(
        "https://registry.sdmx.org", "user", "password"
    )

    assert isinstance(client, RegistryTransactionsClient)


def test_list_transactions(respx_mock) -> None:
    with open("tests/api/fmr/maintenance/samples/tx.json", "rb") as sample:
        respx_mock.get(
            "https://registry.sdmx.org/ws/registry/transactions"
        ).mock(return_value=httpx.Response(200, content=sample.read()))

    client = RegistryTransactionsClient("https://registry.sdmx.org")

    transactions = client.list_transactions()

    assert len(transactions) == 3
    assert transactions[0].meta.transaction_id == "9068"
    assert transactions[0].meta.transaction_time == datetime(
        2026, 10, 15, 15, 47, 57, 85000, tzinfo=timezone.utc
    )
    assert transactions[0].data.inserted == [
        "urn:sdmx:org.sdmx.infomodel.codelist.ValueList="
        "BIS:CMS_REPORT_HASH_REGISTRY(1.0)",
    ]
    assert transactions[0].data.updated == [
        "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=BIS:CL_FREQ(1.0)",
        "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=BIS:CL_BIS_UNIT(1.0)",
    ]
    assert transactions[0].data.deleted == []
    assert transactions[1].meta.transaction_id == "9067"
    assert transactions[1].meta.transaction_time == datetime(
        2026, 10, 15, 15, 47, 56, 450000, tzinfo=timezone.utc
    )
    assert transactions[1].data.inserted == []
    assert transactions[1].data.updated == [
        "urn:sdmx:org.sdmx.infomodel.metadatastructure.MetadataSet="
        "BIS:BIS_DA_CBS(1.0)"
    ]
    assert transactions[1].data.deleted == []
    assert transactions[2].meta.transaction_id == "9067"
    assert transactions[2].meta.transaction_time == datetime(
        2026, 10, 15, 15, 47, 56, 442000, tzinfo=timezone.utc
    )
    assert transactions[2].data.inserted == []
    assert transactions[2].data.updated == []
    assert transactions[2].data.deleted == [
        "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=BIS.TEST:TEST(1.0)"
    ]


def test_list_transactions_with_updated_after(respx_mock) -> None:
    updated_after = datetime(
        2026, 8, 26, 7, 56, 53, 976000, tzinfo=timezone.utc
    )
    endpoint = (
        "https://registry.sdmx.org/ws/registry/transactions?"
        "updatedAfter=1787731013976"
    )
    respx_mock.get(endpoint).mock(return_value=httpx.Response(200, json=[]))
    client = RegistryTransactionsClient("https://registry.sdmx.org")

    transactions = client.list_transactions(updated_after)

    assert transactions == []


def test_list_transactions_with_naive_updated_after(respx_mock) -> None:
    endpoint = (
        "https://registry.sdmx.org/ws/registry/transactions?"
        "updatedAfter=1787731013976"
    )
    respx_mock.get(endpoint).mock(return_value=httpx.Response(200, json=[]))
    client = RegistryTransactionsClient("https://registry.sdmx.org")

    transactions = client.list_transactions(
        datetime(2026, 8, 26, 7, 56, 53, 976000)
    )

    assert transactions == []


def test_list_transactions_maps_http_errors(respx_mock) -> None:
    respx_mock.get("https://registry.sdmx.org/ws/registry/transactions").mock(
        return_value=httpx.Response(409, text="Conflict")
    )
    client = RegistryTransactionsClient("https://registry.sdmx.org")

    with pytest.raises(Invalid, match="Client error 409"):
        client.list_transactions()


@pytest.mark.json
def test_get_structure_transaction(respx_mock) -> None:
    with open(
        "tests/io/json/sdmxjson2/deser/samples/reader/structs.json", "rb"
    ) as sample:
        respx_mock.get(
            "https://registry.sdmx.org/ws/registry/transactions/9068"
        ).mock(return_value=httpx.Response(200, content=sample.read()))
    client = RegistryTransactionsClient("https://registry.sdmx.org")

    transaction = client.get_transaction("9068")

    assert isinstance(transaction, StructureMessage)
    assert transaction.header.id == "IREF195025"
    assert len(transaction.structures) == 261


@pytest.mark.json
def test_get_metadata_transaction(respx_mock) -> None:
    with open(
        "tests/io/json/sdmxjson2/deser/samples/reports/report.json", "rb"
    ) as sample:
        respx_mock.get(
            "https://registry.sdmx.org/ws/registry/transactions/9067"
        ).mock(return_value=httpx.Response(200, content=sample.read()))
    client = RegistryTransactionsClient("https://registry.sdmx.org")

    transaction = client.get_transaction("9067")

    assert isinstance(transaction, MetadataMessage)
    assert len(transaction.reports) == 1


def test_get_transaction_with_invalid_content(respx_mock) -> None:
    respx_mock.get(
        "https://registry.sdmx.org/ws/registry/transactions/invalid"
    ).mock(return_value=httpx.Response(200, content=b"not an SDMX message"))
    client = RegistryTransactionsClient("https://registry.sdmx.org")

    with pytest.raises(InternalError, match="Unexpected transaction format"):
        client.get_transaction("invalid")


def test_get_transaction_with_unsupported_schema(respx_mock) -> None:
    respx_mock.get(
        "https://registry.sdmx.org/ws/registry/transactions/unknown"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "meta": {
                    "schema": "https://json.sdmx.org/2.1/"
                    "sdmx-json-data-schema.json"
                }
            },
        )
    )
    client = RegistryTransactionsClient("https://registry.sdmx.org")

    with pytest.raises(InternalError, match="Unexpected transaction format"):
        client.get_transaction("unknown")


def test_get_transaction_with_unexpected_message(mocker, respx_mock) -> None:
    respx_mock.get(
        "https://registry.sdmx.org/ws/registry/transactions/unexpected"
    ).mock(return_value=httpx.Response(200, content=b"{}"))
    mocker.patch("pysdmx.io.reader.read_sdmx", return_value=Message())
    client = RegistryTransactionsClient("https://registry.sdmx.org")

    with pytest.raises(InternalError, match="Unexpected transaction format"):
        client.get_transaction("unexpected")

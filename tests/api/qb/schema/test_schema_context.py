from pysdmx.api.qb.schema import SchemaContext


def test_expected_formats():
    expected = [
        "datastructure",
        "metadatastructure",
        "dataflow",
        "metadataflow",
        "provisionagreement",
        "metadataprovisionagreement",
    ]

    assert len(SchemaContext) == len(expected)
    for fmt in SchemaContext:
        assert fmt.value in expected

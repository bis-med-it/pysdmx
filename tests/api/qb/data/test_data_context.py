from pysdmx.api.qb.data import DataContext


def test_expected_contexts():
    expected = [
        "datastructure",
        "dataflow",
        "provisionagreement",
    ]

    assert len(DataContext) == len(expected)
    for fmt in DataContext:
        assert fmt.value in expected

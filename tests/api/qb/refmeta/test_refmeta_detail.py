from pysdmx.api.qb.refmeta import RefMetaDetail


def test_expected_details():
    expected = ["full", "allstubs"]

    assert len(RefMetaDetail) == len(expected)
    for d in RefMetaDetail:
        assert d.value in expected

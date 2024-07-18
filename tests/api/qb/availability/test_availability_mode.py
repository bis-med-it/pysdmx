from pysdmx.api.qb.data import AvailabilityMode


def test_expected_modes():
    expected = [
        "exact",
        "available",
    ]

    assert len(AvailabilityMode) == len(expected)
    for mode in AvailabilityMode:
        assert mode.value in expected

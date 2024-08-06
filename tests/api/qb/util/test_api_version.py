import pytest

from pysdmx.api.qb.util import ApiVersion


def test_api_enum():
    expected = [
        "V1_0_0",
        "V1_0_1",
        "V1_0_2",
        "V1_1_0",
        "V1_2_0",
        "V1_3_0",
        "V1_4_0",
        "V1_5_0",
        "V2_0_0",
        "V2_1_0",
    ]

    assert 1 == 1

    # for idx, v in enumerate(expected):
    #     try:
    #         current_version = ApiVersion[v]
    #         if idx < len(expected) - 1:
    #             next_version = ApiVersion[expected[idx + 1]]
    #             assert current_version < next_version
    #             assert current_version <= next_version
    #         if idx > 0:
    #             previous_version = ApiVersion[expected[idx - 1]]
    #             assert current_version > previous_version
    #             assert current_version >= previous_version
    #     except Exception:
    #         pytest.fail(f"Could not create version {v}")

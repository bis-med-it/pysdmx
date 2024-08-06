from pysdmx.api.qb.util import ApiVersion


def test_api_enum():
    expected = [
        "V1.0.0",
        "V1.0.1",
        "V1.0.2",
        "V1.1.0",
        "V1.2.0",
        "V1.3.0",
        "V1.4.0",
        "V1.5.0",
        "V2.0.0",
        "V2.1.0",
    ]

    assert len(ApiVersion) == 10
    for v in list(ApiVersion):
        assert v.value in expected


# def test_api_enum_comparisons():
#     expected = [
#         "V1.0.0",
#         "V1.0.1",
#         "V1.0.2",
#         "V1.1.0",
#         "V1.2.0",
#         "V1.3.0",
#         "V1.4.0",
#         "V1.5.0",
#         "V2.0.0",
#         "V2.1.0",
#     ]

#     assert len(ApiVersion) == 10
#     prev = None
#     for v in ApiVersion:
#         assert v.value in expected
#         if prev is not None:
#             assert v > prev
#             assert v >= prev
#             assert v >= v
#             assert v == v
#             assert prev < v
#             assert prev <= v

#         prev = v

from datetime import datetime, timezone

from pysdmx.io.json.fusion.messages.code import FusionCode
from pysdmx.io.json.fusion.messages.core import FusionAnnotation, FusionString


def test_code_validity_period_without_timezone_is_assumed_utc():
    vp = FusionAnnotation(
        type="FR_VALIDITY_PERIOD", title="/2020-01-01T00:00:00"
    )
    code = FusionCode(
        id="A",
        names=[FusionString(locale="en", value="Annual")],
        annotations=[vp],
    )

    out = code.to_model()

    assert out.valid_from is None
    assert out.valid_to == datetime(2020, 1, 1, tzinfo=timezone.utc)

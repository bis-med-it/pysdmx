from pysdmx.io.json.sdmxjson2.messages.concept import JsonConcept
from pysdmx.io.json.sdmxjson2.messages.core import (
    JsonRepresentation,
    JsonTextFormat,
)
from pysdmx.model import DataType


def test_dt_from_enum():
    f = JsonTextFormat(textType="Short")
    r = JsonRepresentation(enumerationFormat=f)
    c = JsonConcept(id="TEST", coreRepresentation=r)

    concept = c.to_model([])

    assert concept.dtype == DataType.SHORT


def test_dt_from_format():
    f = JsonTextFormat(textType="Alpha")
    r = JsonRepresentation(format=f)
    c = JsonConcept(id="TEST", coreRepresentation=r)

    concept = c.to_model([])

    assert concept.dtype == DataType.ALPHA


def test_dt_from_default():
    r = JsonRepresentation(minOccurs=0)
    c = JsonConcept(id="TEST", coreRepresentation=r)

    concept = c.to_model([])

    assert concept.dtype == DataType.STRING

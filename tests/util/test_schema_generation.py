import pytest

from pysdmx.errors import Invalid
from pysdmx.model import Codelist, Dataflow
from pysdmx.model.message import Message
from pysdmx.util import parse_short_urn, parse_urn
from pysdmx.util._model_utils import schema_generator


def test_schema_generation_pa():
    with pytest.raises(
        NotImplementedError,
        match="ProvisionAgreement schema generation is not supported",
    ):
        schema_generator(
            Message(),
            parse_urn("ProvisionAgreement=MD:TEST_DF(1.0)"),
        )


def test_schema_generation_invalid_reference():
    codelist = Codelist(id="test_codelist", agency="MD", version="1.0")
    message = Message(structures=[codelist])
    invalid_ref = parse_short_urn(codelist.short_urn)

    with pytest.raises(
        Invalid,
        match="can only reference a ",
    ):
        schema_generator(message, invalid_ref)


def test_schema_generation_dataflow_no_structure():
    dataflow = Dataflow(id="TEST_DF", agency="MD", version="1.0")
    message = Message(structures=[dataflow])
    dataflow_ref = parse_short_urn(dataflow.short_urn)
    with pytest.raises(
        Invalid,
        match="does not have a structure defined",
    ):
        schema_generator(message, dataflow_ref)

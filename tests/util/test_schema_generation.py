import re

import pytest

from pysdmx.errors import Invalid
from pysdmx.model import Codelist, Dataflow, ProvisionAgreement
from pysdmx.model.message import Message
from pysdmx.util import parse_short_urn, parse_urn
from pysdmx.util._model_utils import schema_generator


def test_schema_generation_pa():
    with pytest.raises(
        Invalid,
        match=re.escape(
            "Missing Provision Agreement ProvisionAgreement=MD:TEST_DF(1.0)"
            " in structures message."
        ),
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


def test_schema_generation_prov_agre_no_dataflow():
    dataflow = Dataflow(id="TEST_DF", agency="MD", version="1.0")
    prov_agree = ProvisionAgreement(
        provider="DataProvider=MD:DATA_PROVIDERS(1.0).MD",
        dataflow="Dataflow=MD:TEST(1.0)",
        id="TEST_PA",
        agency="MD",
        version="1.0",
    )
    message = Message(structures=[prov_agree, dataflow])
    prov_agree_ref = parse_short_urn(prov_agree.short_urn)
    with pytest.raises(
        Invalid,
        match=re.escape(
            "Missing Dataflow in ProvisionAgreement=MD:TEST_PA(1.0)"
            " structures message."
        ),
    ):
        schema_generator(message, prov_agree_ref)


def test_schema_generation_prov_agre_dfw_no_structure():
    dataflow = Dataflow(id="TEST_DF", agency="MD", version="1.0")
    prov_agree = ProvisionAgreement(
        provider="DataProvider=MD:DATA_PROVIDERS(1.0).MD",
        dataflow="Dataflow=MD:TEST_DF(1.0)",
        id="TEST_PA",
        agency="MD",
        version="1.0",
    )
    message = Message(structures=[prov_agree, dataflow])
    prov_agree_ref = parse_short_urn(prov_agree.short_urn)
    with pytest.raises(
        Invalid,
        match=re.escape(
            "Dataflow ProvisionAgreement=MD:TEST_PA(1.0) "
            "does not have a structure defined."
        ),
    ):
        schema_generator(message, prov_agree_ref)


def test_schema_generation_prov_agre_dfw_missing_structure():
    dataflow = Dataflow(
        id="TEST_DF",
        agency="MD",
        version="1.0",
        structure="DataStructure=MD:MISSING_DSD(1.0)",
    )
    prov_agree = ProvisionAgreement(
        provider="DataProvider=MD:DATA_PROVIDERS(1.0).MD",
        dataflow="Dataflow=MD:TEST_DF(1.0)",
        id="TEST_PA",
        agency="MD",
        version="1.0",
    )
    message = Message(structures=[prov_agree, dataflow])
    prov_agree_ref = parse_short_urn(prov_agree.short_urn)
    with pytest.raises(
        Invalid,
        match=re.escape(
            "Not found referenced DataStructure "
            "DataStructure=MD:MISSING_DSD(1.0) from Provision "
            "Agreement ProvisionAgreement=MD:TEST_PA(1.0)."
        ),
    ):
        schema_generator(message, prov_agree_ref)

import pytest

from pysdmx.io.json.sdmxjson2.messages.agency import JsonAgencyScheme
from pysdmx.io.json.sdmxjson2.messages.category import (
    JsonCategorisation,
    JsonCategoryScheme,
)
from pysdmx.io.json.sdmxjson2.messages.code import (
    JsonCodelist,
    JsonHierarchy,
    JsonHierarchyAssociation,
    JsonValuelist,
)
from pysdmx.io.json.sdmxjson2.messages.concept import JsonConceptScheme
from pysdmx.io.json.sdmxjson2.messages.constraint import JsonDataConstraint
from pysdmx.io.json.sdmxjson2.messages.consumer import (
    JsonDataConsumerScheme,
)
from pysdmx.io.json.sdmxjson2.messages.core import JsonLink
from pysdmx.io.json.sdmxjson2.messages.dataflow import JsonDataflow
from pysdmx.io.json.sdmxjson2.messages.dsd import (
    JsonComponents,
    JsonDataStructure,
    JsonDimensions,
)
from pysdmx.io.json.sdmxjson2.messages.map import (
    JsonRepresentationMap,
    JsonStructureMap,
)
from pysdmx.io.json.sdmxjson2.messages.metadataflow import JsonMetadataflow
from pysdmx.io.json.sdmxjson2.messages.mpa import (
    JsonMetadataProvisionAgreement,
)
from pysdmx.io.json.sdmxjson2.messages.msd import (
    JsonMetadataComponents,
    JsonMetadataStructure,
)
from pysdmx.io.json.sdmxjson2.messages.pa import JsonProvisionAgreement
from pysdmx.io.json.sdmxjson2.messages.provider import (
    JsonDataProviderScheme,
    JsonMetadataProviderScheme,
)
from pysdmx.io.json.sdmxjson2.messages.report import JsonMetadataReport
from pysdmx.io.json.sdmxjson2.messages.vtl import (
    JsonCustomTypeScheme,
    JsonNamePersonalisationScheme,
    JsonRulesetScheme,
    JsonTransformationScheme,
    JsonUserDefinedOperatorScheme,
    JsonVtlMappingScheme,
)

_STUB_URL = "https://example.test/structure/TEST/STUB/1.0"


@pytest.mark.parametrize(
    (
        "json_type",
        "to_model_args",
        "extra_fields",
        "artefact_id",
        "artefact_name",
    ),
    [
        pytest.param(
            JsonAgencyScheme,
            ((),),
            {},
            "AGENCIES",
            "AGENCIES",
            id="agency-scheme",
        ),
        pytest.param(
            JsonCategorisation,
            (),
            {},
            "STUB",
            "Stub artefact",
            id="categorisation",
        ),
        pytest.param(
            JsonCategoryScheme,
            (),
            {},
            "STUB",
            "Stub artefact",
            id="category-scheme",
        ),
        pytest.param(
            JsonCodelist, (), {}, "STUB", "Stub artefact", id="codelist"
        ),
        pytest.param(
            JsonHierarchy, ((),), {}, "STUB", "Stub artefact", id="hierarchy"
        ),
        pytest.param(
            JsonHierarchyAssociation,
            ((), ()),
            {},
            "STUB",
            "Stub artefact",
            id="hierarchy-association",
        ),
        pytest.param(
            JsonValuelist, (), {}, "STUB", "Stub artefact", id="valuelist"
        ),
        pytest.param(
            JsonConceptScheme,
            ((),),
            {},
            "STUB",
            "Stub artefact",
            id="concept-scheme",
        ),
        pytest.param(
            JsonDataConstraint,
            (),
            {},
            "STUB",
            "Stub artefact",
            id="data-constraint",
        ),
        pytest.param(
            JsonDataConsumerScheme,
            (),
            {},
            "DATA_CONSUMERS",
            "DATA_CONSUMERS",
            id="data-consumer-scheme",
        ),
        pytest.param(
            JsonDataflow, (), {}, "STUB", "Stub artefact", id="dataflow"
        ),
        pytest.param(
            JsonDataStructure,
            ((), (), (), ()),
            {"dataStructureComponents": JsonComponents(JsonDimensions())},
            "STUB",
            "Stub artefact",
            id="data-structure",
        ),
        pytest.param(
            JsonRepresentationMap,
            (),
            {},
            "STUB",
            "Stub artefact",
            id="representation-map",
        ),
        pytest.param(
            JsonStructureMap,
            ((),),
            {},
            "STUB",
            "Stub artefact",
            id="structure-map",
        ),
        pytest.param(
            JsonMetadataflow,
            (),
            {},
            "STUB",
            "Stub artefact",
            id="metadataflow",
        ),
        pytest.param(
            JsonMetadataProvisionAgreement,
            (),
            {},
            "STUB",
            "Stub artefact",
            id="metadata-provision-agreement",
        ),
        pytest.param(
            JsonMetadataStructure,
            ((), (), ()),
            {"metadataStructureComponents": JsonMetadataComponents()},
            "STUB",
            "Stub artefact",
            id="metadata-structure",
        ),
        pytest.param(
            JsonProvisionAgreement,
            (),
            {},
            "STUB",
            "Stub artefact",
            id="provision-agreement",
        ),
        pytest.param(
            JsonDataProviderScheme,
            ((),),
            {},
            "DATA_PROVIDERS",
            "DATA_PROVIDERS",
            id="data-provider-scheme",
        ),
        pytest.param(
            JsonMetadataProviderScheme,
            ((),),
            {},
            "METADATA_PROVIDERS",
            "METADATA_PROVIDERS",
            id="metadata-provider-scheme",
        ),
        pytest.param(
            JsonMetadataReport,
            (),
            {},
            "STUB",
            "Stub artefact",
            id="metadata-report",
        ),
        pytest.param(
            JsonCustomTypeScheme,
            (),
            {"vtlVersion": "1.0"},
            "STUB",
            "Stub artefact",
            id="custom-type-scheme",
        ),
        pytest.param(
            JsonNamePersonalisationScheme,
            (),
            {"vtlVersion": "1.0"},
            "STUB",
            "Stub artefact",
            id="name-personalisation-scheme",
        ),
        pytest.param(
            JsonRulesetScheme,
            (),
            {"vtlVersion": "1.0"},
            "STUB",
            "Stub artefact",
            id="ruleset-scheme",
        ),
        pytest.param(
            JsonTransformationScheme,
            ((), (), (), (), ()),
            {},
            "STUB",
            "Stub artefact",
            id="transformation-scheme",
        ),
        pytest.param(
            JsonUserDefinedOperatorScheme,
            (),
            {"vtlVersion": "1.0"},
            "STUB",
            "Stub artefact",
            id="user-defined-operator-scheme",
        ),
        pytest.param(
            JsonVtlMappingScheme,
            (),
            {},
            "STUB",
            "Stub artefact",
            id="vtl-mapping-scheme",
        ),
    ],
)
def test_stub(
    json_type,
    to_model_args,
    extra_fields,
    artefact_id,
    artefact_name,
):
    stub = json_type(
        agency="TEST",
        id=artefact_id,
        name=artefact_name,
        version="1.0",
        isExternalReference=True,
        links=(JsonLink(rel="self", href=_STUB_URL),),
        **extra_fields,
    )

    artefact = stub.to_model(*to_model_args)

    assert artefact.agency == "TEST"
    assert artefact.id == artefact_id
    assert artefact.name == artefact_name
    assert artefact.version == "1.0"
    assert artefact.is_external_reference is True
    assert artefact.structure_url == _STUB_URL

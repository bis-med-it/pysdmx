import pytest

from pysdmx.errors import Invalid
from pysdmx.model import (
    Dataflow,
    ItemReference,
    ProvisionAgreement,
    Reference,
)
from pysdmx.model.vtl import (
    QueryExtraction,
    QueryParameter,
    TransformationScheme,
    UrlExtraction,
    VtlDataExtraction,
    VtlExecution,
)

BASE = "urn:sdmx:org.sdmx.infomodel."
DF_URN = f"{BASE}datastructure.Dataflow=AG:DF(1.0)"
PA_URN = f"{BASE}registry.ProvisionAgreement=AG:PA(1.0)"
TS_URN = f"{BASE}transformation.TransformationScheme=AG:TS(1.0)"
DS_A = f"{BASE}transformation.VtlDatasetMapping=AG:VMS(1.0).DS_A"
DS_B = f"{BASE}transformation.VtlDatasetMapping=AG:VMS(1.0).DS_B"
CL_A = f"{BASE}transformation.VtlCodelistMapping=AG:VMS(1.0).CL_A"


@pytest.fixture
def query():
    return QueryExtraction(
        dataset_mapping=DS_A,
        entry_point="https://sdmx.example.org/rest",
        sdmx_api_version="2.1",
        parameters=[
            QueryParameter(name="key", value="*.M.*", is_fixed=True),
            QueryParameter(name="c[TIME_PERIOD]", is_fixed=False),
        ],
    )


@pytest.fixture
def url():
    return UrlExtraction(
        dataset_mapping=DS_B,
        url_template="https://example.org/data/{flow}?from={startPeriod}",
    )


def test_fixed_parameter():
    param = QueryParameter(name="key", value="*.M.*", is_fixed=True)

    assert param.name == "key"
    assert param.value == "*.M.*"
    assert param.is_fixed is True


def test_non_fixed_parameter_may_have_no_value():
    param = QueryParameter(name="startPeriod", is_fixed=False)

    assert param.value is None
    assert param.is_fixed is False


def test_fixed_parameter_needs_a_value():
    with pytest.raises(Invalid, match="fixed parameter must have a value"):
        QueryParameter(name="key", is_fixed=True)


@pytest.mark.parametrize("name", ["", "start period", "start\tperiod"])
def test_invalid_parameter_name(name):
    with pytest.raises(Invalid, match="name"):
        QueryParameter(name=name, is_fixed=False)


def test_query_extraction(query):
    assert query.dataset_mapping == DS_A
    assert query.entry_point == "https://sdmx.example.org/rest"
    assert query.sdmx_api_version == "2.1"
    assert [p.name for p in query.parameters] == ["key", "c[TIME_PERIOD]"]
    assert query.context is None
    assert query.context_urn is None
    assert isinstance(query, VtlDataExtraction)


@pytest.mark.parametrize(
    ("context", "urn"),
    [
        (DF_URN, DF_URN),
        (Reference("Dataflow", "AG", "DF", "1.0"), DF_URN),
        (Dataflow(id="DF", agency="AG"), DF_URN),
        (PA_URN, PA_URN),
        (
            ProvisionAgreement(
                id="PA", agency="AG", dataflow=DF_URN, provider="P"
            ),
            PA_URN,
        ),
    ],
)
def test_query_extraction_context(context, urn):
    query = QueryExtraction(
        dataset_mapping=DS_A, entry_point="https://x.org", context=context
    )

    assert query.context == context
    assert query.context_urn == urn


@pytest.mark.parametrize(
    "context",
    [
        f"{BASE}datastructure.DataStructure=AG:DSD(1.0)",
        Reference("DataStructure", "AG", "DSD", "1.0"),
        "not a urn",
    ],
)
def test_query_extraction_invalid_context(context):
    with pytest.raises(Invalid, match="Dataflow or Provision Agreement"):
        QueryExtraction(
            dataset_mapping=DS_A, entry_point="https://x.org", context=context
        )


def test_query_extraction_needs_an_entry_point():
    with pytest.raises(Invalid, match="entry point"):
        QueryExtraction(dataset_mapping=DS_A, entry_point="")


@pytest.mark.parametrize("version", ["v2.1", "2", "2.1.0", "02.1"])
def test_query_extraction_invalid_api_version(version):
    with pytest.raises(Invalid, match="major.minor"):
        QueryExtraction(
            dataset_mapping=DS_A,
            entry_point="https://x.org",
            sdmx_api_version=version,
        )


def test_dataset_mapping_as_reference():
    ref = ItemReference("VtlDatasetMapping", "AG", "VMS", "1.0", "DS_A")

    query = QueryExtraction(dataset_mapping=ref, entry_point="https://x.org")

    assert query.dataset_mapping == ref
    assert query.dataset_mapping_urn == DS_A


@pytest.mark.parametrize(
    "mapping",
    [
        CL_A,
        ItemReference("VtlCodelistMapping", "AG", "VMS", "1.0", "CL_A"),
        f"{BASE}transformation.VtlMappingScheme=AG:VMS(1.0)",
        "not a urn",
    ],
)
def test_extraction_needs_a_dataset_mapping(mapping):
    with pytest.raises(Invalid, match="VtlDatasetMapping"):
        UrlExtraction(dataset_mapping=mapping, url_template="https://x.org")


def test_parameter_names_are_unique_in_an_extraction():
    params = [
        QueryParameter(name="key", value="A", is_fixed=True),
        QueryParameter(name="key", value="B", is_fixed=False),
    ]

    with pytest.raises(Invalid, match="'key'"):
        QueryExtraction(
            dataset_mapping=DS_A,
            entry_point="https://x.org",
            parameters=params,
        )


def test_url_extraction(url):
    assert url.dataset_mapping == DS_B
    assert url.dataset_mapping_urn == DS_B
    assert url.url_template == (
        "https://example.org/data/{flow}?from={startPeriod}"
    )
    assert url.parameters == ()
    assert isinstance(url, VtlDataExtraction)


def test_url_extraction_needs_a_template():
    with pytest.raises(Invalid, match="URL template"):
        UrlExtraction(dataset_mapping=DS_A, url_template="")


@pytest.mark.parametrize(
    "scheme",
    [
        TS_URN,
        Reference("TransformationScheme", "AG", "TS", "1.0"),
        TransformationScheme(id="TS", agency="AG", vtl_version="2.2"),
    ],
)
def test_execution(scheme, query, url):
    execution = VtlExecution(
        id="EXEC",
        agency="AG",
        name="Execution",
        transformation_scheme=scheme,
        extractions=[query, url],
    )

    assert execution.id == "EXEC"
    assert execution.agency == "AG"
    assert execution.version == "1.0"
    assert execution.transformation_scheme == scheme
    assert execution.transformation_scheme_urn == TS_URN
    assert execution.extractions == [query, url]
    assert execution.short_urn == "VtlExecution=AG:EXEC(1.0)"


def test_execution_needs_an_agency(query):
    with pytest.raises(Invalid, match="agency"):
        VtlExecution(
            id="EXEC", transformation_scheme=TS_URN, extractions=[query]
        )


def test_execution_needs_an_extraction():
    with pytest.raises(Invalid, match="at least one data extraction"):
        VtlExecution(id="EXEC", agency="AG", transformation_scheme=TS_URN)


@pytest.mark.parametrize(
    "scheme",
    [
        f"{BASE}transformation.RulesetScheme=AG:RS(1.0)",
        Reference("RulesetScheme", "AG", "RS", "1.0"),
        "not a urn",
    ],
)
def test_execution_needs_a_transformation_scheme(scheme, query):
    with pytest.raises(Invalid, match="Transformation Scheme"):
        VtlExecution(
            id="EXEC",
            agency="AG",
            transformation_scheme=scheme,
            extractions=[query],
        )


def test_execution_has_one_extraction_per_dataset_mapping(query):
    ref = ItemReference("VtlDatasetMapping", "AG", "VMS", "1.0", "DS_A")
    other = UrlExtraction(dataset_mapping=ref, url_template="https://x.org")

    with pytest.raises(Invalid, match="at most one data extraction"):
        VtlExecution(
            id="EXEC",
            agency="AG",
            transformation_scheme=TS_URN,
            extractions=[query, other],
        )

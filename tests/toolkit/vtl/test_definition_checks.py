import pytest
from msgspec.structs import replace

from pysdmx.errors import Invalid
from pysdmx.model import (
    Components,
    Dataflow,
    DataStructureDefinition,
    ItemReference,
    ProvisionAgreement,
    QueryExtraction,
    Reference,
    Ruleset,
    RulesetScheme,
    Transformation,
    TransformationScheme,
    UrlExtraction,
    VtlCodelistMapping,
    VtlDataflowMapping,
    VtlDatasetMapping,
    VtlExecution,
    VtlMappingScheme,
)
from pysdmx.toolkit.vtl import model_validations

BASE = "urn:sdmx:org.sdmx.infomodel."
DSD = DataStructureDefinition(id="DSD", agency="AG", components=Components([]))
DF_A = Dataflow(id="DF_A", agency="AG", structure=DSD)
DF_SAME = Dataflow(
    id="DF_SAME", agency="AG", structure="DataStructure=AG:DSD(1.0)"
)
DF_OTHER = Dataflow(
    id="DF_OTHER",
    agency="AG",
    structure=f"{BASE}datastructure.DataStructure=AG:OTHER(1.0)",
)
DF_UNKNOWN = Dataflow(id="DF_UNKNOWN", agency="AG")
PA_SAME = ProvisionAgreement(
    id="PA_SAME",
    agency="AG",
    dataflow=f"{BASE}datastructure.Dataflow=AG:DF_SAME(1.0)",
    provider="P",
)
PA_LOST = ProvisionAgreement(
    id="PA_LOST",
    agency="AG",
    dataflow=f"{BASE}datastructure.Dataflow=AG:MISSING(1.0)",
    provider="P",
)
STRUCTURES = [DSD, DF_A, DF_SAME, DF_OTHER, DF_UNKNOWN, PA_SAME, PA_LOST]
VIRAL = """define viral propagation {name} ({scope} OBS_STATUS) is
    when "M" then "M";
    else "A"
    end viral propagation"""


def ref(cls, id_):
    return Reference(cls, "AG", id_, "1.0")


def mapping_ref(item, scheme="VMS"):
    return ItemReference("VtlDatasetMapping", "AG", scheme, "1.0", item)


def viral(name, scope="variable"):
    return Ruleset(
        id=name,
        name=name,
        ruleset_type="viral",
        ruleset_scope=scope,
        ruleset_definition=VIRAL.format(name=name, scope=scope),
    )


def ruleset_scheme(id_, *rulesets, version="2.2"):
    return RulesetScheme(
        id=id_, agency="AG", name=id_, vtl_version=version, items=rulesets
    )


@pytest.fixture
def mappings():
    return VtlMappingScheme(
        id="VMS",
        agency="AG",
        name="Mappings",
        items=[
            VtlDatasetMapping(
                id="DS_A",
                vtl_alias="ds_a",
                is_input=True,
                sdmx_artefact=ref("Dataflow", "DF_A"),
            ),
            VtlDatasetMapping(
                id="DS_R",
                vtl_alias="ds_r",
                is_input=False,
                sdmx_artefact=ref("Dataflow", "DF_R"),
            ),
            VtlCodelistMapping(
                id="CL", vtl_alias="cl", codelist=ref("Codelist", "CL")
            ),
        ],
    )


@pytest.fixture
def ts(mappings):
    return TransformationScheme(
        id="TS",
        agency="AG",
        name="Program",
        vtl_version="2.2",
        vtl_mapping_scheme=mappings,
        items=[
            Transformation(
                id="T1",
                name="T1",
                expression="ds_a + 1",
                result="ds_r",
                is_persistent=True,
            )
        ],
    )


def execution(scheme, *extractions, **kwargs):
    return VtlExecution(
        id="EXEC",
        agency="AG",
        name="Execution",
        transformation_scheme=scheme,
        extractions=extractions
        or [
            UrlExtraction(
                dataset_mapping=mapping_ref("DS_A"), url_template="u"
            )
        ],
        **kwargs,
    )


def query(context=None, item="DS_A"):
    return QueryExtraction(
        dataset_mapping=mapping_ref(item), entry_point="e", context=context
    )


def test_valid_definitions(ts, mappings):
    model_validations(mappings)
    model_validations(ts)
    model_validations(execution(ts))


@pytest.mark.parametrize("result", ["ds_r", "'ds_r'", " ds_r "])
def test_output_is_the_result_of_a_persistent_transformation(ts, result):
    transformation = replace(ts.items[0], result=result)

    model_validations(replace(ts, items=[transformation]))


@pytest.mark.parametrize(
    "changes", [{"is_persistent": False}, {"result": "other"}]
)
def test_output_without_persistent_transformation(ts, changes):
    invalid = replace(ts, items=[replace(ts.items[0], **changes)])

    with pytest.raises(Invalid, match="ds_r.*persistent"):
        model_validations(invalid)


def test_mapping_scheme_is_found_in_the_structures(ts, mappings):
    by_reference = replace(
        ts,
        vtl_mapping_scheme=ref("VtlMappingScheme", "VMS"),
        items=[replace(ts.items[0], is_persistent=False)],
    )

    model_validations(by_reference)
    with pytest.raises(Invalid, match="persistent"):
        model_validations(by_reference, [mappings])


def test_mapping_scheme_reference_has_the_right_class(ts):
    invalid = replace(ts, vtl_mapping_scheme=ref("RulesetScheme", "RS"))

    with pytest.raises(Invalid, match="VTL Mapping Scheme"):
        model_validations(invalid)


def test_one_viral_propagation_per_variable_or_value_domain(ts):
    schemes = [
        ruleset_scheme("RS1", viral("VP1")),
        ruleset_scheme("RS2", viral("VP2", "valuedomain")),
    ]
    model_validations(replace(ts, ruleset_schemes=schemes))
    schemes.append(ruleset_scheme("RS3", viral("VP3")))

    with pytest.raises(Invalid, match="variable OBS_STATUS"):
        model_validations(replace(ts, ruleset_schemes=schemes))


def test_schemes_have_the_vtl_version_of_the_transformation_scheme(ts):
    schemes = [ruleset_scheme("RS1", viral("VP1"), version="2.1")]

    with pytest.raises(Invalid, match="VTL version"):
        model_validations(replace(ts, ruleset_schemes=schemes))


def test_referenced_schemes_are_found_in_the_structures(ts):
    scheme = ruleset_scheme("RS1", viral("VP1"), version="2.1")
    by_reference = replace(ts, ruleset_schemes=[ref("RulesetScheme", "RS1")])

    model_validations(by_reference)
    with pytest.raises(Invalid, match="VTL version"):
        model_validations(by_reference, [scheme])


@pytest.mark.parametrize(
    ("mapping", "error"),
    [
        (VtlCodelistMapping(id="X", codelist=ref("Codelist", "CL")), "alias"),
        (
            VtlCodelistMapping(
                id="X", vtl_alias="a b", codelist=ref("Codelist", "CL")
            ),
            "alias",
        ),
        (VtlCodelistMapping(id="X", vtl_alias="x"), "codelist"),
        (
            VtlCodelistMapping(
                id="X", vtl_alias="x", codelist=ref("Dataflow", "DF")
            ),
            "codelist",
        ),
    ],
)
def test_invalid_mapping(mapping, error):
    scheme = VtlMappingScheme(
        id="VMS", agency="AG", name="Mappings", items=[mapping]
    )

    with pytest.raises(Invalid, match=error):
        model_validations(scheme)


def test_deprecated_mappings_are_valid():
    mapping = VtlDataflowMapping(
        id="OLD", dataflow=DF_A, dataflow_alias="urn or alias"
    )
    scheme = VtlMappingScheme(
        id="VMS", agency="AG", name="Mappings", items=[mapping]
    )

    model_validations(scheme)


@pytest.mark.parametrize(
    ("mapping", "error"),
    [
        (mapping_ref("DS_A", scheme="OTHER"), "executed program"),
        (mapping_ref("MISSING"), "executed program"),
        (mapping_ref("DS_R"), "only to the inputs"),
    ],
)
def test_extraction_applies_to_an_input_of_the_program(ts, mapping, error):
    extraction = UrlExtraction(dataset_mapping=mapping, url_template="u")

    with pytest.raises(Invalid, match=error):
        model_validations(execution(ts, extraction))


@pytest.mark.parametrize(
    "context",
    [DF_SAME, ref("Dataflow", "DF_SAME"), PA_SAME, DF_UNKNOWN, PA_LOST, None],
)
def test_context_with_the_data_structure_of_the_mapping(ts, context):
    model_validations(execution(ts, query(context)), STRUCTURES)


@pytest.mark.parametrize("context", [DF_OTHER, ref("Dataflow", "DF_OTHER")])
def test_context_with_another_data_structure(ts, context):
    with pytest.raises(Invalid, match="data structure"):
        model_validations(execution(ts, query(context)), STRUCTURES)


def test_context_is_not_checked_without_the_structures(ts):
    model_validations(execution(ts, query(ref("Dataflow", "DF_OTHER"))))


def test_mapping_to_a_data_structure(ts, mappings):
    ds_a = replace(mappings.items[0], sdmx_artefact=DSD)
    scheme = replace(ts, vtl_mapping_scheme=replace(mappings, items=[ds_a]))

    model_validations(execution(scheme, query(DF_SAME)), STRUCTURES)
    with pytest.raises(Invalid, match="data structure"):
        model_validations(execution(scheme, query(DF_OTHER)), STRUCTURES)


def test_transformation_scheme_is_found_in_the_structures(ts):
    urn = f"{BASE}transformation.TransformationScheme=AG:TS(1.0)"
    invalid = execution(
        urn,
        UrlExtraction(dataset_mapping=mapping_ref("DS_R"), url_template="u"),
    )

    model_validations(invalid)
    with pytest.raises(Invalid, match="only to the inputs"):
        model_validations(invalid, [ts])


def test_stub_is_valid():
    stub = VtlExecution(
        id="EXEC", agency="AG", name="Stub", is_external_reference=True
    )

    model_validations(stub)

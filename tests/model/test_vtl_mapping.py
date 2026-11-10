import pytest

from pysdmx.errors import Invalid
from pysdmx.model import (
    Codelist,
    Components,
    Concept,
    Dataflow,
    DataflowRef,
    DataStructureDefinition,
    ItemReference,
    ProvisionAgreement,
    Reference,
)
from pysdmx.model.vtl import (
    VtlCodelistMapping,
    VtlConceptMapping,
    VtlDataflowMapping,
    VtlDatasetMapping,
    VtlMapping,
    VtlMappingScheme,
)

BASE = "urn:sdmx:org.sdmx.infomodel."
DF_URN = f"{BASE}datastructure.Dataflow=AG:DF(1.0)"
DSD_URN = f"{BASE}datastructure.DataStructure=AG:DSD(1.0)"
PA_URN = f"{BASE}registry.ProvisionAgreement=AG:PA(1.0)"
CL_URN = f"{BASE}codelist.Codelist=AG:CL(1.0)"
CON_URN = f"{BASE}conceptscheme.Concept=AG:CS(1.0).C1"
DF_REF = DataflowRef(agency="AG", id="DF")

LEGACY = [
    (VtlCodelistMapping, "codelist_alias", {"codelist": CL_URN}),
    (VtlConceptMapping, "concept_alias", {"concept": CON_URN}),
    (VtlDataflowMapping, "dataflow_alias", {"dataflow": DF_REF}),
]


@pytest.mark.parametrize(("cls", "deprecated", "kwargs"), LEGACY)
def test_vtl_alias_is_taken_from_deprecated_alias(cls, deprecated, kwargs):
    mapping = cls(id="M", **{deprecated: "alias"}, **kwargs)

    assert mapping.vtl_alias == "alias"
    assert getattr(mapping, deprecated) == "alias"


@pytest.mark.parametrize(("cls", "deprecated", "kwargs"), LEGACY)
def test_deprecated_alias_is_taken_from_vtl_alias(cls, deprecated, kwargs):
    mapping = cls(id="M", vtl_alias="alias", **kwargs)

    assert mapping.vtl_alias == "alias"
    assert getattr(mapping, deprecated) == "alias"


@pytest.mark.parametrize(("cls", "deprecated", "kwargs"), LEGACY)
def test_aliases_must_have_the_same_value(cls, deprecated, kwargs):
    with pytest.raises(Invalid, match="must have the same value"):
        cls(id="M", vtl_alias="new", **{deprecated: "old"}, **kwargs)


def test_dataflow_mapping_needs_an_alias():
    with pytest.raises(Invalid, match="alias"):
        VtlDataflowMapping(id="M", dataflow=DF_REF)


def test_mapping_without_artefact_has_no_urn():
    assert VtlMapping(id="M").sdmx_urn is None
    assert VtlCodelistMapping(id="M").sdmx_urn is None


@pytest.mark.parametrize(
    "codelist",
    [
        CL_URN,
        Reference("Codelist", "AG", "CL", "1.0"),
        Codelist(id="CL", agency="AG"),
    ],
)
def test_codelist_mapping_urn(codelist):
    mapping = VtlCodelistMapping(id="M", codelist=codelist, vtl_alias="cl")

    assert mapping.sdmx_urn == CL_URN


def test_valuelist_mapping_urn():
    vl = Codelist(id="VL", agency="AG", sdmx_type="valuelist")

    mapping = VtlCodelistMapping(id="M", codelist=vl, vtl_alias="vl")

    assert mapping.sdmx_urn == f"{BASE}codelist.ValueList=AG:VL(1.0)"


def test_urn_of_reference_to_unknown_class_is_not_derived():
    ref = Reference("Unknown", "AG", "X", "1.0")

    assert VtlCodelistMapping(id="M", codelist=ref).sdmx_urn is None


@pytest.mark.parametrize("dataflow", [DF_REF, Dataflow(id="DF", agency="AG")])
def test_dataflow_mapping_urn(dataflow):
    mapping = VtlDataflowMapping(id="M", dataflow=dataflow, vtl_alias="df")

    assert mapping.sdmx_urn == DF_URN


@pytest.mark.parametrize(
    "concept",
    [
        CON_URN,
        ItemReference("Concept", "AG", "CS", "1.0", "C1"),
        Concept(id="C1", urn=CON_URN),
    ],
)
def test_concept_mapping_urn(concept):
    mapping = VtlConceptMapping(id="M", concept=concept, vtl_alias="c1")

    assert mapping.sdmx_urn == CON_URN


def test_concept_without_urn_has_no_urn():
    mapping = VtlConceptMapping(id="M", concept=Concept(id="C1"))

    assert mapping.sdmx_urn is None


@pytest.mark.parametrize(
    ("artefact", "urn"),
    [
        (DF_URN, DF_URN),
        (Reference("Dataflow", "AG", "DF", "1.0"), DF_URN),
        (Dataflow(id="DF", agency="AG"), DF_URN),
        (DSD_URN, DSD_URN),
        (Reference("DataStructure", "AG", "DSD", "1.0"), DSD_URN),
        (
            DataStructureDefinition(
                id="DSD", agency="AG", components=Components([])
            ),
            DSD_URN,
        ),
        (PA_URN, PA_URN),
        (Reference("ProvisionAgreement", "AG", "PA", "1.0"), PA_URN),
        (
            ProvisionAgreement(
                id="PA", agency="AG", dataflow=DF_URN, provider="P"
            ),
            PA_URN,
        ),
    ],
)
def test_dataset_mapping(artefact, urn):
    mapping = VtlDatasetMapping(
        id="DS", vtl_alias="ds", sdmx_artefact=artefact, is_input=True
    )

    assert mapping.id == "DS"
    assert mapping.vtl_alias == "ds"
    assert mapping.sdmx_artefact == artefact
    assert mapping.is_input is True
    assert mapping.sdmx_urn == urn


def test_dataset_mapping_needs_is_input():
    with pytest.raises(TypeError, match="is_input"):
        VtlDatasetMapping(id="DS", vtl_alias="ds", sdmx_artefact=DF_URN)


@pytest.mark.parametrize("alias", ["", "my ds", "'ds'", "d" * 129])
def test_dataset_mapping_invalid_alias(alias):
    with pytest.raises(Invalid, match="VTL alias"):
        VtlDatasetMapping(
            id="DS", vtl_alias=alias, sdmx_artefact=DF_URN, is_input=True
        )


@pytest.mark.parametrize(
    "artefact",
    [
        CL_URN,
        "Dataflow=AG:DF(1.0)",
        "not a urn",
        Reference("Codelist", "AG", "CL", "1.0"),
        Codelist(id="CL", agency="AG"),
    ],
)
def test_dataset_mapping_invalid_artefact(artefact):
    with pytest.raises(Invalid, match="Data Structure Definition, Dataflow"):
        VtlDatasetMapping(
            id="DS", vtl_alias="ds", sdmx_artefact=artefact, is_input=False
        )


def test_mapping_scheme():
    ds = VtlDatasetMapping(
        id="DS", vtl_alias="ds", sdmx_artefact=DF_URN, is_input=True
    )
    cl = VtlCodelistMapping(id="CL", vtl_alias="cl", codelist=CL_URN)

    scheme = VtlMappingScheme(id="VMS", agency="AG", items=[ds, cl])

    assert scheme.items == [ds, cl]
    assert scheme.short_urn == "VtlMappingScheme=AG:VMS(1.0)"


def test_mapping_scheme_aliases_are_unique():
    ds = VtlDatasetMapping(
        id="DS", vtl_alias="same", sdmx_artefact=DF_URN, is_input=True
    )
    cl = VtlCodelistMapping(id="CL", vtl_alias="same", codelist=CL_URN)

    with pytest.raises(Invalid, match="'same'"):
        VtlMappingScheme(id="VMS", agency="AG", items=[ds, cl])


def test_mapping_scheme_accepts_mappings_without_alias():
    items = [VtlCodelistMapping(id="A"), VtlCodelistMapping(id="B")]

    scheme = VtlMappingScheme(id="VMS", agency="AG", items=items)

    assert len(scheme.items) == 2


def test_mapping_scheme_needs_an_agency():
    with pytest.raises(Invalid, match="agency"):
        VtlMappingScheme(id="VMS")

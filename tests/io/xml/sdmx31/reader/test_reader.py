from datetime import datetime
from pathlib import Path

import pytest

from pysdmx.errors import Invalid
from pysdmx.io.format import Format
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.reader import read_sdmx
from pysdmx.io.xml.sdmx31.reader.structure import read as read_structure
from pysdmx.model import (
    AvailabilityConstraint,
    Categorisation,
    CategoryScheme,
    Codelist,
    ConceptScheme,
    DataConsumer,
    DataConsumerScheme,
    DataflowRef,
    DataProvider,
    DataProviderScheme,
    Hierarchy,
    HierarchyAssociation,
    Metadataflow,
    MetadataProvider,
    MetadataProviderScheme,
    MetadataProvisionAgreement,
    MetadataStructure,
    NamePersonalisationScheme,
    Reference,
    RulesetScheme,
    TransformationScheme,
    VtlMappingScheme,
)
from pysdmx.model.dataflow import (
    Dataflow,
    DataStructureDefinition,
    ProvisionAgreement,
)


@pytest.fixture
def samples_folder():
    return Path(__file__).parent / "samples"


@pytest.mark.xml
def test_codelist_31(samples_folder):
    data_path = samples_folder / "codelist.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_sdmx(input_str, validate=True).structures
    codelist = result[0]
    assert isinstance(codelist, Codelist)
    assert codelist.id == "CL_AGE"
    assert codelist.agency == "SDMX"
    assert len(codelist.items) == 5


@pytest.mark.xml
def test_org_schemes_31(samples_folder):
    data_path = samples_folder / "org_schemes.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_structure(input_str, validate=True)

    by_type = {type(s): s for s in result}
    assert set(by_type) == {
        DataProviderScheme,
        DataConsumerScheme,
        MetadataProviderScheme,
    }

    dps = by_type[DataProviderScheme]
    provider = dps.items[0]
    assert isinstance(provider, DataProvider)
    assert provider.id == "DP"
    assert provider.contacts[0].emails == ["dp.test@md.org"]

    assert isinstance(by_type[DataConsumerScheme].items[0], DataConsumer)
    assert isinstance(
        by_type[MetadataProviderScheme].items[0], MetadataProvider
    )


@pytest.mark.xml
def test_provider_scheme_enrichment_31(samples_folder):
    data_path = samples_folder / "provider_scheme_enrichment.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_structure(input_str, validate=True)

    schemes = [s for s in result if isinstance(s, DataProviderScheme)]
    assert len(schemes) == 1
    provider = schemes[0].items[0]
    assert provider.id == "MD"
    assert provider.dataflows == [
        DataflowRef(id="TEST", agency="MD", version="1.0")
    ]


@pytest.mark.xml
def test_metadata_provider_scheme_enrichment_31(samples_folder):
    data_path = samples_folder / "metadata_provider_scheme_enrichment.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_structure(input_str, validate=True)

    mpas = [s for s in result if isinstance(s, MetadataProvisionAgreement)]
    assert len(mpas) == 1
    assert mpas[0].metadataflow == (
        "urn:sdmx:org.sdmx.infomodel.metadatastructure."
        "Metadataflow=MD:MDF_TEST(1.0)"
    )
    assert mpas[0].metadata_provider == (
        "urn:sdmx:org.sdmx.infomodel.base."
        "MetadataProvider=MD:METADATA_PROVIDERS(1.0).MP1"
    )

    schemes = [s for s in result if isinstance(s, MetadataProviderScheme)]
    assert len(schemes) == 1
    providers = {p.id: p for p in schemes[0].items}
    assert providers["MP1"].dataflows == [
        DataflowRef(id="MDF_TEST", agency="MD", version="1.0")
    ]
    assert providers["MP2"].dataflows == []


@pytest.mark.xml
def test_hierarchy_31(samples_folder):
    data_path = samples_folder / "hierarchy.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_sdmx(input_str, validate=True).structures
    hierarchy = result[0]
    assert isinstance(hierarchy, Hierarchy)
    assert hierarchy.id == "H1"
    assert hierarchy.agency == "BIS"
    assert hierarchy.version == "1.0"
    assert hierarchy.name == "Hierarchy 1"
    assert hierarchy.description == "A test hierarchy"
    assert hierarchy.has_formal_levels is False
    assert hierarchy.level is None
    assert len(hierarchy.codes) == 2

    code_a = hierarchy.codes[0]
    assert code_a.id == "A"
    assert (
        code_a.urn
        == "urn:sdmx:org.sdmx.infomodel.codelist.Code=BIS:CL_FREQ(1.0).A"
    )
    assert code_a.level is None
    assert len(code_a.codes) == 1
    assert code_a.codes[0].id == "A1"
    assert (
        code_a.codes[0].urn
        == "urn:sdmx:org.sdmx.infomodel.codelist.Code=BIS:CL_FREQ(1.0).M"
    )

    code_b = hierarchy.codes[1]
    assert code_b.id == "B"
    assert code_b.rel_valid_from == datetime(2021, 1, 1)
    assert code_b.rel_valid_to == datetime(2021, 12, 31)
    assert not code_b.codes


@pytest.mark.xml
def test_hierarchy_levels_31(samples_folder):
    data_path = samples_folder / "hierarchy_levels.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_sdmx(input_str, validate=True).structures
    hierarchy = result[0]
    assert isinstance(hierarchy, Hierarchy)
    assert hierarchy.id == "H2"
    assert hierarchy.has_formal_levels is True
    assert hierarchy.level is not None
    assert hierarchy.level.id == "0"
    assert hierarchy.level.name == "Division"
    assert hierarchy.level.description == "Top level"
    assert hierarchy.level.level is not None
    assert hierarchy.level.level.id == "1"
    assert hierarchy.level.level.name == "Group"
    assert hierarchy.level.level.description is None
    assert hierarchy.level.level.level is None
    assert hierarchy.codes[0].id == "A"
    assert hierarchy.codes[0].level == "1"
    assert hierarchy.codes[1].id == "B"
    assert hierarchy.codes[1].level is None


@pytest.mark.xml
def test_hierarchy_association_31(samples_folder):
    data_path = samples_folder / "hierarchy_association.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_sdmx(input_str, validate=True).structures
    assert len(result) == 2

    ha1 = result[0]
    assert isinstance(ha1, HierarchyAssociation)
    assert ha1.id == "HA1"
    assert ha1.agency == "BIS"
    assert ha1.version == "1.0"
    assert ha1.name == "Association 1"
    assert (
        ha1.hierarchy
        == "urn:sdmx:org.sdmx.infomodel.codelist.Hierarchy=BIS:H1(1.0)"
    )
    assert (
        ha1.component_ref == "urn:sdmx:org.sdmx.infomodel.datastructure."
        "Dimension=BIS:DSD(1.0).FREQ"
    )
    assert (
        ha1.context_ref
        == "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:DF(1.0)"
    )

    ha2 = result[1]
    assert isinstance(ha2, HierarchyAssociation)
    assert ha2.id == "HA2"
    assert (
        ha2.component_ref == "urn:sdmx:org.sdmx.infomodel.datastructure."
        "Dimension=BIS:DSD(1.0).REF_AREA"
    )
    assert ha2.context_ref == ""


@pytest.mark.xml
def test_concept_scheme_31(samples_folder):
    data_path = samples_folder / "conceptscheme.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_sdmx(input_str, validate=True).structures
    concept_scheme = result[0]
    assert isinstance(concept_scheme, ConceptScheme)
    assert concept_scheme.id == "ECB_CONCEPTS"
    assert concept_scheme.agency == "ECB"
    assert len(concept_scheme.concepts) == 2


def test_data_dataflow_31(samples_folder):
    data_path = samples_folder / "ECB_EXR_data.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_3_1
    result = read_sdmx(input_str, validate=True).data
    data = result[0].data
    num_rows = len(data)
    num_columns = data.shape[1]
    assert num_rows == 21
    assert num_columns == 16


@pytest.mark.xml
def test_data_structure_definition_31(samples_folder):
    data_path = samples_folder / "ECB_EXR_metadata.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_sdmx(input_str, validate=True).structures
    dsd = result[0]
    assert isinstance(dsd, DataStructureDefinition)
    assert dsd.id == "ECB_EXR"
    assert dsd.agency == "ECB"
    components = dsd.components
    assert len(components.attributes) == 24
    assert len(components.data) == 31
    assert len(components.dimensions) == 6
    assert len(components.measures) == 1


def test_vtl_complete_31(samples_folder):
    data_path = samples_folder / "VTL_Sample_1.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_sdmx(input_str, validate=True).structures

    vtl_mapping = result[8]
    assert isinstance(vtl_mapping, VtlMappingScheme)
    assert vtl_mapping.id == "VTLMS1"
    assert vtl_mapping.agency == "SDMX"

    ruleset_scheme = result[9]
    assert isinstance(ruleset_scheme, RulesetScheme)
    assert ruleset_scheme.id == "RS1"
    assert ruleset_scheme.agency == "SDMX"
    assert len(ruleset_scheme.items) == 2

    name_personalisation = result[10]
    assert isinstance(name_personalisation, NamePersonalisationScheme)
    assert name_personalisation.id == "NPS1"
    assert name_personalisation.agency == "SDMX"
    assert len(name_personalisation.items) == 1

    ts_scheme = result[11]
    assert isinstance(ts_scheme, TransformationScheme)
    assert ts_scheme.id == "TS1"
    assert ts_scheme.agency == "SDMX"
    assert len(ts_scheme.items) == 2


def test_vtl_complete_3_31(samples_folder):
    data_path = samples_folder / "VTL_Sample_3.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_sdmx(input_str, validate=True).structures
    assert len(result) == 9
    assert isinstance(result[0], Codelist)
    assert isinstance(result[1], Codelist)
    assert isinstance(result[2], ConceptScheme)
    assert isinstance(result[3], DataStructureDefinition)
    assert isinstance(result[4], DataStructureDefinition)
    assert isinstance(result[5], Dataflow)
    assert isinstance(result[6], Dataflow)
    assert isinstance(result[7], VtlMappingScheme)
    assert isinstance(result[8], TransformationScheme)


def test_dataflow_31(samples_folder):
    data_path = samples_folder / "dataflow.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_sdmx(input_str, validate=True)
    header = result.header
    assert header.receiver[0].id == "AR2"
    assert header.receiver[1].id == "UY2"
    dataflow = result.structures[0]
    assert isinstance(dataflow, Dataflow)
    assert dataflow.id == "EXR"
    assert dataflow.agency == "ECB"
    assert dataflow.structure == "DataStructure=ECB:EXR(1.0)"


def test_data_structure_no_structure(samples_folder):
    data_path = samples_folder / "data_structure_no_structure.xml"
    with open(data_path, "r", encoding="utf-8") as file:
        f = file.read()
    with pytest.raises(
        Invalid, match="This SDMX document is not SDMX-ML 3.1 Structure."
    ):
        read_structure(f, validate=False)


def test_data_no_structure_specific(samples_folder):
    from pysdmx.io.xml.sdmx31.reader.structure_specific import (
        read as read_str_spe,
    )

    data_path = samples_folder / "dataflow_no_structure_specific.xml"
    with open(data_path, "r") as f:
        text = f.read()
    with pytest.raises(
        Invalid,
        match="This SDMX document is not an SDMX-ML StructureSpecificData.",
    ):
        read_str_spe(text, validate=False)


def test_prov_agreement(samples_folder):
    data_path = samples_folder / "prov_agreement_3.1.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_sdmx(input_str, validate=True).get_provision_agreements()
    assert result is not None
    prov_agreement = result[0]
    assert isinstance(prov_agreement, ProvisionAgreement)
    assert prov_agreement.id == "TEST"
    assert prov_agreement.short_urn == "ProvisionAgreement=MD:TEST(1.0)"
    assert prov_agreement.dataflow == "Dataflow=MD:TEST(1.0)"
    assert prov_agreement.provider == "DataProvider=MD:DATA_PROVIDERS(1.0).MD"


@pytest.mark.xml
def test_metadata_family_31(samples_folder):
    data_path = samples_folder / "metadata_family.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    msg = read_sdmx(input_str, validate=True)

    msds = msg.get_metadata_structures()
    assert len(msds) == 1
    assert isinstance(msds[0], MetadataStructure)
    assert len(msds[0]) == 3

    flows = msg.get_metadataflows()
    assert len(flows) == 1
    assert isinstance(flows[0], Metadataflow)
    assert isinstance(flows[0].structure, MetadataStructure)
    assert flows[0].targets == (
        "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=*:*(*)",
    )

    mpas = msg.get_metadata_provision_agreements()
    assert len(mpas) == 1
    assert isinstance(mpas[0], MetadataProvisionAgreement)
    assert mpas[0].metadataflow == (
        "urn:sdmx:org.sdmx.infomodel.metadatastructure."
        "Metadataflow=BIS:MDF_TEST(1.0)"
    )


@pytest.mark.xml
def test_generic_metadata_31(samples_folder):
    data_path = samples_folder / "generic_metadata.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.REFMETA_SDMX_ML_3_1
    reports = read_sdmx(input_str, validate=True).get_reports()
    assert len(reports) == 1
    report = reports[0]
    assert report.id == "RPT1"
    assert report.reportingBegin == "2020-01-01"
    # SDMX-ML 3.1 expresses multiple values as repeated <Attribute> elements
    assert report["CONTACT.EMAIL"].value == [
        "john@example.org",
        "doe@example.org",
    ]
    assert report["NOTE"].value == "A single note"


@pytest.mark.xml
def test_category_scheme_31(samples_folder):
    data_path = samples_folder / "category_scheme.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_sdmx(input_str, validate=True).structures
    cs = next(s for s in result if isinstance(s, CategoryScheme))
    assert cs.id == "CS1"
    assert cs.agency == "BIS"
    assert cs.version == "1.0.0"
    assert cs.is_final is True
    assert cs.items[0].id == "TOP"
    assert cs.items[0].categories[0].id == "MID"
    assert cs.items[0].categories[0].categories[0].id == "LEAF"
    assert cs["TOP.MID.LEAF"].id == "LEAF"
    assert len(cs) == 4
    assert {c.id for c in cs.all_items} == {"TOP", "MID", "LEAF", "OTHER"}


@pytest.mark.xml
def test_category_scheme_31_enrichment(samples_folder):
    data_path = samples_folder / "category_scheme.xml"
    input_str, _ = process_string_to_read(data_path)
    result = read_sdmx(input_str, validate=True).structures
    cs = next(s for s in result if isinstance(s, CategoryScheme))
    leaf = cs["TOP.MID.LEAF"]
    assert len(leaf.dataflows) == 1
    assert isinstance(leaf.dataflows[0], DataflowRef)
    assert leaf.dataflows[0].agency == "BIS"
    assert leaf.dataflows[0].id == "DF1"
    assert leaf.dataflows[0].version == "1.0.0"
    assert leaf.dataflows[0].name == "Dataflow 1"
    other = cs["OTHER"]
    assert len(other.other_references) == 1
    assert isinstance(other.other_references[0], Reference)
    assert other.other_references[0].id == "CL_FREQ"


@pytest.mark.xml
def test_categorisation_31(samples_folder):
    data_path = samples_folder / "category_scheme.xml"
    input_str, _ = process_string_to_read(data_path)
    result = read_sdmx(input_str, validate=True).structures
    cats = [s for s in result if isinstance(s, Categorisation)]
    assert len(cats) == 2
    by_id = {c.id: c for c in cats}
    assert by_id["CAT1"].source == (
        "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:DF1(1.0.0)"
    )
    assert by_id["CAT1"].target == (
        "urn:sdmx:org.sdmx.infomodel.categoryscheme."
        "Category=BIS:CS1(1.0.0).TOP.MID.LEAF"
    )
    assert by_id["CAT2"].source == (
        "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=BIS:CL_FREQ(1.0.0)"
    )
    assert by_id["CAT2"].target == (
        "urn:sdmx:org.sdmx.infomodel.categoryscheme."
        "Category=BIS:CS1(1.0.0).OTHER"
    )


@pytest.mark.xml
def test_availability_constraint_31(samples_folder):
    data_path = samples_folder / "availability_constraint.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_sdmx(input_str, validate=True).structures
    assert len(result) == 1

    ac = result[0]
    assert isinstance(ac, AvailabilityConstraint)
    assert ac.series_count == 3
    assert ac.obs_count == 42
    assert ac.reference == (
        "urn:sdmx:org.sdmx.infomodel.datastructure."
        "Dataflow=TEST_AGENCY:DF_TEST(1.0)"
    )

    att = ac.constraint_attachment
    assert att.data_provider is None
    assert att.dataflows == [
        "urn:sdmx:org.sdmx.infomodel.datastructure."
        "Dataflow=TEST_AGENCY:DF_TEST(1.0)"
    ]

    region = ac.cube_region
    assert region.is_included is True
    assert len(region.key_values) == 1
    assert region.key_values[0].id == "FREQ"
    assert [v.value for v in region.key_values[0].values] == ["M"]


def test_availability_constraint_31_incomplete(samples_folder):
    # A native 3.1 AvailabilityConstraint missing its CubeRegion is not
    # schema-valid (CubeRegion is minOccurs="1"), so this exercises the
    # reader's defensive check for validate=False usage.
    data_path = samples_folder / "availability_constraint_incomplete.xml"
    with pytest.raises(
        Invalid, match="requires a constraint attachment and a cube region"
    ):
        read_sdmx(data_path, validate=False)

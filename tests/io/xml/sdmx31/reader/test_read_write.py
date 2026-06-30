import re
from pathlib import Path

import msgspec
import pytest

from pysdmx.io.format import Format
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.reader import read_sdmx
from pysdmx.io.xml.sdmx30.writer.structure import write as write_structure
from pysdmx.io.xml.sdmx30.writer.structure_specific import (
    write as write_str_spe,
)
from pysdmx.io.xml.sdmx31.writer.structure import write as write_structure_31
from pysdmx.model import (
    Codelist,
    ConceptScheme,
    Hierarchy,
    HierarchyAssociation,
    Metadataflow,
    MetadataProvisionAgreement,
    MetadataStructure,
    NamePersonalisationScheme,
    RulesetScheme,
    TransformationScheme,
    VtlMappingScheme,
)
from pysdmx.model.dataflow import (
    ArrayBoundaries,
    Dataflow,
    DataStructureDefinition,
)


@pytest.fixture
def samples_folder():
    return Path(__file__).parent / "samples"


def test_codelist_31(samples_folder):
    data_path = samples_folder / "codelist.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    structures = read_sdmx(input_str, validate=True).structures
    write = write_structure(structures=structures, prettyprint=True)
    result = read_sdmx(write, validate=True).structures
    codelist = result[0]
    assert isinstance(codelist, Codelist)


def test_hierarchy_31(samples_folder):
    data_path = samples_folder / "hierarchy.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    structures = read_sdmx(input_str, validate=True).structures
    write = write_structure(structures=structures, prettyprint=True)
    result = read_sdmx(write, validate=True).structures
    assert isinstance(result[0], Hierarchy)
    assert result == structures


def test_hierarchy_levels_31(samples_folder):
    data_path = samples_folder / "hierarchy_levels.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    structures = read_sdmx(input_str, validate=True).structures
    write = write_structure(structures=structures, prettyprint=True)
    result = read_sdmx(write, validate=True).structures
    assert isinstance(result[0], Hierarchy)
    assert result == structures


def test_hierarchy_association_31(samples_folder):
    data_path = samples_folder / "hierarchy_association.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    structures = read_sdmx(input_str, validate=True).structures
    write = write_structure(structures=structures, prettyprint=True)
    result = read_sdmx(write, validate=True).structures
    assert len(result) == 2
    assert isinstance(result[0], HierarchyAssociation)
    assert result == structures


def test_concept_scheme_31(samples_folder):
    data_path = samples_folder / "conceptscheme.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    structures = read_sdmx(input_str, validate=True).structures
    write = write_structure(structures=structures, prettyprint=True)
    result = read_sdmx(write, validate=True).structures
    concept_scheme = result[0]
    assert isinstance(concept_scheme, ConceptScheme)


def test_data_dataflow_31(samples_folder):
    data_path = samples_folder / "ECB_EXR_data.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_3_1
    data = read_sdmx(input_str, validate=True).data

    structure_path = samples_folder / "ECB_EXR_metadata.xml"
    struct_input, struct_format = process_string_to_read(structure_path)
    structures = read_sdmx(struct_input, validate=True).structures
    schema = structures[0].to_schema()
    for ds in data:
        ds.structure = schema

    write = write_str_spe(datasets=data, prettyprint=True)
    result = read_sdmx(write, validate=True).data
    read_data = result[0].data
    num_rows = len(read_data)
    num_columns = read_data.shape[1]
    assert num_rows == 21
    assert num_columns == 16


def test_data_structure_definition_31(samples_folder):
    data_path = samples_folder / "ECB_EXR_metadata.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    structure = read_sdmx(input_str, validate=True).structures
    write = write_structure(structures=structure, prettyprint=True)
    result = read_sdmx(write, validate=True).structures
    dsd = result[0]
    assert isinstance(dsd, DataStructureDefinition)


def test_vtl_complete_31(samples_folder):
    data_path = samples_folder / "VTL_Sample_1.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    structure = read_sdmx(input_str, validate=True).structures
    write = write_structure(structures=structure, prettyprint=True)
    result = read_sdmx(write, validate=True).structures
    assert result is not None
    assert isinstance(result[0], Codelist)
    assert isinstance(result[1], Codelist)
    assert isinstance(result[2], ConceptScheme)
    assert isinstance(result[3], ConceptScheme)
    assert isinstance(result[4], DataStructureDefinition)
    assert isinstance(result[5], DataStructureDefinition)
    assert isinstance(result[6], Dataflow)
    assert isinstance(result[7], Dataflow)
    assert isinstance(result[8], VtlMappingScheme)
    assert isinstance(result[9], RulesetScheme)
    assert isinstance(result[10], NamePersonalisationScheme)
    assert isinstance(result[11], TransformationScheme)


def test_vtl_complete_3_31(samples_folder):
    data_path = samples_folder / "VTL_Sample_3.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    structure = read_sdmx(input_str, validate=True).structures
    write = write_structure(structures=structure, prettyprint=True)
    result = read_sdmx(write, validate=True).structures
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
    structure = read_sdmx(input_str, validate=True).structures
    write = write_structure(structures=structure, prettyprint=True)
    result = read_sdmx(write, validate=True).structures
    dataflow = result[0]
    assert isinstance(dataflow, Dataflow)


def test_metadata_family_round_trip_31(samples_folder):
    data_path = samples_folder / "metadata_family.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    structures = read_sdmx(input_str, validate=True).structures
    written = write_structure_31(structures=structures, prettyprint=True)
    result = read_sdmx(written, validate=True).structures
    by_in = {s.short_urn: s for s in structures}
    by_out = {s.short_urn: s for s in result}
    assert set(by_in) == set(by_out)
    for urn, original in by_in.items():
        assert by_out[urn] == original
    types = {type(s) for s in result}
    assert Metadataflow in types
    assert MetadataStructure in types
    assert MetadataProvisionAgreement in types


def test_msd_minoccurs_zero_not_preserved_known_limitation(samples_folder):
    # KNOWN LIMITATION (pinned on purpose): the model does not represent a
    # single-occurrence minOccurs (0 vs 1 with maxOccurs <= 1) -- only array
    # cardinality (maxOccurs > 1) is carried via array_def. The sample's FREQ
    # attribute is declared with minOccurs="0", but on read -> write that
    # optionality is lost and the writer omits minOccurs (defaulting it to 1).
    # This test makes the documented loss explicit so it is no longer silent
    # and any future change to the model is caught here. It is consistent with
    # the JSON reader, which has the same model-level limitation.
    data_path = samples_folder / "metadata_family.xml"
    input_str, _ = process_string_to_read(data_path)
    structures = read_sdmx(input_str, validate=True).structures

    written = write_structure_31(structures=structures, prettyprint=True)

    # The single-occurrence FREQ attribute is written without minOccurs.
    freq_tag = re.search(r'<str:MetadataAttribute id="FREQ"[^>]*>', written)
    assert freq_tag is not None
    assert "minOccurs" not in freq_tag.group(0)
    # The genuine array attribute (NOTE, maxOccurs="unbounded") still carries
    # its cardinality, confirming only array_def survives the round-trip.
    note_tag = re.search(r'<str:MetadataAttribute id="NOTE"[^>]*>', written)
    assert note_tag is not None
    assert 'maxOccurs="unbounded"' in note_tag.group(0)


def test_msd_presentational_with_array_emits_both(samples_folder):
    # A presentational attribute may also carry an array definition. Both
    # isPresentational and minOccurs/maxOccurs must be emitted (regression for
    # the previous if/elif that dropped isPresentational when array_def was
    # present). The sample's CONTACT attribute is presentational; inject an
    # array definition and confirm both appear on the same element.
    data_path = samples_folder / "metadata_family.xml"
    input_str, _ = process_string_to_read(data_path)
    structures = read_sdmx(input_str, validate=True).structures

    msd = next(s for s in structures if isinstance(s, MetadataStructure))
    contact = msd.components[0]
    assert contact.is_presentational is True
    assert contact.array_def is None
    contact = msgspec.structs.replace(
        contact, array_def=ArrayBoundaries(0, None)
    )
    msd = msgspec.structs.replace(
        msd, components=(contact, *msd.components[1:])
    )
    others = [s for s in structures if not isinstance(s, MetadataStructure)]

    written = write_structure_31(structures=[msd, *others], prettyprint=True)
    contact_tag = re.search(
        r'<str:MetadataAttribute id="CONTACT"[^>]*>', written
    )
    assert contact_tag is not None
    assert 'isPresentational="true"' in contact_tag.group(0)
    assert 'maxOccurs="unbounded"' in contact_tag.group(0)

    # The output remains valid and round-trips both flags.
    re_read = read_sdmx(written, validate=True).structures
    out_msd = next(s for s in re_read if isinstance(s, MetadataStructure))
    out_contact = out_msd.components[0]
    assert out_contact.is_presentational is True
    assert out_contact.array_def is not None

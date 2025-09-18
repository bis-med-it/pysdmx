from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.vtl import JsonVtlMappingScheme
from pysdmx.model import Agency, Annotation
from pysdmx.model.vtl import VtlCodelistMapping, VtlMappingScheme


@pytest.fixture
def vms():
    vtl_mapping = VtlCodelistMapping(
        "CODELIST_MAP",
        name="Codelist Mapping",
        codelist="CL_FREQ",
        codelist_alias="FREQ",
    )
    return VtlMappingScheme(
        "VMS",
        name="VMS Scheme",
        agency="BIS",
        description="Just testing",
        version="1.42",
        items=[vtl_mapping],
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        is_partial=True,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
    )


@pytest.fixture
def vms_org():
    vtl_mapping = VtlCodelistMapping(
        "CODELIST_MAP",
        name="Codelist Mapping",
        codelist="CL_FREQ",
        codelist_alias="FREQ",
    )
    return VtlMappingScheme(
        "VMS",
        name="VMS testing",
        agency=Agency("BIS"),
        items=[vtl_mapping],
    )


@pytest.fixture
def vms_no_name():
    vtl_mapping = VtlCodelistMapping(
        "CODELIST_MAP",
        name="Codelist Mapping",
        codelist="CL_FREQ",
        codelist_alias="FREQ",
    )
    return VtlMappingScheme("VMS", agency=Agency("BIS"), items=[vtl_mapping])


def test_vms(vms: VtlMappingScheme):
    sjson = JsonVtlMappingScheme.from_model(vms)

    assert sjson.id == vms.id
    assert sjson.name == vms.name
    assert sjson.agency == vms.agency
    assert sjson.description == vms.description
    assert sjson.version == vms.version
    assert len(sjson.vtlMappings) == 1
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.isPartial is True
    assert sjson.validFrom == vms.valid_from
    assert sjson.validTo == vms.valid_to


def test_vms_org(vms_org: VtlMappingScheme):
    sjson = JsonVtlMappingScheme.from_model(vms_org)

    assert sjson.agency == vms_org.agency.id


def test_vms_no_name(vms_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonVtlMappingScheme.from_model(vms_no_name)

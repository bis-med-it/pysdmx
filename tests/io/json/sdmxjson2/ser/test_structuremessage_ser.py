from datetime import datetime

import msgspec
import pytest

from pysdmx import errors
from pysdmx.io import read_sdmx
from pysdmx.io.json.sdmxjson2.messages.structure import (
    JsonStructureMessage,
    JsonStructures,
)
from pysdmx.io.json.sdmxjson2.writer.v2_0.structure import (
    write as write_v2_0,
)
from pysdmx.io.json.sdmxjson2.writer.v2_1.structure import (
    write as write_v2_1,
)
from pysdmx.model import (
    Agency,
    AgencyScheme,
    Annotation,
    AvailabilityConstraint,
    Codelist,
    ConstraintAttachment,
    CubeKeyValue,
    CubeRegion,
    CubeValue,
    Organisation,
)
from pysdmx.model.code import Code
from pysdmx.model.message import Header, StructureMessage


@pytest.fixture
def header():
    return Header(id="test42", test=True, sender=Organisation("BIS"))


@pytest.fixture
def codelist():
    code1 = Code("A", name="Code A")
    code2 = Code("B", name="Code B")
    return Codelist(
        id="CL_FREQ",
        name="Frequency Codelist",
        agency="BIS",
        version="1.0",
        items=[code1, code2],
    )


@pytest.fixture
def agency_scheme():
    agency = Agency("BIS", name="Bank for International Settlements")
    return AgencyScheme(agency="SDMX", items=[agency])


@pytest.fixture
def msg_with_structures(header, codelist, agency_scheme):
    return StructureMessage(header, [codelist, agency_scheme])


def test_structure_message(msg_with_structures: StructureMessage):
    sjson = JsonStructureMessage.from_model(msg_with_structures)

    # Check header
    assert sjson.meta is not None
    assert sjson.meta.id == "test42"
    assert sjson.meta.test is True
    assert sjson.meta.sender.id == "BIS"
    assert isinstance(sjson.meta.prepared, datetime)

    # Check structures
    assert sjson.data is not None
    assert isinstance(sjson.data, JsonStructures)
    assert len(sjson.data.codelists) == 1
    assert len(sjson.data.agencySchemes) == 1


def test_no_header(codelist):
    msg = StructureMessage(None, [codelist])

    with pytest.raises(errors.Invalid, match="messages must have a header"):
        JsonStructureMessage.from_model(msg)


def test_no_structures(header):
    msg = StructureMessage(header, [])

    with pytest.raises(
        errors.Invalid, match="structure messages must have structures"
    ):
        JsonStructureMessage.from_model(msg)


@pytest.fixture
def availability_constraint():
    return AvailabilityConstraint(
        constraint_attachment=ConstraintAttachment(
            data_provider=None,
            dataflows=[
                "urn:sdmx:org.sdmx.infomodel.datastructure."
                "Dataflow=TEST_AGENCY:DF_TEST(1.0)"
            ],
        ),
        cube_region=CubeRegion(
            key_values=[
                # A tuple, not a list: JsonKeyValue.to_model() always
                # rebuilds `values` as a tuple, and the 2.1 assertion
                # below relies on plain equality after a full JSON
                # round trip.
                CubeKeyValue(id="FREQ", values=(CubeValue(value="M"),))
            ]
        ),
        series_count=3,
        obs_count=42,
    )


def test_availability_constraint_v2_0_writer(availability_constraint):
    out = write_v2_0([availability_constraint])

    assert '"role": "Actual"' in out
    assert '"dataConstraints"' in out
    assert '"availabilityConstraints"' not in out
    # The counts have no dedicated field in the legacy payload, so
    # they are carried as FMR-style sdmx_metrics annotations.
    assert '"type": "sdmx_metrics"' in out

    msg = read_sdmx(out, validate=True)
    constraints = msg.get_availability_constraints()

    assert len(constraints) == 1
    # The attachment and cube region already survived the legacy 2.0
    # dataConstraint round trip; the counts now do too, via the
    # annotations, which are lifted back on read (and excluded from
    # the resulting annotations, so there is no duplication).
    assert constraints[0].reference == availability_constraint.reference
    assert constraints[0].cube_region == availability_constraint.cube_region
    assert constraints[0].series_count == availability_constraint.series_count
    assert constraints[0].obs_count == availability_constraint.obs_count
    assert constraints[0].annotations == ()


def test_availability_constraint_v2_1_writer(availability_constraint):
    out = write_v2_1([availability_constraint])

    assert '"availabilityConstraints"' in out
    assert '"role"' not in out

    msg = read_sdmx(out, validate=True)
    constraints = msg.get_availability_constraints()

    assert len(constraints) == 1
    assert constraints[0] == availability_constraint


def test_availability_constraint_v2_1_writer_with_annotation(
    availability_constraint,
):
    ac = msgspec.structs.replace(
        availability_constraint,
        annotations=(Annotation(id="ANN1", title="Note", type="text"),),
    )
    out = write_v2_1([ac])

    assert '"availabilityConstraints"' in out
    assert '"type": "text"' in out

    msg = read_sdmx(out, validate=True)
    constraints = msg.get_availability_constraints()

    assert len(constraints) == 1
    assert constraints[0] == ac


def test_availability_constraint_duplicate_is_invalid(availability_constraint):
    other = msgspec.structs.replace(availability_constraint, series_count=5)
    with pytest.raises(
        errors.Invalid, match="Two availability constraints for the same"
    ):
        write_v2_1([availability_constraint, other])

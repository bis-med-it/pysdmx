"""Collection of readers for SDMX-JSON messages."""

from pysdmx.io.json.gds import messages as msg
from pysdmx.io.serde import Deserializers

deserializers = Deserializers(
    agencies=msg.JsonAgencyMessage,
    categories=None,
    categorisation=None,
    codes=None,
    concepts=None,
    dataflow_info=None,
    dataflows=None,
    providers=None,
    provision_agreement=None,
    schema=None,
    hier_assoc=None,
    hierarchy=None,
    report=None,
    mapping=None,
    code_map=None,
    transformation_scheme=None,
)
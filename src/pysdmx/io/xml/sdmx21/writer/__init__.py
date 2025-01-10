"""SDMX 2.1 writer package."""
from pysdmx.io.xml.sdmx21.writer.__write_aux import (
    __write_header,
    check_content_dataset,
    check_dimension_at_observation,
    create_namespaces,
    get_end_message,
)
from pysdmx.io.xml.sdmx21.writer.generic import write_data_generic
from pysdmx.io.xml.sdmx21.writer.structure import (
    write_structures as write_structures,
)
from pysdmx.io.xml.sdmx21.writer.structure_specific import (
    write_data_structure_specific,
)
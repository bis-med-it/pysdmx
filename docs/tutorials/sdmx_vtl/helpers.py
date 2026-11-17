"""Helpers for the SDMX-VTL exercise: from a data extraction to its data.

They are the functions of Step 3 of "At run time" in the course notebook
(sdmx_vtl.ipynb), shared by the exercise (sdmx_vtl_practice.ipynb) and its
answer (sdmx_vtl_practice.py).
"""

from pysdmx.api.dc.query import Operator, TextFilter
from pysdmx.api.qb import ApiVersion, LenientRestService
from pysdmx.api.qb.data import DataContext, DataQuery
from pysdmx.io import read_sdmx
from pysdmx.io.format import DataFormat
from pysdmx.model import UrlExtraction
from pysdmx.util import parse_urn

EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0"
OPERATORS = {
    "eq": Operator.EQUALS,
    "ne": Operator.NOT_EQUALS,
    "lt": Operator.LESS_THAN,
    "le": Operator.LESS_THAN_OR_EQUAL,
    "gt": Operator.GREATER_THAN,
    "ge": Operator.GREATER_THAN_OR_EQUAL,
}


def parameters_of(extraction, values=None):
    """Returns the parameters of an extraction, with the run-time values."""
    return {
        p.name: p.value if p.is_fixed else (values or {}).get(p.name, p.value)
        for p in extraction.parameters
    }


def data_query(extraction, urn, values=None):
    """Returns the SDMX REST version and the data query of an extraction."""
    parameters = parameters_of(extraction, values)
    ref = parse_urn(extraction.context_urn or urn)
    filters = [  # the component filters, e.g. c[TIME_PERIOD]=ge:2015
        TextFilter(
            name[2:-1],
            OPERATORS[value.rpartition(":")[0] or "eq"],
            value.rpartition(":")[2],
        )
        for name, value in parameters.items()
        if name != "key"
    ]
    query = DataQuery(
        context=DataContext(ref.sdmx_type.lower()),
        agency_id=ref.agency,
        resource_id=ref.id,
        version=ref.version,
        key=parameters["key"],
        components=filters[0] if filters else None,
    )
    version = extraction.sdmx_api_version.replace(".", "_")
    return ApiVersion[f"V{version}_0"], query


def retrieve(extraction, urn, values=None):
    """Retrieves the data of an extraction, as a pandas DataFrame.

    Args:
        extraction: A QueryExtraction or a UrlExtraction.
        urn: The URN of the SDMX artefact of the input (the one of its
            VtlDatasetMapping), used unless the extraction has a context.
        values: The run-time values of the parameters, by name. They
            replace the default values of the parameters that are not
            fixed.
    """
    if isinstance(extraction, UrlExtraction):
        template = extraction.url_template
        url = template.format(**parameters_of(extraction, values))
        print(url)
        return read_sdmx(url).data[0].data
    version, query = data_query(extraction, urn, values)
    print(extraction.entry_point + query.get_url(version, omit_defaults=True))
    service = LenientRestService(
        extraction.entry_point, version, data_format=DataFormat.SDMX_CSV_2_0_0
    )
    return read_sdmx(service.data(query).decode()).data[0].data

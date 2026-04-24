"""Utility functions for the data connectors."""

from typing import Optional, Union

from pysdmx.api.dc._api import MaintainableIdentification
from pysdmx.api.dc.query import BasicFilter
from pysdmx.api.dc.query.util import parse_query
from pysdmx.api.qb import DataContext, DataQuery
from pysdmx.model import Agency
from pysdmx.util import parse_urn


def prepare_basic_data_query(
    dataflow: Union[str, MaintainableIdentification],
    filters: Optional[Union[BasicFilter, str]] = None,
) -> DataQuery:
    """Return a data query out of the supplied information."""
    if isinstance(dataflow, str):
        dataflow = parse_urn(dataflow)
    aid = (
        dataflow.agency.id
        if isinstance(dataflow.agency, Agency)
        else dataflow.agency
    )

    if isinstance(filters, str):
        filters = parse_query(filters)  # type: ignore[assignment]

    return DataQuery(
        DataContext.DATAFLOW,
        aid,
        dataflow.id,
        dataflow.version,
        components=filters,  # type: ignore[arg-type]
        obs_dimension="AllDimensions",
    )

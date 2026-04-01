"""A Pandas connector for SDMX-REST services."""

import pathlib
import tempfile
from typing import Any, Optional, Union

import pandas as pd

from pysdmx.api.dc import (
    BasicConnector,
    MaintainableIdentification,
    prepare_basic_data_query,
)
from pysdmx.api.dc.query import Filter
from pysdmx.api.dc.rest import SdmxConnector
from pysdmx.api.qb import ApiVersion, DataFormat, RestService
from pysdmx.model import Dataflow
from pysdmx.toolkit.pd import to_pandas_schema


class PandasConnector(BasicConnector):
    """A Pandas connector for data discovery and data retrieval.

    This connector is an implementation of the SDMX "data discovery and
    data retrieval" API for SDMX-REST v2 web services, which returns Pandas
    data frames for data queries.

    In addition to being compliant with the SDMX-REST v2 API, the targeted
    service must be able to return structural metadata in SDMX-JSON v2.0.0 and
    data in SDMX-CSV v2.0.0.
    """

    def __init__(
        self,
        api_endpoint: str,
        pem: Optional[str] = None,
        timeout: Optional[float] = 5.0,
    ):
        """Instantiate a data discovery and retrieval Pandas connector."""
        self.__conn = SdmxConnector(api_endpoint, pem, timeout)
        self.__client = RestService(
            api_endpoint,
            ApiVersion.V2_0_0,
            data_format=DataFormat.SDMX_CSV_2_0_0,
            pem=pem,
            timeout=timeout,
        )

    def dataflows(
        self, search_term: Optional[str] = None
    ) -> tuple[Dataflow, ...]:
        """Get the list of dataflows available in the connector.

        Args:
            search_term (Optional[str]): A search term. If set, any dataflow
                containing the term in its ID, name, or description will be
                returned.

        Returns:
            tuple[Dataflow]: A sorted and immutable collection of dataflows
                matching the supplied search term, if any. For each dataflow,
                information such as its ID, name and description is returned.
                If a search term is supplied and does not match any dataflow,
                an empty collection will be returned. The collection is sorted
                by agency ID, then dataflow ID and then version number.

        Raises:
            errors.Invalid: In case the targeted service returns a client
                error, i.e. a status between 400 and 499.
            errors.InternalError: In case the targeted service returns a
                server error, i.e. a status between 500 and 599, or in case
                the server response could not be deserialized.
            errors.NotFound: In case the targeted service does not contain
                any dataflow.
            errors.Unavailable: In case the targeted service could not be
                reached.
        """
        return self.__conn.dataflows(search_term)

    def dataflow(
        self, dataflow: Union[str, MaintainableIdentification]
    ) -> Dataflow:
        """Retrieve information about a dataflow.

        This function provides details about a dataflow, including its
        components, to assist in querying data effectively.

        Args:
            dataflow (Union[str, MaintainableIdentification]): Specifies the
                dataflow to retrieve. This can be:
                - A string representing the SDMX URN of the dataflow.
                - An object implementing the `MaintainableIdentification`
                  protocol (e.g., instances of `DataflowRef` or `Dataflow`).

        Returns:
            Dataflow: An object containing detailed information about
                the requested dataflow, including:

                - Basic metadata, such as the dataflow's ID and name.
                - Metrics, such as the number of observations or period
                  coverage (if available from the source).
                - The expected data structure (data schema), including
                  components, their types, and other relevant details.

        Raises:
            errors.Invalid: In case the targeted service returns a client
                error, i.e. a status between 400 and 499.
            errors.InternalError: In case the targeted service returns a
                server error, i.e. a status between 500 and 599, or in case
                the server response could not be deserialized.
            errors.NotFound: In case the targeted service does not contain
                the requested dataflow.
            errors.Unavailable: In case the targeted service could not be
                reached.
        """
        return self.__conn.dataflow(dataflow)

    def data(
        self,
        dataflow: Union[str, MaintainableIdentification],
        filters: Optional[Union[Filter, str]] = None,
        apply_schema: bool = True,
    ) -> pd.DataFrame:
        """Get data for the selected dataflow, matching the supplied filters.

        Args:
            dataflow (Union[str, MaintainableIdentification]): The dataflow
                from which to retrieve data. Either a string representing the
                SDMX URN of the dataflow or the information necessary to
                uniquely identify it. Classes such as `DataflowRef` or
                `Dataflow` are examples of pysdmx classes that implement the
                `MaintainableIdentification` protocol.
            filters: The data query filters, if any. This can be a string
                similar to a SQL WHERE clause ("AREA='UY' AND FREQ <> 'A'")
                or a Python expression ("REF_AREA=='UY' and FREQ != 'A'") or
                one of the various filters the `pysdmx.api.dc.query` module
                offers, including `MultiFilter`.
            apply_schema: Whether to apply a schema, with data types, to the
                data frame. In that case, the dataflow definition is retrieved
                and applied to the data, which includes type casting of the
                various columns.

        Returns:
            The requested data, if any. Data are returned as Pandas data frame.
        """
        q = prepare_basic_data_query(dataflow, filters)
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            try:
                for chunk in self.__client.stream_data(q):
                    f.write(chunk)
                f.flush()
                f.close()
                params = {"usecols": self.__include_col}
                if apply_schema:
                    flow = self.dataflow(dataflow)
                    schema = to_pandas_schema(flow.components)
                    params["dtype"] = schema
                return pd.read_csv(f.name, **params)
            finally:
                pathlib.Path(f.name).unlink()

    def __include_col(self, col: Any) -> bool:
        return col not in ["STRUCTURE", "STRUCTURE_ID", "ACTION"]

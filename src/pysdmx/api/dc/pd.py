"""A Pandas connector for SDMX-REST services."""

import pathlib
import tempfile
from typing import Any, Iterable, Literal, Optional, Union

import pandas as pd

from pysdmx.api.dc import BasicConnector, MaintainableIdentification
from pysdmx.api.dc.query import BasicFilter
from pysdmx.api.dc.rest import SdmxConnector
from pysdmx.api.dc.util import prepare_basic_data_query
from pysdmx.api.qb import ApiVersion, DataFormat, RestService
from pysdmx.model import Dataflow
from pysdmx.toolkit.pd import to_pandas_schema
from pysdmx.util import experimental


@experimental
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
        timeout: Optional[float] = 20.0,
    ):
        """Instantiate a data discovery and retrieval Pandas connector."""
        self.__conn = SdmxConnector(api_endpoint, pem, timeout)
        self.__client = RestService(
            api_endpoint,
            ApiVersion.V2_0_0,
            data_format=DataFormat.SDMX_CSV_1_0_0,
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
        filters: Optional[Union[BasicFilter, str]] = None,
        columns: Optional[Iterable[str]] = None,
        apply_schema: bool = True,
        infer_series_keys: bool = True,
        infer_index: bool = True,
        labels: Literal["id", "name", "both"] = "id",
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
            columns: The components (dimensions, attributes and measures) to
                be returned. If not provided, all components will be returned.
            apply_schema: Whether to apply a schema, with data types, to the
                data frame. In that case, the dataflow definition is retrieved
                and applied to the data, which includes type casting of the
                various columns.
            infer_series_keys: Whether to attempt inferring the series keys
                from the dimension values. Series keys are generated by
                concatenating the values of all dimension columns using a
                period (.) as a separator. This operation will only be
                performed if the `TIME_PERIOD` column exists in the data
                structure. When enabled, a new column called `SERIES_KEY`
                will be added to the DataFrame.
            infer_index: Whether to create an index for the DataFrame.
                This operation will only be performed if the `TIME_PERIOD`
                column exists in the data structure. When enabled, the
                DataFrame will be indexed using a combination of `SERIES_KEY`
                and `TIME_PERIOD`.
            labels: Specifies the format of category fields in the DataFrame.
                The following options are available:
                    - "id": Only include the code IDs (default behavior).
                    - "name": Replace code IDs with their corresponding names.
                    - "both": Include both the code IDs and names,
                      formatted as "ID: Name".

        Returns:
            The requested data, if any. Data are returned as Pandas data frame.
        """
        q = prepare_basic_data_query(dataflow, filters)
        try:
            # Write response in chunks to temporary file
            with tempfile.NamedTemporaryFile(
                mode="wb", suffix=".csv", delete=False
            ) as f:
                for chunk in self.__client.stream_data(
                    q, chunk_size=1_048_576
                ):
                    f.write(chunk)
                f.flush()
                f.close()

            # Infer read parameters (exclude SDMX columns, add data types etc.)
            params: dict[str, Any] = {}
            csv_cols = ["STRUCTURE", "STRUCTURE_ID", "ACTION"]
            params["usecols"] = lambda c: c not in csv_cols
            flow = None
            if apply_schema:
                flow = self.dataflow(dataflow)
                schema = to_pandas_schema(flow.components)  # type: ignore[arg-type]
                params["dtype"] = schema

            # Read CSV and return DataFrame
            df = pd.read_csv(f.name, **params)

            # Infer series keys
            if (
                infer_series_keys or infer_index
            ) and "TIME_PERIOD" in df.columns:
                if not flow:
                    flow = self.dataflow(dataflow)
                dim_cols = [
                    d.id
                    for d in flow.components.dimensions
                    if d.id != "TIME_PERIOD"
                ]
                df["SERIES_KEY"] = df[dim_cols].map(str).agg(".".join, axis=1)

            # Add index
            if infer_index and "TIME_PERIOD" in df.columns:
                idxs = ["SERIES_KEY", "TIME_PERIOD"]
                idxs = [i for i in idxs if i and (not columns or i in columns)]
                if idxs:
                    df.set_index(idxs, inplace=True)

            if columns:
                df = df[columns]

            if labels != "id":
                if not flow:
                    flow = self.dataflow(dataflow)
                df = self.__map_category_fields(df, flow, labels)
            return df
        finally:
            pathlib.Path(f.name).unlink()

    def __map_category_fields(
        self, df: pd.DataFrame, flow: Dataflow, labels: Literal["name", "both"]
    ) -> pd.DataFrame:
        for comp in flow.components:
            field = comp.id
            if field in df.columns and comp.enumeration:
                if labels == "name":
                    mapping = {c.id: c.name for c in comp.enumeration}
                    df[field] = df[field].map(mapping)
                else:
                    mapping = {
                        c.id: f"{c.id}: {c.name}" for c in comp.enumeration
                    }
                    df[field] = df[field].map(mapping)
        return df

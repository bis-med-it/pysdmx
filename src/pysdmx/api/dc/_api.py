"""API to be implemented by connectors."""

from datetime import datetime
from typing import (
    Any,
    Generator,
    Iterable,
    List,
    Literal,
    Optional,
    Protocol,
    runtime_checkable,
    Sequence,
    Union,
)

from pysdmx.api.dc.query import (
    BooleanFilter,
    DateTimeFilter,
    MultiFilter,
    NotFilter,
    NumberFilter,
    SortBy,
    TextFilter,
)
from pysdmx.model import (
    DataflowInfo,
    DataflowRef,
    Organisation,
    SeriesInfo,
)


@runtime_checkable
class Connector(Protocol):
    """A Connector provides access to a data source.

    Connectors support both data discovery and data retrieval.

    Attributes:
        owner: The organisation providing the Connector.
            It is recommended to provide contact details, in case users
            of the Connector have questions about it.
    """

    owner: Organisation

    def dataflows(
        self,
        filter_query: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> Iterable[DataflowRef]:
        """Get the dataflows provided by the Connector.

        Args:
            filter_query: A search term. If set, any dataflow containing the
                term in its id, name or description will be returned.
            provider: A data provider. If set, any dataflow for which data are
                being provided by the supplied provider will be returned.

        Returns: Iterable[DataflowRef]: A collection of dataflow references.

                The references contain core information about the
                dataflows provided by the Connector. Most importantly,
                they contain the identifying information required to
                retrieve more information about a specific dataflow
                (see dataflow).

                It is expected that this method, if implemented,
                will return at least one DataflowRef object.
        """

    def providers(
        self,
        filter_query: Optional[str] = None,
    ) -> Iterable[Organisation]:
        """Get the providers of which data are available in the Connector.

        Args:
            filter_query: A search term. If set, any provider containing the
                term in its id, name or description will be returned.

        Returns: Iterable[Organisation]: A collection of data providers.
        """

    def dataflow(
        self, dataflow: Union[str, DataflowRef], metrics: bool = False
    ) -> DataflowInfo:
        """Get information about a dataflow.

        Args:
            dataflow: Either a string representing the dataflow ID or
                a DataflowRef, as returned by calling the dataflows
                function.
            metrics: Metrics contain useful information such as
                the number of observations, series, when the
                dataflow was last updated, etc. However, it may be
                expensive to fetch this information. In case metrics
                are not required, you may set metrics to False, to
                prevent them from being computed.

        Returns: DataflowInfo: Information about the requested dataflow.

            The information includes:

            - Some basic metadata about the dataflow (such as its ID and name).
            - Some useful metrics such as the number of observations.
            - The expected structure of data (i.e. the data schema), including
              the expected columns, their types, etc.
        """

    def series(
        self,
        dataflow: Union[str, DataflowRef, DataflowInfo],
        provider: Optional[Union[str, Organisation]] = None,
        filters: Optional[
            Union[
                BooleanFilter,
                DateTimeFilter,
                MultiFilter,
                NotFilter,
                NumberFilter,
                str,
                TextFilter,
            ]
        ] = None,
        discontinued: bool = False,
        updated_after: Optional[datetime] = None,
    ) -> Generator[SeriesInfo, None, None]:
        """Get the series available in the dataflow.

        Args:
            dataflow: Either a string representing the dataflow ID or
                a DataflowRef, as returned by calling the dataflows
                function, or a DataflowInfo, as returned by calling the
                dataflow function.
            provider: The organisation providing the data to be returned.
            filters: A dictionary, where the keys are the IDs of the
                components used for filtering and the values
                represent the filters to be applied.
            discontinued: Whether discontinued (i.e. old)
                series should be returned. Defaults to `False`.
            updated_after: Retrieve the series updated after
                the supplied timestamp.

        Returns: A generator, to iterate over the collection matching series
            The information includes:

            - Some basic metadata about the series (such as an ID or name).
            - Some useful metrics such as the number of observations, the last
              time it was updated, etc.
        """

    def data(
        self,
        dataflow: Union[str, DataflowRef, DataflowInfo],
        provider: Optional[Union[str, Organisation]] = None,
        series: Optional[Sequence[str]] = None,
        filters: Optional[
            Union[
                BooleanFilter,
                DateTimeFilter,
                MultiFilter,
                NotFilter,
                NumberFilter,
                str,
                TextFilter,
            ]
        ] = None,
        columns: Optional[Sequence[str]] = None,
        sort: Optional[List[SortBy]] = None,
        offset: int = 0,
        limit: Optional[int] = None,
        history: bool = False,
        updated_after: Optional[datetime] = None,
        format: Literal["dict", "pandas"] = "dict",
    ) -> Any:
        """Get data for the selected dataflow.

        Args:
            dataflow: Either a string representing the dataflow ID or
                a DataflowRef, as returned by calling the dataflows
                function, or a DataflowInfo, as returned by calling the
                dataflow function.
            provider: The organisation providing the data to be returned.
            series: One or more strings identifying the series
                for which data should be returned (e.g. D.USD.EUR.SP00).
                wildcards can be used too (e.g. D.*.EUR.SP00).
            filters: A dictionary, where the keys are the IDs of the
                components used for filtering and the values
                represent the filters to be applied.
            columns: The fields to be returned.
            sort: The desired sorting order of the results.
            offset: From which row to start fetching. This is useful to
                paginate results. Default to 0.
            limit: The number of rows to be returned.
            history: Whether to retrieve previous "versions" of the data or
                only the latest one. This is useful to see how the data may
                have evolved or have been corrected over time.
            updated_after: Retrieve the series updated after
                the supplied timestamp.
            format: The desired format for the data. By default, a generator
                of dict objects will be returned, but there are other options
                such as pandas data frames.

        Returns: A generator, to iterate over the matching data, if format is
            set to dict (the default), or a pandas data frame.
        """


__all__ = ["Connector"]

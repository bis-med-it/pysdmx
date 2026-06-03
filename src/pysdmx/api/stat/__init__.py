"""Download connector for SDMX .Stat Suite services (e.g. OECD)."""

from __future__ import annotations

from enum import Enum
from typing import Optional, Union

from pysdmx.api.qb import (
    ApiVersion,
    DataFormat,
    RestService,
    StructureFormat,
)
from pysdmx.util import experimental


class StatEndpoints(str, Enum):
    """Known .Stat Suite SDMX-REST v2 entry points."""

    OECD = "https://sdmx.oecd.org/public/rest/v2"


@experimental
class StatConnector:
    """Download connector for .Stat Suite SDMX-REST v2 services.

    .Stat Suite deployments (e.g. OECD dotStatSuite) serve structural
    metadata as SDMX-ML 2.1 and data as SDMX-CSV, and do not expose the
    SDMX-REST ``/schema`` endpoint. This connector retrieves a single
    SDMX-ML 2.1 structure message (with descendants) plus SDMX-CSV 1.0.0
    data, and relies on pysdmx's native readers to produce a ``Dataflow``,
    a ``Schema`` and a ``PandasDataset``.

    Obtain the ``agency``, ``id`` and ``version`` of a dataflow from the
    OECD Data Explorer (https://data-explorer.oecd.org) via its
    "Developer API" button.
    """

    def __init__(
        self,
        api_endpoint: Union[str, StatEndpoints] = StatEndpoints.OECD,
        pem: Optional[str] = None,
        timeout: Optional[float] = 20.0,
    ) -> None:
        """Instantiate a .Stat Suite download connector.

        Args:
            api_endpoint: The SDMX-REST v2 entry point. Defaults to the
                OECD public service.
            pem: Optional PEM file with trusted certificate authorities,
                for services using a self-signed certificate.
            timeout: Maximum number of seconds to wait per request.
        """
        self._svc = RestService(
            api_endpoint,
            ApiVersion.V2_0_0,
            data_format=DataFormat.SDMX_CSV_1_0_0,
            structure_format=StructureFormat.SDMX_ML_2_1,
            timeout=timeout,
            pem=pem,
        )


__all__ = ["StatConnector", "StatEndpoints"]

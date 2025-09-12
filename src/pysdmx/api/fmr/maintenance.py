"""Upload metadata to an FMR instance."""

from enum import Enum
from typing import Optional, Sequence, Union

import httpx
import msgspec

from pysdmx.io.json.sdmxjson2.writer import serializers
from pysdmx.model import MetadataReport
from pysdmx.model.__base import MaintainableArtefact
from pysdmx.model.message import (
    Header,
    MetadataMessage,
    StructureMessage,
)
from pysdmx.util._net_utils import map_httpx_errors


class StructureAction(Enum):
    """Enumeration that defines the action when updating metadata in the FMR.

    Arguments:
        Append: Structures uploaded with action 'Append' may only add new
            structures and may not overwrite any existing structures.
        Merge: Structures uploaded with action 'Merge' may add new structures
            and replace existing structures. However for Item Schemes
            (codelists, concept schemes, etc.), the items submitted will be
            added to the existing scheme. For example if a codelist exists
            with codes A, B, and C, and the same codelist is submitted with
            codes B and X, then the resulting codelist will have codes A, B,
            C, X, i.e. code B has been replace while code X has been added.
        Replace: Structures uploaded with action 'Replace' may add new
            structures to the Registry, and can also replace existing
            structures with new ones. This is the default.
    """

    Append = "Append"
    Merge = "Merge"
    Replace = "Replace"


class RegistryMaintenanceClient:
    """EXPERIMENTAL: A client to update metadata in the FMR."""

    def __init__(
        self,
        api_endpoint: str,
        user: str,
        password: str,
        pem: Optional[str] = None,
        timeout: float = 60.0,
    ):
        """Instantiate a new client to update metadata in the target endpoint.

        Args:
            api_endpoint: The endpoint of the targeted service.
            user: Username for authentication.
            password: Password for authentication.
            pem: In case the service exposed a certificate created by an
                unknown certificate authority, you can pass a pem file for
                this authority using this parameter.
            timeout: The maximum number of seconds to wait before considering
                that a request timed out. Defaults to 10 seconds.
        """
        if api_endpoint.endswith("/"):
            api_endpoint = api_endpoint[0:-1]
        self._api_endpoint = f"{api_endpoint}/ws/secure/sdmxapi/rest"
        self._user = user
        self._password = password
        self._timeout = timeout
        self._ssl_context = (
            httpx.create_ssl_context(
                verify=pem,
            )
            if pem
            else httpx.create_ssl_context()
        )
        self._encoder = msgspec.json.Encoder()

    def __post(
        self,
        message: Union[MetadataMessage, StructureMessage],
        action: StructureAction = StructureAction.Replace,
    ) -> None:
        with httpx.Client(verify=self._ssl_context) as client:
            try:
                url = f"{self._api_endpoint}"
                auth = httpx.BasicAuth(self._user, self._password)
                headers = {
                    "Content-Type": "application/text",
                    "Action": action.value,
                }
                if isinstance(message, MetadataMessage):
                    serializer = serializers.metadata_message
                else:
                    serializer = serializers.structure_message
                bodyjs = self._encoder.encode(serializer.from_model(message))
                r = client.post(
                    url,
                    headers=headers,
                    content=bodyjs,
                    timeout=self._timeout,
                    auth=auth,
                )
                r.raise_for_status()
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                map_httpx_errors(e)

    def put_structures(
        self,
        artefacts: Sequence[MaintainableArtefact],
        header: Optional[Header] = None,
        action: StructureAction = StructureAction.Replace,
    ) -> None:
        """EXPERIMENTAL: Upload SDMX structures to the FMR.

        This method is experimental and its interface or behavior may change
        without notice.

        Args:
            artefacts: The sequence of SDMX maintainable artefacts to upload.
            header: Optional SDMX Header to include in the message. If not
                supplied, pysdmx will generate one for you.
            action: How to apply the changes in case of already existing
                structures.
        """
        if not header:
            header = Header()
        message = StructureMessage(header=header, structures=artefacts)
        return self.__post(message, action)

    def put_metadata_reports(
        self,
        reports: Sequence[MetadataReport],
        header: Optional[Header] = None,
        action: StructureAction = StructureAction.Replace,
    ) -> None:
        """EXPERIMENTAL: Upload SDMX metadata reports to the FMR.

        This method is experimental and its interface or behavior may change
        without notice.

        Args:
            reports: A sequence of metadata reports to upload.
            header: Optional SDMX Header to include in the message. If not
                supplied, pysdmx will generate one for you.
            action: How to apply the changes in case of already existing
                structures.
        """
        if not header:
            header = Header()
        message = MetadataMessage(header=header, reports=reports)
        return self.__post(message, action)

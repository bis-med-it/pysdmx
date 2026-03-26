"""Collection of SDMX-JSON schemas for dataflow queries."""

from typing import List, Optional, Sequence, Union

from msgspec import Struct

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.code import JsonCodelist, JsonValuelist
from pysdmx.io.json.sdmxjson2.messages.concept import JsonConceptScheme
from pysdmx.io.json.sdmxjson2.messages.constraint import JsonDataConstraint
from pysdmx.io.json.sdmxjson2.messages.core import (
    JsonAnnotation,
    MaintainableType,
)
from pysdmx.io.json.sdmxjson2.messages.dsd import JsonDataStructure
from pysdmx.io.json.sdmxjson2.messages.provider import JsonDataProviderScheme
from pysdmx.model import (
    Agency,
    Components,
    Dataflow,
    DataflowInfo,
    DataProvider,
    DataStructureDefinition,
)
from pysdmx.model.dataflow import Group
from pysdmx.util import is_final, parse_urn


def __parse_annotation_metrics(
    const: JsonDataConstraint,
) -> tuple[Optional[int], Optional[int]]:
    if const.annotations:
        obs = None
        series = None
        for a in const.annotations:
            if a.type == "sdmx_metrics" and a.id == "obs_count" and a.title:
                obs = int(a.title)
            elif (
                a.type == "sdmx_metrics" and a.id == "series_count" and a.title
            ):
                series = int(a.title)
        return obs, series
    else:
        return None, None


def _extract_metrics(
    df: "JsonDataflow", constraints: Sequence[JsonDataConstraint]
) -> tuple[Optional[int], Optional[int]]:
    dfurn = (
        "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow="
        f"{df.agency}:{df.id}({df.version})"
    )
    const = [
        c
        for c in constraints
        if c.constraintAttachment
        and c.constraintAttachment.dataflows
        and dfurn in c.constraintAttachment.dataflows
    ]
    if const:
        obs_count, series_count = __parse_annotation_metrics(const[0])
    else:
        obs_count = None
        series_count = None
    return (obs_count, series_count)


class JsonDataflow(MaintainableType, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a dataflow."""

    structure: str = ""

    def to_model(
        self,
        dsds: Sequence[JsonDataStructure] = (),
        concepts: Sequence[JsonConceptScheme] = (),
        valuelists: Sequence[JsonValuelist] = (),
        codelists: Sequence[JsonCodelist] = (),
        constraints: Sequence[JsonDataConstraint] = (),
    ) -> Dataflow:
        """Converts a FusionDataflow to a standard dataflow."""
        dsd: Optional[Union[DataStructureDefinition, str]] = None
        if len(dsds) > 0:
            ref = parse_urn(self.structure)
            m = [
                d
                for d in dsds
                if d.agency == ref.agency
                and d.id == ref.id
                and d.version == ref.version
            ]
            if len(m) == 1:
                dsd = m[0].to_model(concepts, codelists, valuelists, ())
        dsd = dsd if dsd is not None else self.structure
        obs_count, series_count = _extract_metrics(self, constraints)
        return Dataflow(
            id=self.id,
            agency=self.agency,
            name=self.name,
            description=self.description,
            version=self.version,
            is_final=is_final(self.version),
            structure=dsd,
            annotations=[a.to_model() for a in self.annotations],
            is_external_reference=self.isExternalReference,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            obs_count=obs_count,
            series_count=series_count,
        )

    @classmethod
    def from_model(self, df: Dataflow) -> "JsonDataflow":
        """Converts a pysdmx dataflow to an SDMX-JSON one."""
        if not df.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON dataflows must have a name",
                {"dataflow": df.id},
            )
        if not df.structure:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON dataflows must reference a DSD.",
                {"dataflow": df.id},
            )
        if isinstance(df.structure, DataStructureDefinition):
            dsdref = (
                "urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure="
                f"{df.structure.agency}:{df.structure.id}({df.structure.version})"
            )
        else:
            dsdref = df.structure
        return JsonDataflow(
            agency=(
                df.agency.id if isinstance(df.agency, Agency) else df.agency
            ),
            id=df.id,
            name=df.name,
            version=df.version,
            isExternalReference=df.is_external_reference,
            validFrom=df.valid_from,
            validTo=df.valid_to,
            description=df.description,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in df.annotations]
            ),
            structure=dsdref,
        )


class JsonDataflows(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for the list of dataflows."""

    dataflows: Sequence[JsonDataflow]
    dataProviderSchemes: Sequence[JsonDataProviderScheme] = ()
    dataStructures: Sequence[JsonDataStructure] = ()
    conceptSchemes: Sequence[JsonConceptScheme] = ()
    valuelists: Sequence[JsonValuelist] = ()
    codelists: Sequence[JsonCodelist] = ()
    dataConstraints: Sequence[JsonDataConstraint] = ()

    def __filter(
        self, df: JsonDataflow, agency: str, id_: str, version: str
    ) -> bool:
        if version != "+" and version != "latest":
            return (
                df.agency == agency and df.id == id_ and df.version == version
            )
        else:
            return df.agency == agency and df.id == id_

    def to_model(
        self,
        components: Components,
        grps: Optional[Sequence[Group]],
        agency: str,
        id_: str,
        version: str,
    ) -> DataflowInfo:
        """Returns the requested dataflow details."""
        prvs: List[DataProvider] = []
        for dps in self.dataProviderSchemes:
            prvs.extend(dps.dataProviders)
        df = list(
            filter(
                lambda df: self.__filter(df, agency, id_, version),
                self.dataflows,
            )
        )[0]

        obs_count, series_count = _extract_metrics(df, self.dataConstraints)

        return DataflowInfo(
            id=df.id,
            components=components,
            agency=Agency(df.agency),
            name=df.name,
            description=df.description,
            version=df.version,
            providers=prvs,
            dsd_ref=df.structure,
            groups=grps,
            obs_count=obs_count,
            series_count=series_count,
        )

    def to_generic_model(self) -> Sequence[Dataflow]:
        """Returns the requested dataflows."""
        return [
            df.to_model(
                self.dataStructures,
                self.conceptSchemes,
                self.valuelists,
                self.codelists,
                self.dataConstraints,
            )
            for df in self.dataflows
        ]


class JsonDataflowMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for /dataflow queries (with details)."""

    data: JsonDataflows

    def to_model(
        self,
        components: Components,
        grps: Optional[Sequence[Group]],
        agency: str,
        id_: str,
        version: str,
    ) -> DataflowInfo:
        """Returns the requested dataflow details."""
        return self.data.to_model(components, grps, agency, id_, version)


class JsonDataflowsMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for /dataflow queries."""

    data: JsonDataflows

    def to_model(self) -> Sequence[Dataflow]:
        """Returns the requested dataflows."""
        return self.data.to_generic_model()

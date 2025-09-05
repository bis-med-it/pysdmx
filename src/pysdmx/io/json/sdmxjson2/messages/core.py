"""Collection of SDMX-JSON schemas for common artefacts."""

from datetime import datetime
from typing import Optional, Sequence, Union

import msgspec

from pysdmx.errors import NotFound
from pysdmx.model import (
    Annotation,
    ArrayBoundaries,
    Codelist,
    DataType,
    Facets,
    Organisation,
)
from pysdmx.model.message import Header
from pysdmx.util import find_by_urn


class JsonLink(msgspec.Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for link objects."""

    href: Optional[str] = None
    urn: Optional[str] = None
    rel: Optional[str] = None
    uri: Optional[str] = None
    type: Optional[str] = None
    title: Optional[str] = None
    hreflang: Optional[str] = None


class JsonAnnotation(msgspec.Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for annotations."""

    id: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None
    value: Optional[str] = None
    text: Optional[str] = None
    links: Sequence[JsonLink] = ()

    def to_model(self) -> Annotation:
        """Converts a JsonAnnotation to a standard Annotation."""
        m = [lnk for lnk in self.links if lnk.rel == "self"]
        lnk = m[0] if len(m) == 1 else None
        if lnk and lnk.href:
            url = lnk.href
        elif lnk and lnk.uri:
            url = lnk.uri
        else:
            url = None
        return Annotation(
            id=self.id,
            title=self.title,
            type=self.type,
            url=url,
            text=self.value if self.value else self.text,
        )

    @classmethod
    def from_model(self, annotation: Annotation) -> "JsonAnnotation":
        """Converts a pysdmx annotation to an SDMX-JSON one."""
        if annotation.url:
            links = tuple([JsonLink(rel="self", href=annotation.url)])
        else:
            links = ()

        return JsonAnnotation(
            id=annotation.id,
            title=annotation.title,
            type=annotation.type,
            text=annotation.text,
            links=links,
        )


class IdentifiableType(msgspec.Struct, frozen=True, omit_defaults=True):
    """An abstract base type used for all nameable artefacts."""

    id: str
    annotations: Sequence[JsonAnnotation] = ()


class NameableType(msgspec.Struct, frozen=True, omit_defaults=True):
    """An abstract base type used for all nameable artefacts."""

    id: str
    name: str
    description: Optional[str] = None
    annotations: Sequence[JsonAnnotation] = ()


class MaintainableType(
    msgspec.Struct,
    frozen=True,
    rename={"agency": "agencyID"},
    omit_defaults=True,
):
    """An abstract base type used for all maintainable artefacts."""

    agency: str
    id: str
    name: str
    version: str = "1.0"
    isExternalReference: bool = False
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    description: Optional[str] = None
    annotations: Sequence[JsonAnnotation] = ()


class ItemSchemeType(MaintainableType, frozen=True, omit_defaults=True):
    """An abstract base type used for all item schemes."""

    isPartial: bool = False


class JsonTextFormat(msgspec.Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for TextFormat."""

    dataType: Optional[str] = None
    minLength: Optional[int] = None
    maxLength: Optional[int] = None
    minValue: Optional[Union[int, float]] = None
    maxValue: Optional[Union[int, float]] = None
    startValue: Optional[Union[int, float]] = None
    endValue: Optional[Union[int, float]] = None
    decimals: Optional[int] = None
    pattern: Optional[str] = None
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    isSequence: bool = False
    isMultilingual: bool = False
    sentinelValues: Optional[Sequence[str]] = None
    timeInterval: Optional[str] = None
    interval: Optional[Union[int, float]] = None

    @classmethod
    def from_model(
        self, dtype: Optional[DataType], facets: Optional[Facets]
    ) -> Optional["JsonTextFormat"]:
        """Converts pysdmx format details to an SDMX-JSON JsonTextFormat."""
        if dtype is None and facets is None:
            return None
        else:
            typ = dtype.value if dtype else None
            if facets is None:
                return JsonTextFormat(typ)
            else:
                return JsonTextFormat(
                    typ,
                    facets.min_length,
                    facets.max_length,
                    facets.min_value,
                    facets.max_value,
                    facets.start_value,
                    facets.end_value,
                    facets.decimals,
                    facets.pattern,
                    facets.start_time,
                    facets.end_time,
                    facets.is_sequence,
                    facets.is_multilingual,
                    timeInterval=facets.time_interval,
                    interval=facets.interval,
                )


def get_facets(input: JsonTextFormat) -> Facets:
    """Create Facets out of a JsonTextFormat."""
    return Facets(
        min_length=input.minLength,
        max_length=input.maxLength,
        is_sequence=input.isSequence,
        min_value=input.minValue,
        max_value=input.maxValue,
        start_value=input.startValue,
        end_value=input.endValue,
        decimals=input.decimals,
        pattern=input.pattern,
        start_time=input.startTime,
        end_time=input.endTime,
        is_multilingual=input.isMultilingual,
    )


class JsonRepresentation(msgspec.Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for core representation."""

    enumerationFormat: Optional[JsonTextFormat] = None
    enumeration: Optional[str] = None
    format: Optional[JsonTextFormat] = None
    minOccurs: Optional[int] = None
    maxOccurs: Optional[int] = None

    def to_facets(self) -> Optional[Facets]:
        """Return a Facets domain object."""
        fmt = self.enumerationFormat if self.enumeration else self.format
        if fmt and (
            fmt.minLength
            or fmt.maxLength
            or fmt.isSequence
            or fmt.minValue
            or fmt.maxValue
            or fmt.startValue
            or fmt.endValue
            or fmt.decimals
            or fmt.pattern
            or fmt.startTime
            or fmt.endTime
            or fmt.isMultilingual
        ):
            return get_facets(fmt)
        else:
            return None

    def to_enumeration(
        self,
        codelists: Sequence[Codelist],
        valid: Sequence[str],
    ) -> Optional[Codelist]:
        """Returns the list of codes allowed for this component."""
        if self.enumeration:
            try:
                a = find_by_urn(codelists, self.enumeration)
                codes = [c for c in a.codes if not valid or c.id in valid]
                return msgspec.structs.replace(a, items=codes)
            except NotFound:
                # This is OK. In case of schema queries, if a component
                # has both a local and a core representations, only the
                # relevant one (i.e. the local one) will be included in
                # the schema.
                return None
        return None

    def to_array_def(self) -> Optional[ArrayBoundaries]:
        """Returns the array boundaries, if any."""
        if self.maxOccurs and self.maxOccurs > 1:
            m = self.minOccurs if self.minOccurs is not None else 0
            return ArrayBoundaries(m, self.maxOccurs)
        else:
            return None

    @classmethod
    def from_model(
        self,
        dtype: Optional[DataType],
        enumeration: Optional[str],
        facets: Optional[Facets],
        array_def: Optional[ArrayBoundaries],
    ) -> Optional["JsonRepresentation"]:
        """Converts pysdmx representation details to an SDMX-JSON one."""
        if (
            dtype is None
            and enumeration is None
            and facets is None
            and array_def is None
        ):
            return None
        else:
            fmt = JsonTextFormat.from_model(dtype, facets)
            if array_def:
                mino = array_def.min_size
                maxo = array_def.max_size
            else:
                mino = None
                maxo = None
            if enumeration:
                return JsonRepresentation(
                    enumerationFormat=fmt,
                    enumeration=enumeration,
                    minOccurs=mino,
                    maxOccurs=maxo,
                )
            else:
                return JsonRepresentation(
                    format=fmt, minOccurs=mino, maxOccurs=maxo
                )


class JsonHeader(msgspec.Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for message header."""

    id: str
    prepared: datetime
    sender: Organisation
    test: bool = False
    contentLanguages: Sequence[str] = ()
    name: Optional[str] = None
    receivers: Optional[Organisation] = None
    links: Sequence[JsonLink] = ()

    def to_model(self) -> Header:
        """Map to pysdmx header class."""
        return Header(
            id=self.id,
            test=self.test,
            prepared=self.prepared,
            sender=self.sender,
        )

    @classmethod
    def from_model(self, header: Header) -> "JsonHeader":
        """Create an SDMX-JSON header from a pysdmx Header."""
        return JsonHeader(
            header.id,
            header.prepared,
            header.sender,
            header.test,
            receivers=header.receiver,
        )

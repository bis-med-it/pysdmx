"""Collection of SDMX-JSON schemas for common artefacts."""

from datetime import datetime
from typing import Optional, Sequence, Union

import msgspec

from pysdmx.model import ArrayBoundaries, Codelist, Facets
from pysdmx.util import find_by_urn


class JsonAnnotation(msgspec.Struct, frozen=True):
    """SDMX-JSON payload for annotations."""

    id: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None
    value: Optional[str] = None
    text: Optional[str] = None


class JsonTextFormat(msgspec.Struct, frozen=True):
    """SDMX-JSON payload for TextFormat."""

    dataType: str
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
    interval: Optional[int] = None


class JsonRepresentation(msgspec.Struct, frozen=True):
    """SDMX-JSON payload for core representation."""

    enumerationFormat: Optional[JsonTextFormat] = None
    enumeration: Optional[str] = None
    format: Optional[JsonTextFormat] = None
    minOccurs: Optional[int] = None
    maxOccurs: Optional[int] = None

    def to_facets(self) -> Optional[Facets]:
        """Return a Facets domain object."""
        if self.enumeration:
            fmt = self.enumerationFormat
        else:
            fmt = self.format
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
        ):
            return Facets(
                min_length=fmt.minLength,
                max_length=fmt.maxLength,
                is_sequence=fmt.isSequence,
                min_value=fmt.minValue,
                max_value=fmt.maxValue,
                start_value=fmt.startValue,
                end_value=fmt.endValue,
                decimals=fmt.decimals,
                pattern=fmt.pattern,
                start_time=fmt.startTime,
                end_time=fmt.endTime,
            )
        else:
            return None

    def to_enumeration(
        self,
        codelists: Sequence[Codelist],
        valid: Sequence[str],
    ) -> Optional[Codelist]:
        """Returns the list of codes allowed for this component."""
        if self.enumeration:
            a = find_by_urn(codelists, self.enumeration)
            codes = [c for c in a.codes if not valid or c.id in valid]
            return msgspec.structs.replace(a, items=codes)
        return None

    def to_array_def(self) -> Optional[ArrayBoundaries]:
        """Returns the array boundaries, if any."""
        if self.maxOccurs and self.maxOccurs > 1:
            m = self.minOccurs if self.minOccurs is not None else 0
            return ArrayBoundaries(m, self.maxOccurs)
        else:
            return None


class JsonLink(msgspec.Struct, frozen=True):
    """SDMX-JSON payload for link objects."""

    urn: str
    rel: Optional[str] = None


class JsonHeader(msgspec.Struct, frozen=True):
    """SDMX-JSON payload for message header."""

    links: Sequence[JsonLink] = ()

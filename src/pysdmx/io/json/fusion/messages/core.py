"""Collection of Fusion-JSON schemas for common artefacts."""

from datetime import datetime
from typing import Any, Optional, Sequence, Union

import msgspec

from pysdmx.model import ArrayBoundaries, Codelist, Facets
from pysdmx.util import find_by_urn


class FusionAnnotation(msgspec.Struct, frozen=True):
    """Fusion-JSON payload for annotations."""

    title: str
    type: str


class FusionString(msgspec.Struct, frozen=True):
    """Fusion-JSON payload for an international string."""

    locale: str
    value: str


class FusionLink(msgspec.Struct, frozen=True):
    """Fusion-JSON payload for link objects."""

    urn: str


class FusionTextFormat(msgspec.Struct, frozen=True):
    """Fusion-JSON payload for TextFormat."""

    textType: str
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


class FusionRepresentation(msgspec.Struct, frozen=True):
    """Fusion-JSON payload for core representation."""

    textFormat: Optional[FusionTextFormat] = None
    representation: Optional[str] = None
    minOccurs: Optional[int] = None
    maxOccurs: Optional[int] = None

    def to_facets(self) -> Optional[Facets]:
        """Return a Facets domain object."""
        if self.textFormat and (
            self.textFormat.minLength
            or self.textFormat.maxLength
            or self.textFormat.isSequence
            or self.textFormat.minValue
            or self.textFormat.maxValue
            or self.textFormat.startValue
            or self.textFormat.endValue
            or self.textFormat.decimals
            or self.textFormat.pattern
            or self.textFormat.startTime
            or self.textFormat.endTime
        ):
            return Facets(
                min_length=self.textFormat.minLength,
                max_length=self.textFormat.maxLength,
                is_sequence=self.textFormat.isSequence,
                min_value=self.textFormat.minValue,
                max_value=self.textFormat.maxValue,
                start_value=self.textFormat.startValue,
                end_value=self.textFormat.endValue,
                decimals=self.textFormat.decimals,
                pattern=self.textFormat.pattern,
                start_time=self.textFormat.startTime,
                end_time=self.textFormat.endTime,
            )
        else:
            return None

    def to_enumeration(
        self,
        codelists: Sequence[Any],
        valid: Sequence[str],
    ) -> Optional[Codelist]:
        """Returns the list of codes allowed for this component."""
        if self.representation:
            a = find_by_urn(codelists, self.representation)
            cl = a.to_model()
            codes = [
                c.to_model() for c in a.items if not valid or c.id in valid
            ]
            return msgspec.structs.replace(cl, items=codes)
        return None

    def to_array_def(self) -> Optional[ArrayBoundaries]:
        """Returns the array boundaries, if any."""
        if self.maxOccurs and self.maxOccurs > 1:
            m = self.minOccurs if self.minOccurs is not None else 0
            return ArrayBoundaries(m, self.maxOccurs)
        else:
            return None

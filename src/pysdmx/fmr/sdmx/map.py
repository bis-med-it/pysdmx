"""Collection of SDMX-JSON schemas for structure map queries."""

from datetime import datetime as dt, timezone as tz
import re
from typing import Any, Optional, Sequence, Union

from msgspec import Struct

from pysdmx.model import (
    ComponentMapper,
    DatePatternMap,
    ImplicitMapper,
    MappingDefinition,
    MultipleComponentMapper,
    MultipleValueMap,
    ValueMap,
    ValueSetter,
)
from pysdmx.util import find_by_urn


class JsonSourceValue(Struct, frozen=True):
    """SDMX-JSON payload for a source value."""

    value: str
    isRegEx: bool = False

    def to_model(self) -> Union[str, re.Pattern[str]]:
        """Returns the requested source value."""
        if self.isRegEx:
            return re.compile(self.value)
        else:
            return self.value


class JsonRepresentationMapping(Struct, frozen=True):
    """SDMX-JSON payload for a representation mapping."""

    sourceValues: Sequence[JsonSourceValue]
    targetValues: Sequence[str]
    validFrom: Optional[str] = None
    validTo: Optional[str] = None

    def __get_dt(self, inp: str) -> dt:
        return dt.fromisoformat(inp).replace(tzinfo=tz.utc)

    def to_model(self, is_multi: bool) -> Union[MultipleValueMap, ValueMap]:
        """Returns the requested value maps."""
        if is_multi:
            return MultipleValueMap(
                [src.to_model() for src in self.sourceValues],
                self.targetValues,
                self.__get_dt(self.validFrom) if self.validFrom else None,
                self.__get_dt(self.validTo) if self.validTo else None,
            )
        else:
            return ValueMap(
                self.sourceValues[0].to_model(),
                self.targetValues[0],
                self.__get_dt(self.validFrom) if self.validFrom else None,
                self.__get_dt(self.validTo) if self.validTo else None,
            )


class JsonRepresentationMap(
    Struct,
    frozen=True,
    rename={"agency": "agencyID"},
):
    """SDMX-JSON payload for a representation map."""

    id: str
    agency: str
    version: str
    representationMappings: Sequence[JsonRepresentationMapping]

    def to_model(
        self, is_multi: bool = False
    ) -> Sequence[Union[MultipleValueMap, ValueMap]]:
        """Returns the requested value maps."""
        return [rm.to_model(is_multi) for rm in self.representationMappings]


class JsonFixedValueMap(Struct, frozen=True):
    """SDMX-JSON payload for a fixed value map."""

    target: str
    values: Sequence[Any]

    def to_model(self) -> ValueSetter:
        """Returns the requested fixed value map."""
        return ValueSetter(self.target, self.values[0])


class JsonComponentMap(Struct, frozen=True):
    """SDMX-JSON payload for a component map."""

    source: Sequence[str]
    target: Sequence[str]
    representationMap: Optional[str] = None

    def to_model(
        self, rms: Sequence[JsonRepresentationMap]
    ) -> Union[ComponentMapper, MultipleComponentMapper, ImplicitMapper]:
        """Returns the requested map."""
        if self.representationMap:
            rm = find_by_urn(rms, self.representationMap)
            if len(self.source) == 1 and len(self.target) == 1:
                return ComponentMapper(
                    self.source[0],
                    self.target[0],
                    rm.to_model(),
                )
            else:
                return MultipleComponentMapper(
                    self.source, self.target, rm.to_model(True)
                )
        else:
            return ImplicitMapper(self.source[0], self.target[0])


class JsonMappedPair(Struct, frozen=True):
    """SDMX-JSON payload for a pair of mapped components."""

    source: str
    target: str


class JsonDatePatternMap(Struct, frozen=True):
    """SDMX-JSON payload for a date pattern map."""

    sourcePattern: str
    mappedComponents: Sequence[JsonMappedPair]
    locale: str
    id: Optional[str] = None
    targetFrequencyID: Optional[str] = None
    frequencyDimension: Optional[str] = None

    def to_model(self) -> DatePatternMap:
        """Returns the requested date mapper."""
        freq = (
            self.targetFrequencyID
            if self.targetFrequencyID
            else self.frequencyDimension
        )
        typ = "fixed" if self.targetFrequencyID else "variable"
        return DatePatternMap(
            self.mappedComponents[0].source,
            self.mappedComponents[0].target,
            self.sourcePattern,
            freq,
            self.id,
            self.locale,
            typ,
        )


class JsonStructureMap(Struct, frozen=True):
    """SDMX-JSON payload for a structure map."""

    datePatternMaps: Sequence[JsonDatePatternMap] = ()
    componentMaps: Sequence[JsonComponentMap] = ()
    fixedValueMaps: Sequence[JsonFixedValueMap] = ()

    def to_model(
        self,
        rms: Sequence[JsonRepresentationMap],
    ) -> MappingDefinition:
        """Returns the requested mapping definition."""
        m1 = [dpm.to_model() for dpm in self.datePatternMaps]
        m2 = [cm.to_model(rms) for cm in self.componentMaps]
        m3 = [fvm.to_model() for fvm in self.fixedValueMaps]
        m4 = [m for m in m2 if isinstance(m, ImplicitMapper)]
        m5 = [m for m in m2 if isinstance(m, MultipleComponentMapper)]
        m6 = [m for m in m2 if isinstance(m, ComponentMapper)]

        return MappingDefinition(
            component_maps=m6,
            date_maps=m1,
            fixed_value_maps=m3,
            implicit_maps=m4,
            multiple_component_maps=m5,
        )


class JsonStructureMaps(Struct, frozen=True):
    """SDMX-JSON payload for structure maps."""

    structureMaps: Sequence[JsonStructureMap]
    representationMaps: Sequence[JsonRepresentationMap] = ()

    def to_model(self) -> MappingDefinition:
        """Returns the requested mapping definition."""
        return self.structureMaps[0].to_model(self.representationMaps)


class JsonMappingMessage(Struct, frozen=True):
    """SDMX-JSON payload for /structuremap queries."""

    data: JsonStructureMaps

    def to_model(self) -> MappingDefinition:
        """Returns the requested mapping definition."""
        return self.data.to_model()


class JsonRepresentationMaps(Struct, frozen=True):
    """SDMX-JSON payload for representation maps."""

    representationMaps: Sequence[JsonRepresentationMap]

    def to_model(self) -> Sequence[ValueMap]:
        """Returns the requested mapping definition."""
        out = self.representationMaps[0].to_model()
        return out  # type: ignore[return-value]


class JsonRepresentationMapMessage(Struct, frozen=True):
    """SDMX-JSON payload for /representationmap queries."""

    data: JsonRepresentationMaps

    def to_model(self) -> Sequence[ValueMap]:
        """Returns the requested representation map."""
        return self.data.to_model()

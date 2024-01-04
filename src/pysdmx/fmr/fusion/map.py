"""Collection of Fusion-JSON schemas for structure map queries."""

from datetime import datetime as dt, timezone as tz
import re
from typing import Any, Dict, Optional, Sequence, Union

from msgspec import Struct

from pysdmx.model import (
    ComponentMapper,
    FixedDatePatternMap,
    ImplicitMapper,
    MappingDefinition,
    MultipleComponentMapper,
    MultipleValueMap,
    ValueMap,
    ValueSetter,
)
from pysdmx.util import find_by_urn


class FusionSourceValue(Struct, frozen=True):
    """Fusion-JSON payload for a source value."""

    value: str
    regEx: bool = False

    def to_model(self) -> Union[str, re.Pattern[str]]:
        """Returns the requested source value."""
        if self.regEx:
            return re.compile(self.value)
        else:
            return self.value


class FusionRepresentationMapping(Struct, frozen=True):
    """Fusion-JSON payload for a representation mapping."""

    source: Sequence[FusionSourceValue]
    target: Sequence[str]
    validFrom: Optional[str] = None
    validTo: Optional[str] = None

    def __get_dt(self, inp: str) -> dt:
        if inp.endswith("Z"):
            inp = inp[0:-1]
        return dt.fromisoformat(inp).replace(tzinfo=tz.utc)

    def to_model(self, is_multi: bool) -> Union[MultipleValueMap, ValueMap]:
        """Returns the requested value maps."""
        if is_multi:
            return MultipleValueMap(
                [src.to_model() for src in self.source],
                self.target,
                self.__get_dt(self.validFrom) if self.validFrom else None,
                self.__get_dt(self.validTo) if self.validTo else None,
            )
        else:
            return ValueMap(
                self.source[0].to_model(),
                self.target[0],
                self.__get_dt(self.validFrom) if self.validFrom else None,
                self.__get_dt(self.validTo) if self.validTo else None,
            )


class FusionRepresentationMap(
    Struct,
    frozen=True,
    rename={"agency": "agencyId"},
):
    """Fusion-JSON payload for a representation map."""

    id: str
    agency: str
    version: str
    mappedRelationships: Sequence[FusionRepresentationMapping]

    def to_model(
        self,
        is_multi: bool = False,
    ) -> Sequence[Union[MultipleValueMap, ValueMap]]:
        """Returns the requested value maps."""
        return [rm.to_model(is_multi) for rm in self.mappedRelationships]


class FusionComponentMap(Struct, frozen=True):
    """Fusion-JSON payload for a component map."""

    sources: Sequence[str]
    targets: Sequence[str]
    representationMapRef: Optional[str] = None

    def to_model(
        self, rms: Sequence[FusionRepresentationMap]
    ) -> Union[ComponentMapper, MultipleComponentMapper, ImplicitMapper]:
        """Returns the requested component map."""
        if self.representationMapRef:
            rm = find_by_urn(rms, self.representationMapRef)
            if len(self.sources) == 1 and len(self.targets) == 1:
                return ComponentMapper(
                    self.sources[0],
                    self.targets[0],
                    rm.to_model(),
                )
            else:
                return MultipleComponentMapper(
                    self.sources, self.targets, rm.to_model(True)
                )
        else:
            return ImplicitMapper(self.sources[0], self.targets[0])


class FusionTimePatternMap(Struct, frozen=True):
    """Fusion-JSON payload for a date pattern map."""

    source: str
    target: str
    freqId: str
    pattern: str

    def to_model(self) -> FixedDatePatternMap:
        """Returns the requested date mapper."""
        return FixedDatePatternMap(
            self.source,
            self.target,
            self.pattern,
            self.freqId,
        )


class FusionStructureMap(Struct, frozen=True):
    """Fusion-JSON payload for a structure map."""

    fixedOutput: Dict[str, Any] = {}
    timePatternMaps: Sequence[FusionTimePatternMap] = ()
    componentMaps: Sequence[FusionComponentMap] = ()

    def to_model(
        self,
        rms: Sequence[FusionRepresentationMap],
    ) -> MappingDefinition:
        """Returns the requested mapping definition."""
        m1 = [tpm.to_model() for tpm in self.timePatternMaps]
        m2 = [cm.to_model(rms) for cm in self.componentMaps]
        m3 = [ValueSetter(k, v) for k, v in self.fixedOutput.items()]
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


class FusionMappingMessage(Struct, frozen=True):
    """Fusion-JSON payload for /structuremap queries."""

    StructureMap: Sequence[FusionStructureMap]
    RepresentationMap: Sequence[FusionRepresentationMap] = ()

    def to_model(self) -> MappingDefinition:
        """Returns the requested mapping definition."""
        return self.StructureMap[0].to_model(self.RepresentationMap)


class FusionRepresentationMapMessage(Struct, frozen=True):
    """Fusion-JSON payload for /representationmap queries."""

    RepresentationMap: Sequence[FusionRepresentationMap]

    def to_model(self) -> MappingDefinition:
        """Returns the requested mapping definition."""
        out = self.RepresentationMap[0].to_model()
        return out  # type: ignore[return-value]

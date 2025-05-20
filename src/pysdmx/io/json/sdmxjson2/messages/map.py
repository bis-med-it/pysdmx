"""Collection of SDMX-JSON schemas for structure map queries."""

from datetime import datetime as dt
from datetime import timezone as tz
from typing import Any, Dict, Literal, Optional, Sequence, Union

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.core import (
    JsonAnnotation,
    MaintainableType,
)
from pysdmx.model import (
    ComponentMap,
    DataType,
    DatePatternMap,
    FixedValueMap,
    ImplicitComponentMap,
    MultiComponentMap,
    MultiRepresentationMap,
    MultiValueMap,
    RepresentationMap,
    StructureMap,
    ValueMap,
)
from pysdmx.util import find_by_urn


class JsonSourceValue(Struct, frozen=True):
    """SDMX-JSON payload for a source value."""

    value: str
    isRegEx: bool = False

    def to_model(self) -> str:
        """Returns the requested source value."""
        if self.isRegEx:
            return f"regex:{self.value}"
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

    def to_model(self, is_multi: bool) -> Union[MultiValueMap, ValueMap]:
        """Returns the requested value maps."""
        if is_multi:
            return MultiValueMap(
                source=[src.to_model() for src in self.sourceValues],
                target=self.targetValues,
                valid_from=(
                    self.__get_dt(self.validFrom) if self.validFrom else None
                ),
                valid_to=self.__get_dt(self.validTo) if self.validTo else None,
            )
        else:
            return ValueMap(
                source=self.sourceValues[0].to_model(),
                target=self.targetValues[0],
                valid_from=(
                    self.__get_dt(self.validFrom) if self.validFrom else None
                ),
                valid_to=self.__get_dt(self.validTo) if self.validTo else None,
            )


class JsonRepresentationMap(MaintainableType, frozen=True):
    """SDMX-JSON payload for a representation map."""

    source: Sequence[Dict[str, str]] = ()
    target: Sequence[Dict[str, str]] = ()
    representationMappings: Sequence[JsonRepresentationMapping] = ()

    def __parse_st(self, item: Dict[str, str]) -> Union[DataType, str]:
        if "dataType" in item:
            return DataType(item["dataType"])
        elif "valuelist" in item:
            return item["valuelist"]
        else:
            return item["codelist"]

    def to_model(
        self, is_multi: bool = False
    ) -> Union[MultiRepresentationMap, RepresentationMap]:
        """Returns the requested value maps."""
        mrs = [rm.to_model(is_multi) for rm in self.representationMappings]
        s = [self.__parse_st(i) for i in self.source]
        t = [self.__parse_st(j) for j in self.target]
        if is_multi:
            return MultiRepresentationMap(
                id=self.id,
                name=self.name,
                agency=self.agency,
                source=s,
                target=t,
                maps=mrs,  # type: ignore[arg-type]
                description=self.description,
                version=self.version,
            )
        else:
            return RepresentationMap(
                id=self.id,
                name=self.name,
                agency=self.agency,
                source=s[0],
                target=t[0],
                maps=mrs,  # type: ignore[arg-type]
                description=self.description,
                version=self.version,
            )


class JsonFixedValueMap(Struct, frozen=True):
    """SDMX-JSON payload for a fixed value map."""

    values: Sequence[Any]
    source: Optional[str] = None
    target: Optional[str] = None

    def to_model(self) -> FixedValueMap:
        """Returns the requested fixed value map."""
        located_in = "source" if self.source else "target"
        target = self.target if self.target else self.source
        return FixedValueMap(
            target,  # type: ignore[arg-type]
            self.values[0],
            located_in,  # type: ignore[arg-type]
        )


class JsonComponentMap(Struct, frozen=True):
    """SDMX-JSON payload for a component map."""

    source: Sequence[str]
    target: Sequence[str]
    representationMap: Optional[str] = None

    def to_model(
        self, rms: Sequence[JsonRepresentationMap]
    ) -> Union[ComponentMap, MultiComponentMap, ImplicitComponentMap]:
        """Returns the requested map."""
        if self.representationMap:
            mult = len(self.source) > 1 or len(self.target) > 1
            if rms:
                rm = find_by_urn(rms, self.representationMap)
                rm = rm.to_model(mult)
            else:
                rm = self.representationMap
            if mult:
                return MultiComponentMap(self.source, self.target, rm)
            else:
                return ComponentMap(self.source[0], self.target[0], rm)
        else:
            return ImplicitComponentMap(self.source[0], self.target[0])


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
    resolvePeriod: Optional[
        Literal["startOfPeriod", "endOfPeriod", "midPeriod"]
    ] = None
    targetFrequencyID: Optional[str] = None
    frequencyDimension: Optional[str] = None
    mappedFrequencies: Optional[Sequence[str]] = None
    annotations: Optional[Sequence[JsonAnnotation]] = None

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
            freq,  # type: ignore[arg-type]
            self.id,
            self.locale,
            typ,  # type: ignore[arg-type]
            self.resolvePeriod,
        )


class JsonStructureMap(MaintainableType, frozen=True):
    """SDMX-JSON payload for a structure map."""

    source: str = ""
    target: str = ""
    datePatternMaps: Sequence[JsonDatePatternMap] = ()
    componentMaps: Sequence[JsonComponentMap] = ()
    fixedValueMaps: Sequence[JsonFixedValueMap] = ()

    def to_model(
        self,
        rms: Sequence[JsonRepresentationMap],
    ) -> StructureMap:
        """Returns the requested mapping definition."""
        m1 = tuple([dpm.to_model() for dpm in self.datePatternMaps])
        m2 = tuple([cm.to_model(rms) for cm in self.componentMaps])
        m3 = tuple([fvm.to_model() for fvm in self.fixedValueMaps])
        return StructureMap(
            id=self.id,
            name=self.name,
            agency=self.agency,
            source=self.source,
            target=self.target,
            maps=m1 + m2 + m3,
            description=self.description,
            version=self.version,
            annotations=[a.to_model() for a in self.annotations],
            is_external_reference=self.isExternalReference,
            valid_from=self.validFrom,
            valid_to=self.validTo,
        )


class JsonStructureMaps(Struct, frozen=True):
    """SDMX-JSON payload for structure maps."""

    structureMaps: Sequence[JsonStructureMap]
    representationMaps: Sequence[JsonRepresentationMap] = ()

    def to_model(self) -> Sequence[StructureMap]:
        """Returns the requested mapping definition."""
        return [
            sm.to_model(self.representationMaps) for sm in self.structureMaps
        ]


class JsonMappingMessage(Struct, frozen=True):
    """SDMX-JSON payload for /structuremap queries."""

    data: JsonStructureMaps

    def to_model(self) -> StructureMap:
        """Returns the requested mapping definition."""
        return self.data.to_model()[0]


class JsonStructureMapsMessage(Struct, frozen=True):
    """SDMX-JSON payload for generic /structuremap queries."""

    data: JsonStructureMaps

    def to_model(self) -> Sequence[StructureMap]:
        """Returns the requested mapping definition."""
        return self.data.to_model()


class JsonRepresentationMaps(Struct, frozen=True):
    """SDMX-JSON payload for representation maps."""

    representationMaps: Sequence[JsonRepresentationMap]

    def to_model(
        self,
    ) -> Sequence[Union[MultiRepresentationMap, RepresentationMap]]:
        """Returns the requested mapping definition."""
        maps = []
        for m in self.representationMaps:
            multi = bool(len(m.source) > 1 or len(m.target) > 1)
            maps.append(m.to_model(multi))
        return maps


class JsonRepresentationMapMessage(Struct, frozen=True):
    """SDMX-JSON payload for /representationmap queries."""

    data: JsonRepresentationMaps

    def to_model(self) -> Union[MultiRepresentationMap, RepresentationMap]:
        """Returns the requested representation map."""
        return self.data.to_model()[0]


class JsonRepresentationMapsMessage(Struct, frozen=True):
    """SDMX-JSON payload for /representationmap queries."""

    data: JsonRepresentationMaps

    def to_model(
        self,
    ) -> Sequence[Union[MultiRepresentationMap, RepresentationMap]]:
        """Returns the requested representation maps."""
        return self.data.to_model()

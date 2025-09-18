"""Collection of SDMX-JSON schemas for structure map queries."""

from datetime import datetime as dt
from datetime import timezone as tz
from typing import Any, Dict, Literal, Optional, Sequence, Union

from msgspec import Struct

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.core import (
    JsonAnnotation,
    MaintainableType,
)
from pysdmx.model import (
    Agency,
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


class JsonSourceValue(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a source value."""

    value: str
    isRegEx: bool = False

    def to_model(self) -> str:
        """Returns the requested source value."""
        if self.isRegEx:
            return f"regex:{self.value}"
        else:
            return self.value

    @classmethod
    def from_model(self, value: str) -> "JsonSourceValue":
        """Converts a pysdmx source string value to an SDMX-JSON one."""
        if value.startswith("regex:"):
            return JsonSourceValue(value.replace("regex:", ""), True)
        else:
            return JsonSourceValue(value)


class JsonRepresentationMapping(Struct, frozen=True, omit_defaults=True):
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

    @classmethod
    def from_model(
        self, vm: Union[MultiValueMap, ValueMap]
    ) -> "JsonRepresentationMapping":
        """Converts a value map to an SDMX-JSON JsonRepresentationMapping."""
        if isinstance(vm, ValueMap):
            return JsonRepresentationMapping(
                [JsonSourceValue.from_model(vm.source)],
                [vm.target],
                vm.valid_from.strftime("%Y-%m-%d") if vm.valid_from else None,
                vm.valid_to.strftime("%Y-%m-%d") if vm.valid_to else None,
            )
        else:
            return JsonRepresentationMapping(
                [JsonSourceValue.from_model(s) for s in vm.source],
                vm.target,
                vm.valid_from.strftime("%Y-%m-%d") if vm.valid_from else None,
                vm.valid_to.strftime("%Y-%m-%d") if vm.valid_to else None,
            )


class JsonRepresentationMap(MaintainableType, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a representation map."""

    source: Sequence[Dict[str, str]] = ()
    target: Sequence[Dict[str, str]] = ()
    representationMappings: Sequence[JsonRepresentationMapping] = ()

    def __parse_st(self, item: Dict[str, str]) -> Union[DataType, str]:
        if "dataType" in item:
            return DataType(item["dataType"])
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

    @classmethod
    def from_model(
        self, rm: Union[MultiRepresentationMap, RepresentationMap]
    ) -> "JsonRepresentationMap":
        """Converts a pysdmx representation map to an SDMX-JSON one."""

        def __convert_st(st: str) -> Dict[str, str]:
            if "Codelist" in st or "ValueList" in st:
                return {"codelist": st}
            else:
                return {"dataType": st}

        if not rm.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON representation maps must have a name",
                {"representation_map": rm.id},
            )

        if isinstance(rm, RepresentationMap):
            source = [__convert_st(rm.source)] if rm.source else []
            target = [__convert_st(rm.target)] if rm.target else []
        else:
            source = [__convert_st(s) for s in rm.source]
            target = [__convert_st(t) for t in rm.target]
        return JsonRepresentationMap(
            agency=(
                rm.agency.id if isinstance(rm.agency, Agency) else rm.agency
            ),
            id=rm.id,
            name=rm.name,
            version=rm.version,
            isExternalReference=rm.is_external_reference,
            validFrom=rm.valid_from,
            validTo=rm.valid_to,
            description=rm.description,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in rm.annotations]
            ),
            source=tuple(source),
            target=tuple(target),
            representationMappings=tuple(
                [JsonRepresentationMapping.from_model(m) for m in rm.maps]
            ),
        )


class JsonFixedValueMap(Struct, frozen=True, omit_defaults=True):
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

    @classmethod
    def from_model(self, fvm: FixedValueMap) -> "JsonFixedValueMap":
        """Converts a pysdmx fixed value map to an SDMX-JSON one."""
        return JsonFixedValueMap(
            values=[fvm.value],
            source=fvm.target if fvm.located_in == "source" else None,
            target=fvm.target if fvm.located_in == "target" else None,
        )


class JsonComponentMap(Struct, frozen=True, omit_defaults=True):
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

    @classmethod
    def from_model(
        self, cm: Union[ComponentMap, MultiComponentMap, ImplicitComponentMap]
    ) -> "JsonComponentMap":
        """Converts a pysdmx component map to an SDMX-JSON one."""
        if isinstance(cm, ImplicitComponentMap):
            return JsonComponentMap([cm.source], [cm.target])
        elif isinstance(cm, ComponentMap):
            rm = (
                (
                    "urn:sdmx:org.sdmx.infomodel.structuremapping."
                    f"{cm.values.short_urn}"
                )
                if isinstance(cm.values, RepresentationMap)
                else cm.values
            )
            return JsonComponentMap([cm.source], [cm.target], rm)
        else:
            rm = (
                (
                    "urn:sdmx:org.sdmx.infomodel.structuremapping."
                    f"{cm.values.short_urn}"
                )
                if isinstance(cm.values, MultiRepresentationMap)
                else cm.values
            )
            return JsonComponentMap(cm.source, cm.target, rm)


class JsonMappedPair(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a pair of mapped components."""

    source: str
    target: str


class JsonDatePatternMap(Struct, frozen=True, omit_defaults=True):
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
            source=self.mappedComponents[0].source,
            target=self.mappedComponents[0].target,
            pattern=self.sourcePattern,
            frequency=freq,  # type: ignore[arg-type]
            id=self.id,
            locale=self.locale,
            pattern_type=typ,  # type: ignore[arg-type]
            resolve_period=self.resolvePeriod,
        )

    @classmethod
    def from_model(self, dpm: DatePatternMap) -> "JsonDatePatternMap":
        """Converts a pysdmx date pattern map to an SDMX-JSON one."""
        if dpm.pattern_type == "fixed":
            tf = dpm.frequency
            fd = None
        else:
            tf = None
            fd = dpm.frequency

        return JsonDatePatternMap(
            sourcePattern=dpm.pattern,
            mappedComponents=[JsonMappedPair(dpm.source, dpm.target)],
            locale=dpm.locale,
            id=dpm.id,
            resolvePeriod=dpm.resolve_period,
            targetFrequencyID=tf,
            frequencyDimension=fd,
        )


class JsonStructureMap(MaintainableType, frozen=True, omit_defaults=True):
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

    @classmethod
    def from_model(self, sm: StructureMap) -> "JsonStructureMap":
        """Converts a pysdmx structure map to an SDMX-JSON one."""
        cms = list(sm.component_maps)
        cms.extend(list(sm.implicit_component_maps))  # type: ignore[arg-type]
        cms.extend(list(sm.multi_component_maps))  # type: ignore[arg-type]
        if not sm.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON structure maps must have a name",
                {"structure_map": sm.id},
            )
        return JsonStructureMap(
            agency=(
                sm.agency.id if isinstance(sm.agency, Agency) else sm.agency
            ),
            id=sm.id,
            name=sm.name,
            version=sm.version,
            isExternalReference=sm.is_external_reference,
            validFrom=sm.valid_from,
            validTo=sm.valid_to,
            description=sm.description,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in sm.annotations]
            ),
            source=sm.source,
            target=sm.target,
            datePatternMaps=tuple(
                [
                    JsonDatePatternMap.from_model(dpm)
                    for dpm in sm.date_pattern_maps
                ]
            ),
            componentMaps=tuple(
                [JsonComponentMap.from_model(cm) for cm in cms]
            ),
            fixedValueMaps=tuple(
                [
                    JsonFixedValueMap.from_model(fvm)
                    for fvm in sm.fixed_value_maps
                ]
            ),
        )


class JsonStructureMaps(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for structure maps."""

    structureMaps: Sequence[JsonStructureMap]
    representationMaps: Sequence[JsonRepresentationMap] = ()

    def to_model(self) -> Sequence[StructureMap]:
        """Returns the requested mapping definition."""
        return [
            sm.to_model(self.representationMaps) for sm in self.structureMaps
        ]


class JsonMappingMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for /structuremap queries."""

    data: JsonStructureMaps

    def to_model(self) -> StructureMap:
        """Returns the requested mapping definition."""
        return self.data.to_model()[0]


class JsonStructureMapsMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for generic /structuremap queries."""

    data: JsonStructureMaps

    def to_model(self) -> Sequence[StructureMap]:
        """Returns the requested mapping definition."""
        return self.data.to_model()


class JsonRepresentationMaps(Struct, frozen=True, omit_defaults=True):
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


class JsonRepresentationMapMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for /representationmap queries."""

    data: JsonRepresentationMaps

    def to_model(self) -> Union[MultiRepresentationMap, RepresentationMap]:
        """Returns the requested representation map."""
        return self.data.to_model()[0]


class JsonRepresentationMapsMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for /representationmap queries."""

    data: JsonRepresentationMaps

    def to_model(
        self,
    ) -> Sequence[Union[MultiRepresentationMap, RepresentationMap]]:
        """Returns the requested representation maps."""
        return self.data.to_model()

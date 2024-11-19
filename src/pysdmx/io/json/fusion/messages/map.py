"""Collection of Fusion-JSON schemas for structure map queries."""

from datetime import datetime as dt, timezone as tz
import re
from typing import Any, Dict, Optional, Sequence, Union

from msgspec import Struct

from pysdmx.io.json.fusion.messages.core import FusionString
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
    StructureMap as SM,
    ValueMap,
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

    def to_model(self, is_multi: bool) -> Union[MultiValueMap, ValueMap]:
        """Returns the requested value maps."""
        if is_multi:
            return MultiValueMap(
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
    names: Sequence[FusionString]
    agency: str
    version: str
    sources: Sequence[str]
    targets: Sequence[str]
    mappedRelationships: Sequence[FusionRepresentationMapping]
    descriptions: Sequence[FusionString] = ()

    def to_model(
        self, is_multi: bool = False
    ) -> Union[MultiRepresentationMap, RepresentationMap]:
        """Returns the requested representation map."""
        mrs = [rm.to_model(is_multi) for rm in self.mappedRelationships]
        s = [i if i.startswith("urn:") else DataType(i) for i in self.sources]
        t = [j if j.startswith("urn:") else DataType(j) for j in self.targets]
        if is_multi:
            return MultiRepresentationMap(
                id=self.id,
                name=self.names[0].value,
                agency=self.agency,
                source=s,
                target=t,
                maps=mrs,  # type: ignore[arg-type]
                description=(
                    self.descriptions[0].value if self.descriptions else None
                ),
                version=self.version,
            )
        else:
            return RepresentationMap(
                id=self.id,
                name=self.names[0].value,
                agency=self.agency,
                source=s[0],
                target=t[0],
                maps=mrs,  # type: ignore[arg-type]
                description=(
                    self.descriptions[0].value if self.descriptions else None
                ),
                version=self.version,
            )


class FusionComponentMap(Struct, frozen=True):
    """Fusion-JSON payload for a component map."""

    sources: Sequence[str]
    targets: Sequence[str]
    representationMapRef: Optional[str] = None

    def to_model(
        self, rms: Sequence[FusionRepresentationMap]
    ) -> Union[ComponentMap, MultiComponentMap, ImplicitComponentMap]:
        """Returns the requested component map."""
        if self.representationMapRef:
            rm = find_by_urn(rms, self.representationMapRef)
            if len(self.sources) == 1 and len(self.targets) == 1:
                return ComponentMap(
                    self.sources[0],
                    self.targets[0],
                    rm.to_model(),
                )
            else:
                return MultiComponentMap(
                    self.sources, self.targets, rm.to_model(True)
                )
        else:
            return ImplicitComponentMap(self.sources[0], self.targets[0])


class FusionTimePatternMap(Struct, frozen=True):
    """Fusion-JSON payload for a date pattern map."""

    source: str
    target: str
    pattern: str
    locale: str
    freqId: Optional[str] = None
    freqDim: Optional[str] = None
    id: Optional[str] = None

    def to_model(self) -> DatePatternMap:
        """Returns the requested date mapper."""
        freq = self.freqId if self.freqId else self.freqDim
        typ = "fixed" if self.freqId else "variable"
        return DatePatternMap(
            self.source,
            self.target,
            self.pattern,
            freq,  # type: ignore[arg-type]
            self.id,
            self.locale,
            typ,  # type: ignore[arg-type]
        )


class FusionStructureMap(Struct, frozen=True):
    """Fusion-JSON payload for a structure map."""

    id: str
    agencyId: str
    version: str
    source: str
    target: str
    names: Sequence[FusionString] = ()
    descriptions: Sequence[FusionString] = ()
    fixedInput: Dict[str, Any] = {}
    fixedOutput: Dict[str, Any] = {}
    timePatternMaps: Sequence[FusionTimePatternMap] = ()
    componentMaps: Sequence[FusionComponentMap] = ()

    def to_model(
        self,
        rms: Sequence[FusionRepresentationMap],
    ) -> SM:
        """Returns the requested mapping definition."""
        m1 = tuple(tpm.to_model() for tpm in self.timePatternMaps)
        m2 = tuple(cm.to_model(rms) for cm in self.componentMaps)
        m3 = tuple(FixedValueMap(k, v) for k, v in self.fixedOutput.items())
        m4 = tuple(
            FixedValueMap(k, v, "source") for k, v in self.fixedInput.items()
        )

        return SM(
            id=self.id,
            name=self.names[0].value,
            agency=self.agencyId,
            source=self.source,
            target=self.target,
            maps=m1 + m2 + m3 + m4,
            description=(
                self.descriptions[0].value if self.descriptions else None
            ),
            version=self.version,
        )


class FusionMappingMessage(Struct, frozen=True):
    """Fusion-JSON payload for /structuremap queries."""

    StructureMap: Sequence[FusionStructureMap]
    RepresentationMap: Sequence[FusionRepresentationMap] = ()

    def to_model(self) -> SM:
        """Returns the requested mapping definition."""
        return self.StructureMap[0].to_model(self.RepresentationMap)


class FusionRepresentationMapMessage(Struct, frozen=True):
    """Fusion-JSON payload for /representationmap queries."""

    RepresentationMap: Sequence[FusionRepresentationMap]

    def to_model(self) -> SM:
        """Returns the requested mapping definition."""
        m = self.RepresentationMap[0]
        multi = bool(len(m.sources) > 1 or len(m.targets) > 1)
        out = m.to_model(multi)
        return out  # type: ignore[return-value]

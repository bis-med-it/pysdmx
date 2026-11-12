"""Collection of Fusion-JSON schemas for content constraints."""

from typing import Dict, List, Optional, Sequence, Union

from msgspec import Struct

from pysdmx.io.json.fusion.messages.core import FusionString
from pysdmx.model import (
    AvailabilityConstraint,
    ConstraintAttachment,
    CubeKeyValue,
    CubeRegion,
    CubeValue,
    DataKey,
    DataKeyValue,
    KeySet,
)
from pysdmx.model import (
    DataConstraint as DC,
)


class FusionKeyValue(Struct, frozen=True):
    """Fusion-JSON payload for the list of allowed values per component."""

    values: Sequence[str]


class FusionKeySet(Struct, frozen=True):
    """Fusion-JSON payload for the list of allowed values per component."""

    dims: Sequence[str]
    rows: Sequence[Sequence[str]]

    def to_model(self, is_included: bool) -> KeySet:
        """Converts a Fusion KeySet to a KeySet."""
        keys = []
        for r in self.rows:
            kv = [DataKeyValue(self.dims[idx], v) for idx, v in enumerate(r)]
            keys.append(DataKey(kv))
        return KeySet(keys, is_included)


class FusionContentConstraint(Struct, frozen=True):
    """Fusion-JSON payload for a content constraint."""

    includeCube: Dict[str, FusionKeyValue] = {}
    includeSeries: Optional[FusionKeySet] = None
    excludeSeries: Optional[FusionKeySet] = None

    def to_map(self) -> Dict[str, Sequence[str]]:
        """Gets the list of allowed values for a component."""
        return {k: v.values for k, v in self.includeCube.items()}

    def get_included_series(self, dimensions: List[str]) -> Sequence[str]:
        """Get the list of included series defined in the keyset."""
        if self.includeSeries:
            series = []
            for r in self.includeSeries.rows:
                s = dict.fromkeys(dimensions, "*")
                for idx, cd in enumerate(self.includeSeries.dims):
                    s[cd] = r[idx]
                series.append(".".join(s.values()))
            return series
        else:
            return []

    def get_excluded_series(self, dimensions: List[str]) -> Sequence[str]:
        """Get the list of excluded series defined in the keyset."""
        if self.excludeSeries:
            series = []
            for r in self.excludeSeries.rows:
                s = dict.fromkeys(dimensions, "*")
                for idx, cd in enumerate(self.excludeSeries.dims):
                    s[cd] = r[idx]
                series.append(".".join(s.values()))
            return series
        else:
            return []


class FusionDataConstraint(Struct, frozen=True, rename={"agency": "agencyId"}):
    """Fusion-JSON payload for a standalone data constraint."""

    id: str
    agency: str
    version: str
    names: Sequence[FusionString] = ()
    descriptions: Sequence[FusionString] = ()
    attachments: Sequence[str] = ()
    includeCube: Dict[str, FusionKeyValue] = {}
    includeSeries: Optional[FusionKeySet] = None
    excludeSeries: Optional[FusionKeySet] = None

    def to_model(self) -> DC:
        """Returns the data constraint domain model."""
        attachment = ConstraintAttachment(
            data_provider=None,
            dataflows=tuple(self.attachments) or None,
        )
        ckv = tuple(
            CubeKeyValue(
                component_id,
                tuple(CubeValue(value) for value in key_value.values),
            )
            for component_id, key_value in self.includeCube.items()
        )
        inc_keyset = (
            self.includeSeries.to_model(True) if self.includeSeries else None
        )
        exc_keyset = (
            self.excludeSeries.to_model(False) if self.excludeSeries else None
        )
        keysets = [ks for ks in [inc_keyset, exc_keyset] if ks is not None]

        return DC(
            id=self.id,
            agency=self.agency,
            version=self.version,
            name=self.names[0].value if self.names else None,
            description=self.descriptions[0].value
            if self.descriptions
            else None,
            constraint_attachment=attachment,
            cube_regions=(CubeRegion(ckv),) if ckv else (),
            key_sets=tuple(keysets),
        )


class FusionDataConstraintMessage(Struct, frozen=True):
    """Fusion-JSON payload for /dataconstraint queries."""

    DataConstraint: Sequence[FusionDataConstraint]

    def to_model(
        self,
    ) -> Sequence[Union[DC, AvailabilityConstraint]]:
        """Returns the requested data constraints."""
        return [constraint.to_model() for constraint in self.DataConstraint]

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

    def to_model(self) -> DC:
        """Returns the data constraint domain model."""
        attachment = ConstraintAttachment(
            data_provider=None,
            dataflows=tuple(self.attachments) or None,
        )
        cube_region = CubeRegion(
            tuple(
                CubeKeyValue(
                    component_id,
                    tuple(CubeValue(value) for value in key_value.values),
                )
                for component_id, key_value in self.includeCube.items()
            )
        )
        return DC(
            id=self.id,
            agency=self.agency,
            version=self.version,
            name=self.names[0].value if self.names else None,
            description=self.descriptions[0].value
            if self.descriptions
            else None,
            constraint_attachment=attachment,
            cube_regions=(cube_region,),
        )


class FusionDataConstraintMessage(Struct, frozen=True):
    """Fusion-JSON payload for /dataconstraint queries."""

    DataConstraint: Sequence[FusionDataConstraint]

    def to_model(
        self,
    ) -> Sequence[Union[DC, AvailabilityConstraint]]:
        """Returns the requested data constraints."""
        return [constraint.to_model() for constraint in self.DataConstraint]

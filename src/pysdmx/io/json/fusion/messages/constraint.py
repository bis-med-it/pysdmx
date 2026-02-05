"""Collection of Fusion-JSON schemas for content constraints."""

from typing import Dict, List, Optional, Sequence

from msgspec import Struct


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

    def to_map(self) -> Dict[str, Sequence[str]]:
        """Gets the list of allowed values for a component."""
        return {k: v.values for k, v in self.includeCube.items()}

    def get_series(self, dimensions: List[str]) -> Sequence[str]:
        """Get the list of series defined in the keyset."""
        if self.includeSeries:
            series = []
            for r in self.includeSeries.rows:
                s = []
                for d in dimensions:
                    try:
                        idx = self.includeSeries.dims.index(d)
                        s.append(r[idx])
                    except ValueError:
                        s.append("*")
                series.append(".".join(s))
            return series
        else:
            return []

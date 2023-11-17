"""Collection of Fusion-JSON schemas for content constraints."""

from typing import Dict, Sequence

from msgspec import Struct


class FusionKeyValue(Struct, frozen=True):
    """Fusion-JSON payload for the list of allowed values per component."""

    values: Sequence[str]


class FusionContentConstraint(Struct, frozen=True):
    """Fusion-JSON payload for a content constraint."""

    includeCube: Dict[str, FusionKeyValue] = {}

    def to_map(self) -> Dict[str, Sequence[str]]:
        """Gets the list of allowed values for a component."""
        return {k: v.values for k, v in self.includeCube.items()}

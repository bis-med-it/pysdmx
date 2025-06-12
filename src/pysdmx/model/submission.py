"""A module to represent a Submission Result."""

from msgspec import Struct


class SubmissionResult(Struct, frozen=True):
    """A class to represent a Submission Result."""

    action: str
    short_urn: str
    status: str

    def __str__(self) -> str:
        """Custom string representation without the class name."""
        processed_output = []
        for attr, value, *_ in self.__rich_repr__():  # type: ignore[misc]
            processed_output.append(f"{attr}: {value}")
        return f"{', '.join(processed_output)}"

    def __repr__(self) -> str:
        """Custom __repr__ that omits empty sequences."""
        attrs = []
        for attr, value, *_ in self.__rich_repr__():  # type: ignore[misc]
            attrs.append(f"{attr}={repr(value)}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"

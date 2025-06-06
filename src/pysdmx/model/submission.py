"""A module to represent a Submission Result."""

from typing import Sequence

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
            # str is taken as a Sequence, so we need to check it's not a str
            if isinstance(value, Sequence) and not isinstance(value, str):
                # Handle non-empty lists
                if value:
                    class_name = value[0].__class__.__name__
                    value = f"{len(value)} {class_name.lower()}s"
                # redundant if check for python 3.9 and lower versions cov
                if not value:
                    continue

            processed_output.append(f"{attr}: {value}")
        return f"{', '.join(processed_output)}"

    def __repr__(self) -> str:
        """Custom __repr__ that omits empty sequences."""
        attrs = []
        for attr, value, *_ in self.__rich_repr__():  # type: ignore[misc]
            # Omit empty sequences
            if isinstance(value, (list, tuple, set)) and not value:
                continue
            attrs.append(f"{attr}={repr(value)}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"

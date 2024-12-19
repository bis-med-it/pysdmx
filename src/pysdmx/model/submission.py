"""A module to represent a Submission Result."""

from msgspec import Struct


class SubmissionResult(Struct, frozen=True):
    """A class to represent a Submission Result."""

    action: str
    short_urn: str
    status: str

    def __str__(self) -> str:
        """Return a string representation of the SubmissionResult."""
        return (
            f"<Submission Result - "
            f"Action: {self.action} - "
            f"Short URN: {self.short_urn} - "
            f"Status: {self.status}>"
        )

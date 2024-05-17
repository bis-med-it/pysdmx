"""SDMX Submission classes."""

from msgspec import Struct


class SubmissionResult(Struct):
    """A class to represent a Submission Result."""

    action: str
    full_id: str
    status: str

    def __str__(self) -> str:
        """Return a string representation of the SubmissionResult."""
        return (
            f"<Submission Result - "
            f"Action: {self.action} - "
            f"Full ID: {self.full_id} - "
            f"Status: {self.status}>"
        )

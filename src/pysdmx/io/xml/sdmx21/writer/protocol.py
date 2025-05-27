from typing import Protocol, Any, Optional

class Writer(Protocol):
    def write(
        self,
        **kwargs: Any
    ) -> Optional[str]:
        """Writer protocol to write the content to the desired format.

        Args:
            **kwargs: The keyword arguments required for writing the content.

        Returns:
            Optional[str]: The XML string if output_path is empty, None otherwise.
        """
        ...
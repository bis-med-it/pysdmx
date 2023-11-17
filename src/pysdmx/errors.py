"""Types of errors that can be returned by pysdmx."""

from typing import Optional


class Error(Exception):
    """Base ``pysdmx`` error class.

    This class is inherited by more specific error classes and so, ideally,
    you should not encounter it directly when calling library functions.
    """

    def __init__(
        self, status: int, title: str, description: Optional[str] = None
    ):
        """Instantiates a new error, with the supplied paramaters."""
        self.status = status
        self.title = title
        self.description = description
        super().__init__(self.description)


class RetriableError(Error):
    """A type of errors that may be resolved after retrying.

    This class is inherited by more specific error classes and so, ideally,
    you should not encounter it directly when calling library functions.
    """


class Unavailable(RetriableError):
    """The targeted service is not available.

    This can be for a variety of reasons such as:

    - A network issue between the client making the call and the targeted
      service
    - The targeted service is temporarily unavailable
    - The targeted service is overloaded and therefore unable to process
      the request

    This type of errors is considered as **retriable** and so clients can
    retry executing the query at a later stage.
    """


class ClientError(Error):
    """The request from the client is **invalid**.

    This type of errors is considered as **non-retriable** and so clients
    should **not** retry the query before investigating the issue first.
    """


class ServiceError(Error):
    """The targeted service reported an error.

    This type of errors is considered as **non-retriable** and so clients
    should **not** retry the query before investigating the issue first.
    """


class NotFound(Error):
    """The requested resources are **not available**.

    This can be for a variety of reasons such as:

    - There is a typo in the parameters passed to the function
    - The resources exist but in another service than the targeted one

    This type of errors is considered as **non-retriable** and so clients
    should **not** retry the query before investigating the issue first.
    """

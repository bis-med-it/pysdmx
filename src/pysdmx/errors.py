"""Types of errors that can be returned by pysdmx."""

from typing import Any, Dict, Optional


class PysdmxError(Exception):
    """Base ``pysdmx`` error class.

    This class is inherited by more specific error classes and so, ideally,
    you should not encounter it directly when calling library functions.

    Attributes:
        title: A short description of the problem.
        description: A longer, human-friendly description of the problem,
            ideally with tips on how the issue can be resolved.
        csi: A dictionary containing additional details about the issue,
            that can contribute to its understanding or resolution.
    """

    def __init__(
        self,
        title: str,
        description: Optional[str] = None,
        csi: Optional[Dict[str, Any]] = None,
    ):
        """Instantiates a new error, with the supplied paramaters."""
        self.title = title
        self.description = description
        self.csi = csi
        super().__init__(self.description)


class RetriableError(PysdmxError):
    """A type of errors that may be resolved after retrying.

    This class is inherited by more specific error classes and so, ideally,
    you should not encounter it directly when calling library functions.
    """


class Unavailable(RetriableError):
    """The targeted service or resource is not available.

    This can be for a variety of reasons such as:

    - A network issue between the client making the call and the targeted
      service
    - The targeted service is temporarily unavailable
    - The targeted service is overloaded and therefore unable to process
      the request

    This type of errors is considered as **retriable** and so clients can
    retry executing the query at a later stage.
    """


class Invalid(PysdmxError):
    """The request is invalid.

    This type of errors is considered as **non-retriable** and so clients
    should **not** retry the query before investigating why the request
    is invalid.
    """


class InternalError(PysdmxError):
    """The request is valid but could not be fulfilled.

    This type of errors is considered as **non-retriable** and so clients
    should **not** retry the query before investigating (and possibly
    reporting) the issue first.
    """


class NotFound(PysdmxError):
    """The requested resource is **not available**.

    This type of errors is considered as **non-retriable** and so clients
    should **not** retry the query before investigating the issue first.
    """


class NotImplemented(PysdmxError):
    """The requested operation is not supported.

    This type of errors is considered as **non-retriable** and so clients
    should **not** retry the query before investigating the issue first.
    """


class Unauthorized(PysdmxError):
    """The request was **not authorized**.

    This can be for a variety of reasons such as:

    - Authentication is required by no credentials were supplied.
    - Credentials were supplied but were invalid.
    - Credentials were supplied and valid but access is denied.


    This type of errors is considered as **non-retriable** and so clients
    should **not** retry the query before investigating the issue first.
    """

"""Possible exceptions thrown by this library"""


class NotConnectedException(Exception):
    """This exception indicates an operation that failed due to an incorrect state.
    The operation requires that there is an active connection to the API.
    Use the connected() and connect() functions on YtLoungeApi."""


class NotPairedException(Exception):
    """This exception indicates an operation that failed due to an incorrect state.
    The operation requires that the API has been paired with a screen.
    Use the paired() and pair() functions on YtLoungeApi."""


class NotLinkedException(Exception):
    """This exception indicates an operation that failed due to an incorrect state.
    The operation requires that the API has been linked with a screen.
    Use the linked(), pair() and refresh_auth() functions on YtLoungeApi."""


class NotSupportedException(Exception):
    """This exception indicates an operation that failed due to connecting to an
    unsupported client. Some YouTube clients (currently YouTube TV for Kids) are
    not supported by this library and will raise this exception when attempting
    to connect to them."""

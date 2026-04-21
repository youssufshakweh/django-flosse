class SSEClientDisconnected(Exception):
    """Raised internally when the client closes the connection."""


class SSEYieldError(ValueError):
    """Raised when a view yields a value that cannot be converted to an SSE event."""

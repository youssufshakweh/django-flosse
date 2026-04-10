class SSEClientDisconnected(Exception):
    """Raised internally when the client closes the connection."""


class SSEPermissionDenied(Exception):
    """Raised when a permission check fails."""


class SSEYieldError(ValueError):
    """Raised when a view yields a value that cannot be converted to an SSE event."""

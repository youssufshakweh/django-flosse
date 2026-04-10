from __future__ import annotations

from django.http import HttpRequest


class BaseSSEPermission:
    """
    Minimal permission interface for ``@sse_stream``.

    Subclass this and override ``has_permission`` to add your own auth logic.
    Returning ``False`` causes the decorator to respond with HTTP 403.

    Example::

        class LoginRequired(BaseSSEPermission):
            def has_permission(self, request: HttpRequest) -> bool:
                return request.user.is_authenticated
    """

    def has_permission(self, request: HttpRequest) -> bool:  # noqa: ARG002
        return True


class IsAuthenticated(BaseSSEPermission):
    """Allow access only to authenticated users (session / token auth)."""

    def has_permission(self, request: HttpRequest) -> bool:
        return bool(getattr(request, "user", None) and request.user.is_authenticated)


class IsAdminUser(BaseSSEPermission):
    """Allow access only to staff / superusers."""

    def has_permission(self, request: HttpRequest) -> bool:
        return bool(
            getattr(request, "user", None)
            and request.user.is_authenticated
            and request.user.is_staff
        )


class AllowAny(BaseSSEPermission):
    """Allow unrestricted access (default behaviour)."""

    def has_permission(self, request: HttpRequest) -> bool:
        return True

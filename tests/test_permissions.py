from unittest.mock import MagicMock

from django_flosse.permissions import (
    AllowAny,
    BaseSSEPermission,
    IsAdminUser,
    IsAuthenticated,
)


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #


def _request(is_authenticated=True, is_staff=False, has_user=True):
    request = MagicMock()
    if has_user:
        request.user = MagicMock(
            is_authenticated=is_authenticated,
            is_staff=is_staff,
        )
    else:
        del request.user  # simulate request without .user attribute
    return request


# --------------------------------------------------------------------------- #
# BaseSSEPermission                                                            #
# --------------------------------------------------------------------------- #


class TestBaseSSEPermission:
    def test_default_allows_everything(self):
        assert BaseSSEPermission().has_permission(_request()) is True

    def test_subclass_can_deny(self):
        class DenyAll(BaseSSEPermission):
            def has_permission(self, request):
                return False

        assert DenyAll().has_permission(_request()) is False

    def test_subclass_can_inspect_request(self):
        class HeaderCheck(BaseSSEPermission):
            def has_permission(self, request):
                return request.headers.get("X-Token") == "secret"

        req = MagicMock()
        req.headers = {"X-Token": "secret"}
        assert HeaderCheck().has_permission(req) is True

        req.headers = {"X-Token": "wrong"}
        assert HeaderCheck().has_permission(req) is False


# --------------------------------------------------------------------------- #
# AllowAny                                                                     #
# --------------------------------------------------------------------------- #


class TestAllowAny:
    def test_allows_authenticated_user(self):
        assert AllowAny().has_permission(_request(is_authenticated=True)) is True

    def test_allows_anonymous_user(self):
        assert AllowAny().has_permission(_request(is_authenticated=False)) is True

    def test_allows_request_without_user(self):
        assert AllowAny().has_permission(_request(has_user=False)) is True


# --------------------------------------------------------------------------- #
# IsAuthenticated                                                              #
# --------------------------------------------------------------------------- #


class TestIsAuthenticated:
    def test_grants_authenticated_user(self):
        assert IsAuthenticated().has_permission(_request(is_authenticated=True)) is True

    def test_denies_anonymous_user(self):
        assert (
            IsAuthenticated().has_permission(_request(is_authenticated=False)) is False
        )

    def test_denies_request_without_user_attribute(self):
        assert IsAuthenticated().has_permission(_request(has_user=False)) is False

    def test_denies_when_user_is_none(self):
        request = MagicMock()
        request.user = None
        assert IsAuthenticated().has_permission(request) is False


# --------------------------------------------------------------------------- #
# IsAdminUser                                                                  #
# --------------------------------------------------------------------------- #


class TestIsAdminUser:
    def test_grants_staff_user(self):
        assert (
            IsAdminUser().has_permission(_request(is_authenticated=True, is_staff=True))
            is True
        )

    def test_denies_non_staff_authenticated_user(self):
        assert (
            IsAdminUser().has_permission(
                _request(is_authenticated=True, is_staff=False)
            )
            is False
        )

    def test_denies_anonymous_user(self):
        assert (
            IsAdminUser().has_permission(
                _request(is_authenticated=False, is_staff=False)
            )
            is False
        )

    def test_denies_request_without_user_attribute(self):
        assert IsAdminUser().has_permission(_request(has_user=False)) is False

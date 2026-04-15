from unittest.mock import MagicMock

from django.http import HttpResponse, StreamingHttpResponse

from django_flosse import SSEEvent, sse_stream
from django_flosse.permissions import BaseSSEPermission, IsAuthenticated, IsAdminUser
from tests.conftest import async_consume, consume


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #


def make_request(is_authenticated=True, is_staff=False):
    request = MagicMock()
    request.path = "/sse/test/"
    request.user = MagicMock(is_authenticated=is_authenticated, is_staff=is_staff)
    return request


# --------------------------------------------------------------------------- #
# Response type & headers                                                      #
# --------------------------------------------------------------------------- #


class TestResponseType:
    def test_returns_streaming_http_response(self):
        @sse_stream
        def view(request):
            yield "hello"

        assert isinstance(view(make_request()), StreamingHttpResponse)

    def test_content_type_is_text_event_stream(self):
        @sse_stream
        def view(request):
            yield "x"

        assert "text/event-stream" in view(make_request())["Content-Type"]

    def test_cache_control_no_cache(self):
        @sse_stream
        def view(request):
            yield "x"

        assert "no-cache" in view(make_request())["Cache-Control"]

    def test_x_accel_buffering_disabled(self):
        @sse_stream
        def view(request):
            yield "x"

        assert view(make_request())["X-Accel-Buffering"] == "no"


# --------------------------------------------------------------------------- #
# Yield styles                                                                 #
# --------------------------------------------------------------------------- #


class TestYieldStyles:
    def test_plain_string(self):
        @sse_stream
        def view(request):
            yield "hello"

        assert "data: hello" in consume(view(make_request()))

    def test_tuple_event_and_data(self):
        @sse_stream
        def view(request):
            yield ("update", {"n": 1})

        body = consume(view(make_request()))
        assert "event: update\n" in body
        assert '"n": 1' in body

    def test_tuple_with_id(self):
        @sse_stream
        def view(request):
            yield ("update", "payload", "evt-1")

        body = consume(view(make_request()))
        assert "event: update\n" in body
        assert "id: evt-1\n" in body

    def test_dict_with_data_key(self):
        @sse_stream
        def view(request):
            yield {"data": "msg", "event": "greet"}

        body = consume(view(make_request()))
        assert "event: greet\n" in body
        assert "data: msg\n" in body

    def test_dict_without_data_key(self):
        @sse_stream
        def view(request):
            yield {"foo": "bar"}

        assert '"foo": "bar"' in consume(view(make_request()))

    def test_sse_event_object(self):
        @sse_stream
        def view(request):
            yield SSEEvent(data="bye", event="close", id="99")

        body = consume(view(make_request()))
        assert "event: close\n" in body
        assert "id: 99\n" in body
        assert "data: bye\n" in body

    def test_multiple_events_all_present(self):
        @sse_stream
        def view(request):
            yield "first"
            yield "second"
            yield "third"

        body = consume(view(make_request()))
        assert "data: first\n" in body
        assert "data: second\n" in body
        assert "data: third\n" in body

    def test_generator_with_no_yields(self):
        @sse_stream
        def view(request):
            return
            yield  # make it a generator

        body = consume(view(make_request()))
        assert body == ""


# --------------------------------------------------------------------------- #
# retry directive                                                              #
# --------------------------------------------------------------------------- #


class TestRetryDirective:
    def test_retry_sent_as_first_frame(self):
        @sse_stream(retry=5000)
        def view(request):
            yield "x"

        assert consume(view(make_request())).startswith("retry: 5000\n\n")

    def test_no_retry_when_not_configured(self):
        @sse_stream
        def view(request):
            yield "x"

        assert not consume(view(make_request())).startswith("retry:")


# --------------------------------------------------------------------------- #
# Permissions                                                                  #
# --------------------------------------------------------------------------- #


class TestPermissions:
    def test_no_permission_classes_allows_all(self):
        @sse_stream
        def view(request):
            yield "ok"

        assert view(make_request()).status_code == 200

    def test_single_deny_class_returns_403(self):
        class DenyAll(BaseSSEPermission):
            def has_permission(self, request):
                return False

        @sse_stream(permission_classes=[DenyAll])
        def view(request):
            yield "never"

        response = view(make_request())
        assert isinstance(response, HttpResponse)
        assert response.status_code == 403

    def test_single_allow_class_returns_200(self):
        class AllowAll(BaseSSEPermission):
            def has_permission(self, request):
                return True

        @sse_stream(permission_classes=[AllowAll])
        def view(request):
            yield "yes"

        assert view(make_request()).status_code == 200

    def test_all_must_pass_first_denies(self):
        class Allow(BaseSSEPermission):
            def has_permission(self, request):
                return True

        class Deny(BaseSSEPermission):
            def has_permission(self, request):
                return False

        @sse_stream(permission_classes=[Deny, Allow])
        def view(request):
            yield "never"

        assert view(make_request()).status_code == 403

    def test_all_must_pass_second_denies(self):
        class Allow(BaseSSEPermission):
            def has_permission(self, request):
                return True

        class Deny(BaseSSEPermission):
            def has_permission(self, request):
                return False

        @sse_stream(permission_classes=[Allow, Deny])
        def view(request):
            yield "never"

        assert view(make_request()).status_code == 403

    def test_is_authenticated_grants_authed_user(self):
        @sse_stream(permission_classes=[IsAuthenticated])
        def view(request):
            yield "ok"

        assert view(make_request(is_authenticated=True)).status_code == 200

    def test_is_authenticated_denies_anon_user(self):
        @sse_stream(permission_classes=[IsAuthenticated])
        def view(request):
            yield "never"

        assert view(make_request(is_authenticated=False)).status_code == 403

    def test_is_admin_grants_staff_user(self):
        @sse_stream(permission_classes=[IsAdminUser])
        def view(request):
            yield "ok"

        assert (
            view(make_request(is_authenticated=True, is_staff=True)).status_code == 200
        )

    def test_is_admin_denies_non_staff(self):
        @sse_stream(permission_classes=[IsAdminUser])
        def view(request):
            yield "never"

        assert (
            view(make_request(is_authenticated=True, is_staff=False)).status_code == 403
        )


# --------------------------------------------------------------------------- #
# Error handling                                                               #
# --------------------------------------------------------------------------- #


class TestErrorHandling:
    def test_producer_exception_emits_error_event(self):
        @sse_stream
        def view(request):
            yield "before"
            raise RuntimeError("boom")

        body = consume(view(make_request()))
        assert "event: error\n" in body
        assert "boom" in body

    def test_invalid_yield_emits_error_event(self):
        @sse_stream
        def view(request):
            yield ("a", "b", "c", "d")  # 4-tuple → ValueError

        body = consume(view(make_request()))
        assert "event: error\n" in body

    def test_view_still_streams_events_before_exception(self):
        @sse_stream
        def view(request):
            yield "before error"
            raise RuntimeError("oops")

        body = consume(view(make_request()))
        assert "data: before error\n" in body


# --------------------------------------------------------------------------- #
# @wraps preservation                                                          #
# --------------------------------------------------------------------------- #


class TestDecorationMeta:
    def test_original_function_name_preserved(self):
        @sse_stream
        def my_special_view(request):
            yield "x"

        assert my_special_view.__name__ == "my_special_view"

    def test_original_docstring_preserved(self):
        @sse_stream
        def my_view(request):
            """My docstring."""
            yield "x"

        assert my_view.__doc__ == "My docstring."

    def test_accepts_url_kwargs(self):
        @sse_stream
        def view(request, pk):
            yield f"pk={pk}"

        body = consume(view(make_request(), pk=42))
        assert "data: pk=42\n" in body


# --------------------------------------------------------------------------- #
# Async Tests                                                                 #
# --------------------------------------------------------------------------- #


class TestAsyncDecoratedView:
    async def test_returns_streaming_response(self, plain_request):
        @sse_stream
        async def view(request):
            yield "hello"

        resp = await view(plain_request)
        assert isinstance(resp, StreamingHttpResponse)

    async def test_headers_set_correctly(self, plain_request):
        @sse_stream(retry=3000)
        async def view(request):
            yield "x"

        resp = await view(plain_request)
        assert "text/event-stream" in resp["Content-Type"]
        assert "no-cache" in resp["Cache-Control"]
        assert resp["X-Accel-Buffering"] == "no"

    async def test_plain_string_yields_correct_sse(self, plain_request):
        @sse_stream
        async def view(request):
            yield "hello"

        resp = await view(plain_request)
        body = await async_consume(resp)
        assert "data: hello\n" in body

    async def test_tuple_event_data(self, plain_request):
        @sse_stream
        async def view(request):
            yield ("update", {"n": 1})

        resp = await view(plain_request)
        body = await async_consume(resp)
        assert "event: update\n" in body
        assert '"n": 1' in body

    async def test_retry_sent_first(self, plain_request):
        @sse_stream(retry=5000)
        async def view(request):
            yield "x"

        resp = await view(plain_request)
        body = await async_consume(resp)
        assert body.startswith("retry: 5000\n\n")

    async def test_permission_deny_returns_403(self, anon_request):
        @sse_stream(permission_classes=[IsAuthenticated])
        async def view(request):
            yield "never"

        resp = await view(anon_request)
        assert isinstance(resp, HttpResponse)
        assert resp.status_code == 403

    async def test_permission_allow_streams_200(self, authed_request):
        @sse_stream(permission_classes=[IsAuthenticated])
        async def view(request):
            yield "ok"

        resp = await view(authed_request)
        assert resp.status_code == 200

    async def test_async_producer_exception_emits_error(self, plain_request):
        @sse_stream
        async def view(request):
            yield "before"
            raise RuntimeError("boom")

        resp = await view(plain_request)
        body = await async_consume(resp)
        assert "event: error\n" in body
        assert "boom" in body
        assert "data: before\n" in body

    async def test_invalid_yield_format_emits_error(self, plain_request):
        @sse_stream
        async def view(request):
            yield ("a", "b", "c", "d")

        resp = await view(plain_request)
        body = await async_consume(resp)
        assert "event: error\n" in body

    async def test_wraps_preserves_metadata(self):
        @sse_stream
        async def my_async_view(request):
            """Async SSE view."""
            yield "x"

        assert my_async_view.__name__ == "my_async_view"
        assert my_async_view.__doc__ == "Async SSE view."

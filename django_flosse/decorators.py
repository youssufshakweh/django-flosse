from __future__ import annotations

import logging
from functools import wraps
from typing import Any, Callable, Optional, Sequence, Type

from django.http import HttpRequest, HttpResponse, StreamingHttpResponse

from .events import SSEEvent
from .formatters import to_sse
from .permissions import BaseSSEPermission

logger = logging.getLogger("django_flosse")


def sse_stream(
    _view_func: Optional[Callable] = None,
    *,
    retry: Optional[int] = None,
    permission_classes: Sequence[Type[BaseSSEPermission]] = (),
) -> Callable:
    """
    Decorator that turns a **generator view** into an SSE endpoint.

    Can be used with or without parentheses::

        @sse_stream
        def view(request): ...

        @sse_stream()
        def view(request): ...

        @sse_stream(retry=3000, permission_classes=[IsAuthenticated])
        def view(request): ...

    Parameters
    ----------
    retry:
        If given, sends a ``retry:`` directive (in ms) as the first frame,
        telling the browser how long to wait before reconnecting.
    permission_classes:
        Iterable of :class:`~django_flosse.permissions.BaseSSEPermission` **classes**
        (not instances). All must pass or the response is HTTP 403.

    Yield styles
    ------------
    Inside the decorated generator you may yield:

    * ``str``                           → plain data event
    * ``(event_name, data)``            → named event
    * ``(event_name, data, id)``        → named event with ID
    * ``dict`` with a ``"data"`` key    → keyword-mapped to :class:`~django_flosse.events.SSEEvent`
    * ``dict`` without ``"data"``       → whole dict serialised as JSON data
    * :class:`~django_flosse.events.SSEEvent` → used directly

    Heartbeats
    ----------
    django-flosse does **not** manage heartbeats automatically.
    If you are behind a proxy (Nginx, AWS ELB, Cloudflare) that closes idle
    connections, emit a keep-alive ping yourself inside the generator::

        @sse_stream
        def live_feed(request):
            while True:
                data = get_new_data()
                if data:
                    yield ("update", data)
                else:
                    yield SSEEvent(data="", event="ping")   # keep-alive
                time.sleep(5)
    """

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:

            # ---------------------------------------------------------------- #
            # 1. Permission checks                                             #
            # ---------------------------------------------------------------- #
            for perm_cls in permission_classes:
                if not perm_cls().has_permission(request):
                    logger.debug(
                        "SSE permission denied by %s for %s",
                        perm_cls.__name__,
                        request.path,
                    )
                    return HttpResponse(status=403)

            # ---------------------------------------------------------------- #
            # 2. Streaming generator                                           #
            # ---------------------------------------------------------------- #
            def _stream():
                if retry is not None:
                    yield f"retry: {retry}\n\n"

                try:
                    gen = view_func(request, *args, **kwargs)
                    for item in gen:
                        try:
                            yield to_sse(item)
                        except Exception as fmt_err:  # noqa: BLE001
                            logger.warning("SSE format error: %s", fmt_err)
                            yield SSEEvent(data=str(fmt_err), event="error").encode()

                except GeneratorExit:  # pragma: no cover
                    logger.debug("SSE client disconnected from %s.", request.path)

                except Exception as exc:  # noqa: BLE001
                    logger.exception("SSE producer raised an exception: %s", exc)
                    yield SSEEvent(data=str(exc), event="error").encode()

            # ---------------------------------------------------------------- #
            # 3. Build and return the streaming response                       #
            # ---------------------------------------------------------------- #
            response = StreamingHttpResponse(
                _stream(), content_type="text/event-stream; charset=utf-8"
            )
            response["Cache-Control"] = "no-cache, no-transform"
            response["X-Accel-Buffering"] = "no"
            return response

        return wrapper

    # Support both @sse_stream and @sse_stream()
    if _view_func is not None:
        return decorator(_view_func)

    return decorator

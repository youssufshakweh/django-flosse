from __future__ import annotations

import inspect
import logging
from functools import wraps
from typing import Any, Callable, Optional

from django.http import HttpRequest, HttpResponse, StreamingHttpResponse

from .events import SSEEvent
from .formatters import to_sse

logger = logging.getLogger("django_flosse")


def _build_response(streaming_content: Any) -> StreamingHttpResponse:
    """
    Build a StreamingHttpResponse with the correct SSE headers.

    Works with both sync and async generators — Django detects
    the iterator type automatically via StreamingHttpResponse.
    """
    response = StreamingHttpResponse(
        streaming_content,
        content_type="text/event-stream; charset=utf-8",
    )
    response["Cache-Control"] = "no-cache, no-transform"
    response["X-Accel-Buffering"] = "no"
    return response


# -------------------------------------------------- #
# Decorator                                          #
# -------------------------------------------------- #


def sse_stream(
    _view_func: Optional[Callable] = None,
    *,
    retry: Optional[int] = None,
) -> Callable:
    """
    Decorator that turns a **generator view** into an SSE endpoint.

    Supports both sync and async generator views — detected automatically::

        # sync
        @sse_stream
        def feed(request):
            yield ("update", {"value": 1})

        # async — requires ASGI server (Uvicorn, Daphne)
        @sse_stream
        async def feed(request):
            async for item in my_async_source():
                yield ("update", {"value": item})

    Can be used with or without parentheses::

        @sse_stream
        @sse_stream()
        @sse_stream(retry=3000)

    Parameters
    ----------
    retry:
        If given, sends a ``retry:`` directive (in ms) as the first frame,
        telling the browser how long to wait before reconnecting.

    Yield styles
    ------------
    * ``str``                        → plain data event
    * ``(event_name, data)``         → named event
    * ``(event_name, data, id)``     → named event with ID
    * ``dict`` with ``"data"`` key   → mapped to SSEEvent fields
    * ``dict`` without ``"data"``    → whole dict serialised as JSON
    * :class:`~django_flosse.events.SSEEvent` → used directly

    Heartbeats
    ----------
    django-flosse does **not** manage heartbeats automatically.
    Emit a keep-alive ping yourself if behind a proxy::

        @sse_stream
        async def live_feed(request):
            while True:
                data = await get_new_data()
                if data:
                    yield ("update", data)
                else:
                    yield SSEEvent(data="", event="ping")
                await asyncio.sleep(5)
    """

    def decorator(view_func: Callable) -> Callable:
        # -------------------------------------------------------------------- #
        # Async path                                                           #
        # -------------------------------------------------------------------- #
        if inspect.isasyncgenfunction(view_func):

            @wraps(view_func)
            async def awrapper(
                request: HttpRequest, *args: Any, **kwargs: Any
            ) -> HttpResponse:
                # ---------------------------------------------------------------- #
                # 1. Async streaming generator                                     #
                # ---------------------------------------------------------------- #
                async def astream():
                    if retry is not None:
                        yield f"retry: {retry}\n\n"

                    try:
                        async for item in view_func(request, *args, **kwargs):
                            try:
                                yield to_sse(item)
                            except Exception as fmt_err:  # noqa: BLE001
                                logger.warning("SSE format error: %s", fmt_err)
                                yield SSEEvent(
                                    data=str(fmt_err), event="error"
                                ).encode()

                    except Exception as exc:  # noqa: BLE001
                        logger.exception(
                            "SSE async producer raised an exception: %s", exc
                        )
                        yield SSEEvent(data=str(exc), event="error").encode()

                # ---------------------------------------------------------------- #
                # 2. Build response                                                #
                # ---------------------------------------------------------------- #
                return _build_response(astream())

            return awrapper

        # -------------------------------------------------------------------- #
        # Sync path                                                            #
        # -------------------------------------------------------------------- #
        @wraps(view_func)
        def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
            # ---------------------------------------------------------------- #
            # 1. Streaming generator                                           #
            # ---------------------------------------------------------------- #
            def _stream():
                if retry is not None:
                    yield f"retry: {retry}\n\n"

                try:
                    for item in view_func(request, *args, **kwargs):
                        try:
                            yield to_sse(item)
                        except Exception as fmt_err:  # noqa: BLE001
                            logger.warning("SSE format error: %s", fmt_err)
                            yield SSEEvent(data=str(fmt_err), event="error").encode()

                except GeneratorExit:
                    logger.debug("SSE client disconnected from %s.", request.path)

                except Exception as exc:  # noqa: BLE001
                    logger.exception("SSE producer raised an exception: %s", exc)
                    yield SSEEvent(data=str(exc), event="error").encode()

            # ---------------------------------------------------------------- #
            # 2. Build response                                                #
            # ---------------------------------------------------------------- #
            return _build_response(_stream())

        return wrapper

    # Support both @sse_stream and @sse_stream()
    if _view_func is not None:
        return decorator(_view_func)

    return decorator

from __future__ import annotations

from typing import Any

from .events import SSEEvent


def to_sse(raw: Any) -> str:
    """
    Convert any value yielded by a view into an SSE-formatted string.

    Supported yield styles
    ----------------------
    - ``str``              → treated as plain data
    - ``(event, data)``   → named event with data
    - ``dict``            → passed as keyword args to SSEEvent;
                            if no ``"data"`` key, the whole dict is the data
    - ``SSEEvent``        → encoded as-is

    Anything else is coerced to ``str`` and used as data.
    """

    if isinstance(raw, SSEEvent):
        return raw.encode()

    if isinstance(raw, str):
        return SSEEvent(data=raw).encode()

    if isinstance(raw, tuple):
        if len(raw) == 2:
            event_name, data = raw
            return SSEEvent(event=event_name, data=data).encode()

        if len(raw) == 3:
            event_name, data, id_ = raw
            return SSEEvent(event=event_name, data=data, id=str(id_)).encode()

        raise ValueError(
            f"Tuple yields must be (event, data) or (event, data, id), got {len(raw)}-tuple."
        )

    if isinstance(raw, dict):
        if "data" in raw:
            return SSEEvent(
                **{
                    k: v
                    for k, v in raw.items()
                    if k in ("data", "event", "id", "retry")
                }
            ).encode()

        return SSEEvent(data=raw).encode()

    # Fallback
    return SSEEvent(data=str(raw)).encode()

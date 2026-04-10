from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class SSEEvent:
    """
    Represents a single Server-Sent Event.

    Attributes:
        data:   The payload. Dicts/lists are serialised to JSON automatically.
        event:  Optional named event type (maps to the ``event:`` field).
        id:     Optional event ID for client reconnection (maps to ``id:``).
        retry:  Optional reconnection delay in milliseconds (maps to ``retry:``).

    Examples::

        SSEEvent(data="hello")
        SSEEvent(data={"count": 1}, event="update")
        SSEEvent(data="done", event="finish", id="42")
    """

    data: Any
    event: Optional[str] = None
    id: Optional[str] = None
    retry: Optional[int] = None

    def encode(self) -> str:
        """Serialise to the SSE wire format (ends with a blank line)."""
        lines: list[str] = []

        if self.retry is not None:
            lines.append(f"retry: {self.retry}")

        if self.id is not None:
            lines.append(f"id: {self.id}")

        if self.event is not None:
            lines.append(f"event: {self.event}")

        payload = self.data
        if not isinstance(payload, str):
            payload = json.dumps(payload, ensure_ascii=False)

        # Multi-line data: each line must have its own "data:" prefix.
        for line in payload.splitlines():
            lines.append(f"data: {line}")

        lines.append("")  # Blank line to terminate the event
        return "\n".join(lines) + "\n"

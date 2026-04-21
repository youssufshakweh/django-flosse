r"""
      _ _                                __ _                    
     | (_)                              / _| |                   
   __| |_  __ _ _ __   __ _  ___ ______| |_| | ___  ___ ___  ___ 
  / _` | |/ _` | '_ \ / _` |/ _ \______|  _| |/ _ \/ __/ __|/ _ \
 | (_| | | (_| | | | | (_| | (_) |     | | | | (_) \__ \__ \  __/
  \__,_| |\__,_|_| |_|\__, |\___/      |_| |_|\___/|___/___/\___|
      _/ |             __/ |                                     
     |__/             |___/                                      

Dead-simple Server-Sent Events for Django via a single decorator.

Quick start::

    from django_flosse import sse_stream, SSEEvent

    @sse_stream
    def live_updates(request):
        yield "connected"                             # plain string
        yield ("update", {"count": 1})                # (event, data) tuple
        yield {"data": "done", "event": "finish"}     # dict
        yield SSEEvent(data="bye", event="close")     # SSEEvent object
"""

from .decorators import sse_stream
from .events import SSEEvent
from .exceptions import SSEClientDisconnected, SSEYieldError
from .formatters import to_sse

__all__ = [
    "sse_stream",
    "SSEEvent",
    "to_sse",
    "SSEClientDisconnected",
    "SSEYieldError",
]

__version__ = "0.2.0"

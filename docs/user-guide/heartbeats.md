# Heartbeats

django-flosse does **not** manage heartbeats automatically — and that is intentional.

---

## Why not automatic?

The decorator iterates your generator directly in the WSGI worker with
**zero extra threads**. A background heartbeat thread would undo this simplicity.

Two reasons heartbeats are often unnecessary:

1. **Frequent streams** — if your view yields events every second, the connection
   is never idle and no proxy will close it.
2. **Slow streams** — if your generator blocks for a long time between events,
   the right solution is an **async ASGI** setup, not a background thread
   patching over the problem.

---

## When do you need one?

Only when you are behind a proxy that closes idle connections:

| Proxy / Platform | Default idle timeout |
|------------------|----------------------|
| Nginx            | 60 s (configurable)  |
| AWS ELB          | 60 s                 |
| Cloudflare       | 100 s                |
| Heroku           | 30 s                 |

If your stream can be idle longer than the proxy's timeout, send a keep-alive ping.

---

## How to add one

Yield an `SSEEvent` with an empty `data` field at regular intervals:

```python
import time
from django_flosse import sse_stream, SSEEvent

@sse_stream
def live_feed(request):
    while True:
        data = get_new_data()

        if data:
            yield ("update", data)
        else:
            yield SSEEvent(data="", event="ping")   # (1)

        time.sleep(5)
```

1. Browsers ignore events with empty `data` — this is purely a keep-alive signal
   for the proxy.

---

## Nginx configuration

If increasing the timeout is an option, you can skip the in-code heartbeat entirely:

```nginx
location /sse/ {
    proxy_pass         http://django;
    proxy_read_timeout 3600;   # 1 hour
    proxy_buffering    off;
}
```

!!! tip
    `X-Accel-Buffering: no` is already set by `@sse_stream` — you do not need
    to add it to your Nginx config.
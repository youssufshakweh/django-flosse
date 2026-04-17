# Async Generator Support

`django-flosse` natively supports asynchronous generators out of the box. Starting from version `0.2.0`, you can write SSE streams using `async def` and `async for` without any additional configuration or dependencies.

!!! tip "Why go async?"
    Async generators shine when your data source is I/O bound (DB queries, external APIs, message brokers) or event-driven (Redis pub/sub, Django signals). They keep the event loop unblocked and scale efficiently under high concurrency.

---

## Quick Start

Simply decorate an async generator with `@sse_stream`. The decorator automatically detects async generators and routes them through Django's async response pipeline.

```python
from django_flosse import sse_stream
from django_flosse.events import SSEEvent

@sse_stream
async def live_metrics(request):
    async for metric in fetch_async_metrics():
        yield SSEEvent(event="metric", data=metric)
```

!!! note "No config required"
    The same decorator works for both `def` and `async def`. All yield formats (`str`, `tuple`, `dict`, `SSEEvent`) behave identically.

---

## Common Patterns

### 1. Non-Blocking Polling
```python
import asyncio
from django_flosse import sse_stream

@sse_stream
async def dashboard_feed(request):
    while True:
        data = await fetch_latest_stats()
        yield ("update", data)
        await asyncio.sleep(2)  # ✅ Non-blocking wait
```

!!! warning "Avoid `time.sleep()`"
    Using synchronous `time.sleep()` inside an async generator will block the entire event loop. Always use `asyncio.sleep()`.

### 2. Redis Pub/Sub Streaming
```python
import redis.asyncio as redis
from django_flosse import sse_stream
from django_flosse.events import SSEEvent

r = redis.Redis.from_url("redis://localhost:6379/0")

@sse_stream
async def redis_channel(request):
    async with r.pubsub() as pubsub:
        await pubsub.subscribe("live-feed")
        async for message in pubsub.listen():
            if message["type"] == "message":
                yield SSEEvent(event="update", data=message["data"])
```

### 3. Graceful Cancellation & Cleanup
When a client disconnects, Django cancels the async generator. Use `try/except asyncio.CancelledError` to release resources cleanly.

```python
@sse_stream
async def managed_stream(request):
    resource = await acquire_async_resource()
    try:
        async for data in resource.stream():
            yield ("data", data)
    except asyncio.CancelledError:
        await resource.release()
        # ✅ No need to re-raise. Django handles cancellation silently.
```

---

## Deployment Requirements

### ✅ Use an ASGI Server
Async generators require an ASGI-compatible server to run efficiently:
- **Recommended**: `uvicorn`, `daphne`, `hypercorn`
- ⚠️ **Fallback**: WSGI servers (Gunicorn, uWSGI) will run async code in a thread pool, negating most performance benefits.

Example `asgi.py`:
```python
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
application = get_asgi_application()
```

Run with Uvicorn:
```bash
uvicorn myproject.asgi:application --workers 4 --loop uvloop
```

### 🔧 Reverse Proxy Configuration
Disable buffering to prevent connection timeouts:

```nginx
location /stream/ {
    proxy_pass http://backend;
    proxy_buffering off;
    proxy_cache off;
    proxy_read_timeout 24h;
}
```

!!! tip "Cloudflare / CDN users"
    SSE connections may be terminated by caching proxies. Add a `Cache-Control: no-cache` header (handled by `django-flosse` automatically) and ensure your CDN respects streaming responses.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `RuntimeError: Event loop is closed` | Ensure you're running on an ASGI server, not WSGI |
| Stream stops unexpectedly | Check for unhandled exceptions; wrap yields in `try/except` |
| High memory usage | Avoid accumulating payloads in memory; yield incrementally |
| `CancelledError` spam in logs | Normal on disconnect. Handle gracefully or let Django suppress it |
| Async view runs slowly | Verify you're not using synchronous blocking calls (`requests`, `time.sleep`, etc.) |

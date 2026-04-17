# Deployment

---

## Choosing Your Server

| Use Case | Recommended Server | Why |
|----------|-------------------|-----|
| **Sync views only** (`def`) | Gunicorn (WSGI) | Mature, stable, simple |
| **Async views** (`async def`) | Uvicorn, Daphne (ASGI) | Native async support, better concurrency |
| **Mixed sync/async** | Uvicorn (ASGI) | Handles both seamlessly |

!!! tip "Not sure?"
    Start with **Uvicorn** — it supports both sync and async views, and is the recommended default for `django-flosse v0.2.0+`.

---

## ASGI — Uvicorn (Recommended for Async)

For best performance with `async def` SSE views, run your project with an ASGI server:

```bash
uvicorn myproject.asgi:application \
    --workers 4 \
    --loop uvloop \
    --http h11
```

!!! note "Why these flags?"
    - `--workers`: Scale horizontally (one per CPU core)
    - `--loop uvloop`: Faster event loop (optional but recommended)
    - `--http h11`: Better SSE compatibility with some proxies

### Production Example (with Gunicorn + Uvicorn workers)
```bash
gunicorn myproject.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --workers 4 \
    --worker-connections 1000 \
    --timeout 120
```
This combines Gunicorn's process management with Uvicorn's async performance.

---

## WSGI — Gunicorn (Sync Only)

Each SSE connection holds one WSGI worker for its entire duration.
Use `gthread` workers so each worker can serve multiple streams concurrently:

```bash
gunicorn myproject.wsgi:application \
    --worker-class gthread \
    --workers 2 \
    --threads 4
```

This allows up to `workers × threads = 8` concurrent SSE streams per server.

!!! tip "Tuning"
    Start with `--workers $(nproc)` and `--threads 4`.
    Increase `--threads` if most connections are idle (SSE is I/O-bound).

!!! warning "Async views on WSGI"
    Async generators will run in a thread pool on WSGI servers, negating most performance benefits. Use ASGI for `async def` views.

---

## WSGI — uWSGI

```ini
[uwsgi]
module        = myproject.wsgi:application
workers       = 2
threads       = 4
enable-threads = true
```

---

## Nginx

`X-Accel-Buffering: no` is set automatically by `@sse_stream` — no extra
Nginx config is required for buffering.

For long-lived connections, increase the read timeout:

```nginx
location /sse/ {
    proxy_pass             http://django;
    proxy_read_timeout     3600;
    proxy_buffering        off;
    proxy_cache            off;
}
```

!!! tip "Cloudflare / CDN users"
    Add these headers to prevent proxy buffering:
    ```nginx
    proxy_set_header Connection '';
    proxy_http_version 1.1;
    chunked_transfer_encoding off;
    ```

---

## Compatibility

| django-flosse | Django    | Python     | Server Support |
|---------------|-----------|------------|---------------|
| 0.1.x         | 3.2 – 6.0 | 3.9 – 3.14 | WSGI only |
| **0.2.0+**    | **4.2 – 6.0** | **3.9 – 3.14** | **WSGI + ASGI** |

!!! success "Async support is here!"
    Native `async def` generator views are available in **v0.2.0+**.
    Use an ASGI server (Uvicorn, Daphne) for best performance.
    See [Async Support Guide](../user-guide/async-support.md) for details.

---

## Monitoring & Health Checks

### Log Stream Lifecycle
```python
# settings.py
LOGGING = {
    "version": 1,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "django_flosse": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}
```

### Simple Health Endpoint
```python
# views.py
from django.http import JsonResponse

def sse_health(request):
    return JsonResponse({
        "status": "ok",
        "sse_support": True,
        "async_ready": True,  # v0.2.0+
    })
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connections drop after ~60s | Disable proxy buffering; increase `proxy_read_timeout` |
| Async views run slowly | Ensure you're using ASGI (Uvicorn), not WSGI |
| High memory usage per worker | Reduce `--threads` (WSGI) or `--workers` (ASGI); monitor with `psutil` |
| `CancelledError` in logs | Normal on disconnect; handle gracefully or suppress |
| SSE not working behind Cloudflare | Add `proxy_set_header Connection ''` + disable caching |
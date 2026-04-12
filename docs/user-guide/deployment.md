# Deployment

---

## WSGI — Gunicorn

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

---

## Compatibility

| django-flosse | Django    | Python     |
|---------------|-----------|------------|
| 0.1.x         | 3.2 – 6.0 | 3.9 – 3.14 |

!!! note "ASGI / async support"
    Native `async def` generator views and Uvicorn support are planned
    for a future release. See the [Roadmap](../roadmap.md).
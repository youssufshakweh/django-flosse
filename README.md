# django-flosse 🐟

<p align="center">
  <a href="https://pypi.org/project/django-flosse/">
    <img src="https://img.shields.io/pypi/v/django-flosse?color=blue&label=PyPI" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/django-flosse/">
    <img src="https://img.shields.io/pypi/pyversions/django-flosse" alt="Python versions">
  </a>
  <a href="https://pypi.org/project/django-flosse/">
    <img src="https://img.shields.io/pypi/djversions/django-flosse?label=Django" alt="Django versions">
  </a>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/tests-passing-brightgreen" alt="Tests">
  <img src="https://img.shields.io/badge/coverage-100%25-brightgreen" alt="Coverage">
</p>

Dead-simple **Server-Sent Events** for Django via a single decorator.

```python
from django_flosse import sse_stream

@sse_stream
def live_feed(request):
    for item in my_data_source():
        yield ("update", {"value": item})
```

---

## 📦 Installation

```bash
pip install django-flosse
```

No changes to `INSTALLED_APPS` are required.

---

## ⚡ Quick Start

### 1. Write a generator view

```python
# myapp/views.py
import time
from django_flosse import sse_stream, SSEEvent
from django_flosse.permissions import IsAuthenticated

@sse_stream(permission_classes=[IsAuthenticated])
def progress(request):
    for i in range(1, 11):
        yield ("progress", {"step": i, "total": 10, "pct": i * 10})
        time.sleep(1)

    yield SSEEvent(data="All done!", event="complete")
```

### 2. Wire up the URL

```python
# myapp/urls.py
from django.urls import path
from .views import progress

urlpatterns = [
    path("sse/progress/", progress),
]
```

### 3. Listen in the browser

```javascript
const source = new EventSource("/sse/progress/");

source.addEventListener("progress", (e) => {
    const { step, total, pct } = JSON.parse(e.data);
    console.log(`Step ${step}/${total} — ${pct}%`);
});

source.addEventListener("complete", (e) => {
    console.log(e.data);
    source.close();
});
```

---

## 🎨 Yield Styles

You can yield in whichever style feels most natural.

| What you `yield`                         | Result                              |
|------------------------------------------|-------------------------------------|
| `"hello"`                                | Unnamed data event                  |
| `("update", {"count": 1})`              | Named event `update` with JSON data |
| `("update", {"count": 1}, "evt-42")`    | Named event + ID                    |
| `{"data": "hi", "event": "greet"}`      | Dict mapped to SSEEvent fields      |
| `{"foo": "bar"}` *(no `"data"` key)*    | Whole dict serialised as JSON data  |
| `SSEEvent(data="x", event="y", id="1")` | Full control                        |

Dict data and non-string values are serialised to JSON automatically.

---

## ⚙️ `@sse_stream` Options

The decorator can be used with or without parentheses:

```python
@sse_stream                                    # no arguments
@sse_stream()                                  # explicit empty call
@sse_stream(retry=3000)                        # with options
@sse_stream(permission_classes=[IsAuthenticated], retry=3000)
```

| Parameter           | Default | Description                                      |
|---------------------|---------|--------------------------------------------------|
| `retry`             | `None`  | Browser reconnect delay in ms                    |
| `permission_classes`| `[]`    | Permission classes — all must pass or returns 403|

### Automatic HTTP headers

The decorator sets these on every response automatically:

| Header              | Value                              |
|---------------------|------------------------------------|
| `Content-Type`      | `text/event-stream; charset=utf-8` |
| `Cache-Control`     | `no-cache, no-transform`           |
| `X-Accel-Buffering` | `no` (disables Nginx buffering)    |

---

## 🔒 Permissions

```python
from django_flosse.permissions import BaseSSEPermission

class HasAPIKey(BaseSSEPermission):
    def has_permission(self, request) -> bool:
        return request.headers.get("X-API-Key") == "secret"

@sse_stream(permission_classes=[HasAPIKey])
def secure_stream(request):
    yield "top secret data"
```

### Built-in permissions

| Class             | Behaviour                                   |
|-------------------|---------------------------------------------|
| `AllowAny`        | Always permits (default when list is empty) |
| `IsAuthenticated` | Requires `request.user.is_authenticated`    |
| `IsAdminUser`     | Requires `request.user.is_staff`            |

Multiple classes are AND-ed together — every one must pass.

---

## 📖 `SSEEvent` Reference

```python
from django_flosse import SSEEvent

SSEEvent(
    data  = {"anything": "json-serialisable"},  # required
    event = "my-event",   # optional named event type
    id    = "evt-001",    # optional event ID
    retry = 5000,         # optional reconnect delay (ms)
)
```

---

## 💓 Heartbeats

django-flosse does **not** manage heartbeats automatically — and that is intentional.

The decorator iterates your generator directly in the WSGI worker with zero extra
threads. If you are behind a proxy (Nginx, AWS ELB, Cloudflare) that closes idle
connections, send a keep-alive ping yourself:

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
            yield SSEEvent(data="", event="ping")   # keeps the proxy alive
        time.sleep(5)
```

> **Why not automatic?**
> If your stream yields events frequently, a heartbeat is unnecessary noise.
> If your generator blocks for a long time between events, the right solution
> is an async setup — async support is on the roadmap.

---

## 🛠️ How It Works

```
HTTP request arrives
       │
  @sse_stream
       ├── Permission checks  (→ 403 if denied)
       └── StreamingHttpResponse
                │
         iterates your generator directly
                │
          for item in gen:
               ├── str        → data: <item>\n\n
               ├── tuple      → event: ...\ndata: ...\n\n
               ├── dict       → mapped to SSEEvent fields
               └── SSEEvent   → encoded as-is
```

No threads. No queues. No background processes.

---

## 🌐 Deployment

**WSGI (Gunicorn, uWSGI)**

Each SSE connection holds one worker for its duration. Use `--worker-class=gthread`
and tune `--threads` to serve multiple streams per worker:

```bash
gunicorn myproject.wsgi:application --worker-class=gthread --threads 4 --workers 2
```

> **Note:** ASGI / async support is planned for a future release.
> For high-concurrency deployments, stay tuned for the async version.

**Nginx**

`X-Accel-Buffering: no` is set automatically — no extra config needed. For long-lived
connections behind a proxy, increase the read timeout:

```nginx
proxy_read_timeout 3600;
proxy_buffering    off;
```

---

## 🔧 Compatibility

| django-flosse | Django    | Python         |
|---------------|-----------|----------------|
| 0.1.x         | 3.2 – 6.0 | 3.9 – 3.14     |

---

## 🗺️ Roadmap

- [ ] **Async support** — native `async def` generator views (ASGI)
- [ ] **Class-based views** — `SSEView` with sync + async support
- [ ] **DRF compatibility** — `authentication_classes`, `permission_classes`, throttling
- [ ] **Optional Redis channel** — fan-out broadcasting for multi-client scenarios

---

## 🤝 Contributing

Contributions are welcome! Whether it's a bug fix, a new feature, or just improving
the docs — feel free to open an issue or submit a pull request.

```bash
git clone https://github.com/youssufshakweh/django-flosse
cd django-flosse
pip install -e ".[test]"
pytest
```

If you have an idea but are not sure where to start, open an issue and let's discuss it first.

---

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
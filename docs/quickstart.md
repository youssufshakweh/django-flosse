# Quick Start

Get your first SSE endpoint up and running in **3 steps** — no configuration required.

---

## 1. Write a generator view

```python title="myapp/views.py"
import time
from django_flosse import sse_stream, SSEEvent


@sse_stream
def progress(request):
    for i in range(1, 11):
        yield ("progress", {"step": i, "total": 10, "pct": i * 10})
        time.sleep(1)

    yield SSEEvent(data="All done!", event="complete")
```

!!! info "What's happening here?"
    - `@sse_stream` turns your generator into a fully-featured SSE endpoint.
    - Each `yield` sends an event to the browser immediately.
    - `SSEEvent` gives you full control over the event name, ID, and retry delay.

---

## 2. Wire up the URL

```python title="myapp/urls.py"
from django.urls import path
from .views import progress

urlpatterns = [
    path("sse/progress/", progress),
]
```

---

## 3. Listen in the browser

```javascript title="myapp/templates/progress.html"
const source = new EventSource("/sse/progress/");

source.addEventListener("progress", (e) => {
    const { step, total, pct } = JSON.parse(e.data);
    console.log(`Step ${step}/${total} — ${pct}%`);
});

source.addEventListener("complete", (e) => {
    console.log(e.data); // "All done!"
    source.close();
});

source.addEventListener("error", () => {
    source.close();
});
```

---

## What you get for free

Every `@sse_stream` view automatically handles:

| What                  | How                                          |
|-----------------------|----------------------------------------------|
| Correct headers       | `Content-Type: text/event-stream`            |
| No proxy buffering    | `X-Accel-Buffering: no`                      |
| No caching            | `Cache-Control: no-cache, no-transform`      |
| Error events          | Exceptions are streamed as `event: error`    |
| JSON serialisation    | Dicts and non-strings are serialised for you |

---

## Next steps

<div class="grid cards" markdown>

-   :material-format-list-bulleted: **Yield Styles**

    Learn all the ways you can yield events.

    [:octicons-arrow-right-24: Yield Styles](user-guide/yield-styles.md)

-   :material-heart-pulse: **Heartbeats**

    Keep connections alive when proxies might close idle streams.

    [:octicons-arrow-right-24: Heartbeats](user-guide/heartbeats.md)

-   :material-server: **Deployment**

    Run in production with Gunicorn, Uvicorn, or Nginx.

    [:octicons-arrow-right-24: Deployment](user-guide/deployment.md)

</div>
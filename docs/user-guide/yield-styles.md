# Yield Styles

`@sse_stream` accepts **any** of these yield styles — use whichever feels most natural.

---

## Plain string

The simplest style — yields an unnamed `message` event.

```python
@sse_stream
def view(request):
    yield "hello"
    yield "world"
```

**Wire format:**
```
data: hello

data: world

```

---

## Tuple — `(event, data)`

The most common style. `data` can be any JSON-serialisable value.

```python
@sse_stream
def view(request):
    yield ("update", {"count": 1})
    yield ("update", {"count": 2})
    yield ("complete", "done")
```

**Wire format:**
```
event: update
data: {"count": 1}

event: update
data: {"count": 2}

event: complete
data: done

```

---

## Tuple — `(event, data, id)`

Same as above, but includes an event ID. Useful for client-side reconnection
— the browser sends the last `id` in the `Last-Event-ID` header on reconnect.

```python
@sse_stream
def view(request):
    yield ("update", {"count": 1}, "evt-001")
    yield ("update", {"count": 2}, "evt-002")
```

**Wire format:**
```
event: update
data: {"count": 1}
id: evt-001

event: update
data: {"count": 2}
id: evt-002

```

---

## Dict with `"data"` key

Maps directly to `SSEEvent` fields. Useful when you want to pass all
fields in one expression.

```python
@sse_stream
def view(request):
    yield {"data": "hello", "event": "greet"}
    yield {"data": {"count": 1}, "event": "update", "id": "evt-1"}
```

Supported keys: `data`, `event`, `id`, `retry`.

---

## Dict without `"data"` key

The entire dict is serialised as JSON and used as the event payload.

```python
@sse_stream
def view(request):
    yield {"foo": "bar", "count": 42}
```

**Wire format:**
```
data: {"foo": "bar", "count": 42}

```

---

## `SSEEvent` object

Full control over every SSE field.

```python
from django_flosse import SSEEvent

@sse_stream
def view(request):
    yield SSEEvent(
        data  = {"status": "done"},
        event = "complete",
        id    = "final",
        retry = 5000,       # tell browser: wait 5s before reconnecting
    )
```

**Wire format:**
```
retry: 5000
id: final
event: complete
data: {"status": "done"}

```

---

## Summary

| What you yield                           | Event name   | Has ID | Has retry |
|------------------------------------------|--------------|--------|-----------|
| `"hello"`                                | *(unnamed)*  | ✗      | ✗         |
| `("update", data)`                       | `update`     | ✗      | ✗         |
| `("update", data, "id-1")`              | `update`     | ✓      | ✗         |
| `{"data": x, "event": "e"}`             | `e`          | ✓*     | ✓*        |
| `{"foo": "bar"}`                         | *(unnamed)*  | ✗      | ✗         |
| `SSEEvent(data=x, event="e", id="1")`   | `e`          | ✓      | ✓         |

!!! tip
    Dict data and all non-string values are serialised to JSON automatically.
    You never need to call `json.dumps()` yourself.
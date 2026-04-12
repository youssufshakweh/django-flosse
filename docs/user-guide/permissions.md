# Permissions

`@sse_stream` supports a `permission_classes` argument — a list of classes
that are checked before the stream starts. **All** must pass or the response
is `HTTP 403`.

---

## Built-in classes

### `AllowAny`

Allows every request — this is the default when `permission_classes=[]`.

```python
from django_flosse.permissions import AllowAny

@sse_stream(permission_classes=[AllowAny])
def view(request):
    yield "open to everyone"
```

---

### `IsAuthenticated`

Requires `request.user.is_authenticated` to be `True`.

```python
from django_flosse.permissions import IsAuthenticated

@sse_stream(permission_classes=[IsAuthenticated])
def view(request):
    yield f"hello {request.user.username}"
```

---

### `IsAdminUser`

Requires `request.user.is_staff` to be `True`.

```python
from django_flosse.permissions import IsAdminUser

@sse_stream(permission_classes=[IsAdminUser])
def admin_stream(request):
    yield "staff only"
```

---

## Custom permissions

Subclass `BaseSSEPermission` and implement `has_permission`:

```python
from django_flosse.permissions import BaseSSEPermission

class HasAPIKey(BaseSSEPermission):
    def has_permission(self, request) -> bool:
        return request.headers.get("X-API-Key") == "secret"

@sse_stream(permission_classes=[HasAPIKey])
def secure_stream(request):
    yield "authenticated via API key"
```

---

## Combining classes

Multiple classes are **AND-ed** — every one must pass:

```python
from django_flosse.permissions import IsAuthenticated, BaseSSEPermission

class IsSubscribed(BaseSSEPermission):
    def has_permission(self, request) -> bool:
        return request.user.profile.is_subscribed

@sse_stream(permission_classes=[IsAuthenticated, IsSubscribed])
def premium_stream(request):
    yield "premium content"
```

!!! warning "Order matters"
    Classes are checked **left to right**. The first one that fails
    returns `403` immediately — the rest are not evaluated.

---

## Summary

| Class             | Allows                               |
|-------------------|--------------------------------------|
| `AllowAny`        | Everyone                             |
| `IsAuthenticated` | Authenticated users                  |
| `IsAdminUser`     | Staff / superusers                   |
| Custom            | Anything you can express in Python   |
# Roadmap

django-flosse is actively developed. Here is what is planned:

---

## ✅ Completed

- [x] **Async support** — native `async def` generator views for ASGI servers
      (Uvicorn, Daphne). *Shipped in v0.2.0.*

## 🗓️ Planned

### v0.3.0 — "The Django Way"
- [ ] **Class-based views** — `SSEView` with sync and async support, matching
      Django's own CBV conventions.
- [ ] **DRF compatibility** — use `authentication_classes`, `permission_classes`,
      and `throttle_classes` from Django REST Framework directly.
- [ ] **`contrib.channels`** — built-in in-memory channel for fan-out broadcasting
      to multiple connected clients, with zero extra dependencies.

### v0.4.0 — "Broadcast Ready"
- [ ] **`contrib.redis`** — Redis-backed channel for multi-process and
      multi-worker deployments (`pip install django-flosse[redis]`).

---

!!! note "Have an idea?"
    Open an issue on [GitHub](https://github.com/youssufshakweh/django-flosse/issues)
    and let's discuss it before you start coding — this keeps the library focused
    and the API consistent.
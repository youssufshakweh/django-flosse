---
hide:
  - navigation
  - toc
---

<div align="center">
  <img src="assets/logo.svg" alt="django-flosse logo" width="140"/>
  <h1 style="font-size:2.4rem; margin: 0.4rem 0 0.2rem;">django-flosse</h1>
  <p style="font-size:1.1rem; color: var(--md-default-fg-color--light);">
    Dead-simple Server-Sent Events for Django via a single decorator.
  </p>
</div>

<div align="center" style="margin: 1rem 0 2rem;">
  <a href="https://pypi.org/project/django-flosse/">
    <img src="https://img.shields.io/pypi/v/django-flosse?color=009688&label=PyPI" alt="PyPI">
  </a>
  <a href="https://pypi.org/project/django-flosse/">
    <img src="https://img.shields.io/pypi/pyversions/django-flosse" alt="Python">
  </a>
  <a href="https://pypi.org/project/django-flosse/">
    <img src="https://img.shields.io/pypi/djversions/django-flosse?label=Django" alt="Django">
  </a>
  <img src="https://img.shields.io/badge/license-MIT-009688" alt="License">
  <img src="https://img.shields.io/badge/coverage-100%25-brightgreen" alt="Coverage">
</div>

```python
from django_flosse import sse_stream

@sse_stream
def live_feed(request):
    for item in my_data_source():
        yield ("update", {"value": item})
```

<div class="grid cards" markdown>

-   :material-download-box: **Install in seconds**

    ```bash
    pip install django-flosse
    ```
    No `INSTALLED_APPS` changes required.

-   :material-lightning-bolt: **Zero boilerplate**

    One decorator. Your generator yields events.
    Headers, permissions, errors — all handled.

-   :material-lan: **Zero threads**

    Iterates your generator directly in the WSGI worker.
    No queues. No background processes.

-   :material-lock-check: **Built-in permissions**

    `IsAuthenticated`, `IsAdminUser`, or bring your own
    `BaseSSEPermission` subclass.

</div>

---

<div align="center">
  <a href="installation/" class="md-button md-button--primary">
    Get Started →
  </a>
  <a href="quickstart/" class="md-button">
    Quick Start
  </a>
</div>
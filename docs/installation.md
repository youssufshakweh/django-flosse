## Requirements

| Requirement | Version    |
|-------------|------------|
| Python      | 3.9 – 3.14 |
| Django      | 4.2 – 6.0  |

!!! note "Dropped support"
    Versions prior to Django 4.2 (3.2, 4.0, 4.1) are no longer supported as of `django-flosse v0.2.0`.
    Please upgrade to Django 4.2+ or pin `django-flosse<0.2.0` for legacy projects.

---

## Install the package

=== "pip"

    <!-- termynal -->
    ```
    $ pip install django-flosse
    ---> 100%
    Installed django-flosse
    ```

=== "uv"

    <!-- termynal -->
    ```
    $ uv add django-flosse
    ---> 100%
    Installed django-flosse
    ```

---

## Virtual environment

It's recommended to install packages inside a virtual environment
to avoid conflicts with your system Python.

=== "pip"

    <!-- termynal -->
    ```
    $ python -m venv .venv
    $ source .venv/bin/activate
    # Windows: .venv\Scripts\activate
    $ pip install django-flosse
    ---> 100%
    Installed django-flosse
    ```

=== "uv"

    <!-- termynal -->
    ```
    $ uv venv
    $ source .venv/bin/activate
    # Windows: .venv\Scripts\activate
    $ uv add django-flosse
    ---> 100%
    Installed django-flosse
    ```

---

## Verify installation

<!-- termynal -->
```
$ python -c "import django_flosse; print(django_flosse.__version__)"
0.2.0a1
```

!!! success "You're ready!"
    No changes to `INSTALLED_APPS` are required.
    Head over to [Quick Start](quickstart.md) to write your first SSE view.
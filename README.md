<div align="center">
  <img src="docs/assets/logo.svg" alt="django-flosse" width="120"/>
  <h1>django-flosse</h1>
  <p>Dead-simple Server-Sent Events for Django via a single decorator.</p>

  <a href="https://pypi.org/project/django-flosse/">
    <img src="https://img.shields.io/pypi/v/django-flosse?color=009688&label=PyPI" alt="PyPI">
  </a>
  <a href="https://pypi.org/project/django-flosse/">
    <img src="https://img.shields.io/pypi/pyversions/django-flosse" alt="Python">
  </a>
  <a href="https://pypi.org/project/django-flosse/">
    <img src="https://img.shields.io/pypi/djversions/django-flosse?label=Django" alt="Django">
  </a>
  <a href="https://pepy.tech/projects/django-flosse">
    <img src="https://static.pepy.tech/personalized-badge/django-flosse?period=monthly&units=INTERNATIONAL_SYSTEM&left_color=GRAY&right_color=GREEN&left_text=downloads" alt="PyPI Downloads">
  </a>
  <img src="https://img.shields.io/badge/license-MIT-009688" alt="License">
  <img src="https://img.shields.io/badge/coverage-100%25-brightgreen" alt="Coverage">
    <img src="https://img.shields.io/badge/async-ready-009688" alt="Async Ready">
</div>

---

```python
from django_flosse import sse_stream

@sse_stream
def live_feed(request):
    for item in my_data_source():
        yield ("update", {"value": item})
```

## Installation

```bash
pip install django-flosse
```

No changes to `INSTALLED_APPS` are required.

## Documentation

Full documentation at **[youssufshakweh.github.io/django-flosse](https://youssufshakweh.github.io/django-flosse)**

- [Quick Start](https://youssufshakweh.github.io/django-flosse/quickstart/)
- [Yield Styles](https://youssufshakweh.github.io/django-flosse/user-guide/yield-styles/)
- [Deployment](https://youssufshakweh.github.io/django-flosse/user-guide/deployment/)
- [API Reference](https://youssufshakweh.github.io/django-flosse/api-reference/)

## Contributing

```bash
git clone https://github.com/youssufshakweh/django-flosse
cd django-flosse
pip install -e ".[test]"
pytest
```

## License

This project is licensed under the [MIT License](LICENSE).
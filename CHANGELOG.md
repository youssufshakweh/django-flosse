# Changelog

All notable changes to django-flosse will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0a1] - 2026-04-23

### Changed
- Marked release as alpha (v0.2.0a1) to indicate early development status

### Removed
- Custom permissions system (use Django native decorators instead)

### Known Limitations
- Error messages not yet fully sanitized for production
- Async GeneratorExit handling incomplete
- No backpressure control for high-concurrency scenarios

*This is an early alpha. Not recommended for production without testing.*

---

## [0.2.0] — 2026-04-15

### Breaking Changes
- **Dropped support for Django <4.2** (3.2, 4.0, 4.1). Minimum required version is now **Django 4.2 (LTS)**.

### Added
- **Async generator support** for `@sse_stream`. Decorate `async def` views that `yield` SSE events:
  ```python
  @sse_stream
  async def live_feed(request):
      async for event in my_async_source():
          yield ("update", event)
  ```

---

## [0.1.2] — 2026-04-10

### Fixed
- Removed `Connection: keep-alive` header — conflicts with HTTP/2 and is
  managed automatically by the server.
- Decorator now supports both `@sse_stream` and `@sse_stream()` usage
  without raising `TypeError`.
- Removed threading and heartbeat — the generator is now iterated directly
  in the WSGI worker with zero extra threads or queues.

### Removed
- `heartbeat_interval` parameter from `@sse_stream`.
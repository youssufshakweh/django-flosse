# Changelog

All notable changes to django-flosse will be documented in this file.

---

## [0.1.2] — 2026

### Fixed
- Removed `Connection: keep-alive` header — conflicts with HTTP/2 and is
  managed automatically by the server.
- Decorator now supports both `@sse_stream` and `@sse_stream()` usage
  without raising `TypeError`.
- Removed threading and heartbeat — the generator is now iterated directly
  in the WSGI worker with zero extra threads or queues.

### Removed
- `heartbeat_interval` parameter from `@sse_stream`.
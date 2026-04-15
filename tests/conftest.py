from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from django.http import HttpRequest


# --------------------------------------------------------------------------- #
# Request helpers                                                              #
# --------------------------------------------------------------------------- #


@pytest.fixture
def rf(db):
    """Django RequestFactory — use when you need a real HttpRequest."""
    from django.test import RequestFactory

    return RequestFactory()


@pytest.fixture
def plain_request() -> HttpRequest:
    """Bare MagicMock shaped like an HttpRequest. No database required."""
    request = MagicMock(spec=HttpRequest)
    request.path = "/sse/test/"
    request.method = "GET"
    return request


@pytest.fixture
def authed_request(plain_request) -> HttpRequest:
    """Request with an authenticated user attached."""
    plain_request.user = MagicMock(is_authenticated=True, is_staff=False)
    return plain_request


@pytest.fixture
def staff_request(plain_request) -> HttpRequest:
    """Request with a staff user attached."""
    plain_request.user = MagicMock(is_authenticated=True, is_staff=True)
    return plain_request


@pytest.fixture
def anon_request(plain_request) -> HttpRequest:
    """Request with an anonymous (unauthenticated) user attached."""
    plain_request.user = MagicMock(is_authenticated=False, is_staff=False)
    return plain_request


# --------------------------------------------------------------------------- #
# Response helper                                                              #
# --------------------------------------------------------------------------- #


def consume(response) -> str:
    """Drain a StreamingHttpResponse into a single string."""
    return "".join(
        chunk.decode() if isinstance(chunk, bytes) else chunk
        for chunk in response.streaming_content
    )


async def async_consume(response) -> str:
    """Drain an async StreamingHttpResponse into a single string."""
    chunks = []
    async for chunk in response.streaming_content:
        chunks.append(chunk.decode() if isinstance(chunk, bytes) else chunk)
    return "".join(chunks)

"""Small in-memory rate limiter (sliding window) for auth / OTP / upload endpoints.

State lives in the process, so limits are per worker. That is fine for the single-worker Railway
deployment; use a shared store (Redis) before running several workers.
"""
import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

_lock = threading.Lock()
_events: dict[str, deque] = defaultdict(deque)
_MAX_KEYS = 20000


def client_ip(request: Request) -> str:
    """Client address as seen by the platform proxy (last X-Forwarded-For hop cannot be spoofed by the client)."""
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[-1].strip() or "unknown"
    return request.client.host if request.client else "unknown"


def _trim(q: deque, now: float, window: float) -> None:
    while q and q[0] <= now - window:
        q.popleft()


def _too_many(q: deque, now: float, window: float, detail: str) -> HTTPException:
    retry = max(1, int(window - (now - q[0])) + 1) if q else int(window)
    return HTTPException(status_code=429, detail=detail, headers={"Retry-After": str(retry)})


def _gc(now: float) -> None:
    if len(_events) > _MAX_KEYS:
        for k in [k for k, q in _events.items() if not q or q[-1] < now - 86400]:
            _events.pop(k, None)


def hit(key: str, limit: int, window: float, detail: str = "Too many attempts. Please try again later.") -> None:
    """Count one event for `key`; raise 429 once more than `limit` happened within `window` seconds."""
    now = time.monotonic()
    with _lock:
        _gc(now)
        q = _events[key]
        _trim(q, now, window)
        if len(q) >= limit:
            raise _too_many(q, now, window, detail)
        q.append(now)


def ensure_not_locked(key: str, limit: int, window: float,
                      detail: str = "Too many failed attempts. Please try again later.") -> None:
    """Raise 429 if `limit` failures were already recorded for `key` within `window` seconds."""
    now = time.monotonic()
    with _lock:
        q = _events.get(key)
        if q is not None:
            _trim(q, now, window)
            if len(q) >= limit:
                raise _too_many(q, now, window, detail)


def record_failure(key: str) -> None:
    with _lock:
        _events[key].append(time.monotonic())


def clear(key: str) -> None:
    with _lock:
        _events.pop(key, None)


def reset() -> None:
    """Forget everything (used by tests)."""
    with _lock:
        _events.clear()

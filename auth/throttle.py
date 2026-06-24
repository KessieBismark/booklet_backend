"""Login throttling / lockout — brute-force protection (SEC002).

Tracks failed login attempts per identifier (use the login email and/or the client IP).
After MAX_LOGIN_ATTEMPTS failures within LOGIN_ATTEMPT_WINDOW seconds the identifier is
locked for LOGIN_LOCKOUT_SECONDS. Entity-agnostic.

Storage is in-process (fine for a single worker / dev). For multiple workers, back the
counters with Redis (keyed the same way) so the lockout is shared — the public functions
below are the seam to do that.
"""
from __future__ import annotations

import os
import threading
import time
from typing import Dict, List, Tuple

MAX_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
ATTEMPT_WINDOW = int(os.getenv("LOGIN_ATTEMPT_WINDOW", "300"))     # rolling window, seconds
LOCKOUT_SECONDS = int(os.getenv("LOGIN_LOCKOUT_SECONDS", "900"))   # lock duration, seconds


class _InProcessThrottleStore:
    """Thread-safe in-process failure/lock tracker. Uses a monotonic clock."""

    def __init__(self) -> None:
        self._failures: Dict[str, List[float]] = {}
        self._locked_until: Dict[str, float] = {}
        self._lock = threading.Lock()

    def is_locked(self, key: str) -> Tuple[bool, float]:
        now = time.monotonic()
        with self._lock:
            until = self._locked_until.get(key, 0.0)
            if until > now:
                return True, until - now
            if key in self._locked_until:
                del self._locked_until[key]
            return False, 0.0

    def record_failure(self, key: str) -> None:
        now = time.monotonic()
        with self._lock:
            recent = [t for t in self._failures.get(key, []) if now - t < ATTEMPT_WINDOW]
            recent.append(now)
            self._failures[key] = recent
            if len(recent) >= MAX_ATTEMPTS:
                self._locked_until[key] = now + LOCKOUT_SECONDS
                self._failures[key] = []

    def reset(self, key: str) -> None:
        with self._lock:
            self._failures.pop(key, None)
            self._locked_until.pop(key, None)


_store = _InProcessThrottleStore()


def is_locked(identifier: str) -> Tuple[bool, float]:
    """Return (locked, retry_after_seconds) for an identifier."""
    return _store.is_locked(identifier)


def record_failed_login(identifier: str) -> None:
    """Call on every failed login. Locks the identifier once the threshold is hit."""
    _store.record_failure(identifier)


def reset_login_attempts(identifier: str) -> None:
    """Call on a successful login to clear the failure counter."""
    _store.reset(identifier)

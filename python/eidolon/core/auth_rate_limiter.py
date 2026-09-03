from __future__ import annotations

import time


class RateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._requests: dict[str, list[float]] = {}

    def _active_requests(self, identifier: str, now: float | None = None) -> list[float]:
        current = time.time() if now is None else now
        window_start = current - self._window_seconds
        active = [request_time for request_time in self._requests.get(identifier, []) if request_time > window_start]
        self._requests[identifier] = active
        return active

    def is_allowed(self, identifier: str) -> bool:
        active = self._active_requests(identifier)
        if len(active) >= self._max_requests:
            return False
        active.append(time.time())
        self._requests[identifier] = active
        return True

    def get_remaining(self, identifier: str) -> int:
        active = self._active_requests(identifier)
        return max(0, self._max_requests - len(active))

import time
from collections import defaultdict
from typing import DefaultDict, List


class RateLimiter:
    """
    Simple sliding-window rate limiter.
    """

    def __init__(self, max_requests: int = 5, window_seconds: int = 1) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._events: DefaultDict[str, List[float]] = defaultdict(list)

    def allow(self, key: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds
        events = [t for t in self._events[key] if t >= window_start]
        self._events[key] = events

        if len(events) >= self.max_requests:
            return False

        self._events[key].append(now)
        return True

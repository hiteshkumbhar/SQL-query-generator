"""Flask extensions and shared helpers."""

import time
from collections import defaultdict
from typing import Dict, List


class SimpleRateLimiter:
    """In-memory rate limiter per IP address."""

    def __init__(self, requests_per_minute: int = 30) -> None:
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        window_start = now - 60.0
        # Filter timestamps within current window
        valid_timestamps = [t for t in self.requests[client_ip] if t > window_start]
        self.requests[client_ip] = valid_timestamps
        if len(valid_timestamps) >= self.requests_per_minute:
            return False
        self.requests[client_ip].append(now)
        return True

    def reset(self) -> None:
        self.requests.clear()


rate_limiter = SimpleRateLimiter()

import time
from collections import defaultdict
from typing import Callable
from fastapi import Request
from app.core.exceptions import RateLimitExceededError

class InMemoryRateLimiter:
    """
    Sliding window in-memory rate limiter.
    Stores timestamps of requests per key (IP or user ID).
    """
    def __init__(self):
        self._requests: dict[str, list[float]] = defaultdict(list)

    def is_rate_limited(self, key: str, max_requests: int, window_seconds: int) -> tuple[bool, int]:
        now = time.time()
        window_start = now - window_seconds
        
        # Prune older timestamps
        self._requests[key] = [t for t in self._requests[key] if t > window_start]
        
        if len(self._requests[key]) >= max_requests:
            oldest = self._requests[key][0]
            retry_after = max(1, int(window_seconds - (now - oldest)))
            return True, retry_after
        
        self._requests[key].append(now)
        return False, 0

    def reset(self):
        """Reset all rate limit tracking (useful for testing)."""
        self._requests.clear()

limiter = InMemoryRateLimiter()

def rate_limit(max_requests: int, window_seconds: int, key_func: Callable[[Request], str] | None = None):
    """
    FastAPI dependency for rate limiting endpoints.
    Default key is client IP address (or forwarded-for header).
    """
    async def dependency(request: Request):
        if key_func:
            key = key_func(request)
        else:
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                key = forwarded.split(",")[0].strip()
            else:
                key = request.client.host if request.client else "unknown"
        
        endpoint = request.url.path
        rate_key = f"{endpoint}:{key}"
        
        is_limited, retry_after = limiter.is_rate_limited(rate_key, max_requests, window_seconds)
        if is_limited:
            raise RateLimitExceededError(
                message=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                retry_after=retry_after
            )
            
    return dependency

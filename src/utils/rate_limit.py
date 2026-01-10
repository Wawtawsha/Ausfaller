import asyncio
import time
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitState:
    """Track rate limit state for a platform."""
    last_request: float = 0.0
    request_count: int = 0
    window_start: float = 0.0
    blocked_until: Optional[float] = None


class RateLimiter:
    """
    Rate limiter with exponential backoff for scraping.

    Implements:
    - Minimum delay between requests
    - Maximum requests per time window
    - Exponential backoff on failures
    """

    def __init__(
        self,
        min_delay: float = 5.0,
        max_requests_per_window: int = 50,
        window_seconds: float = 3600.0,  # 1 hour
        max_backoff: float = 300.0,  # 5 minutes max
    ):
        self.min_delay = min_delay
        self.max_requests_per_window = max_requests_per_window
        self.window_seconds = window_seconds
        self.max_backoff = max_backoff

        self._states: dict[str, RateLimitState] = {}
        self._backoff_multiplier: dict[str, int] = {}

    def _get_state(self, key: str) -> RateLimitState:
        """Get or create state for a platform/endpoint."""
        if key not in self._states:
            self._states[key] = RateLimitState()
        return self._states[key]

    async def acquire(self, key: str = "default") -> None:
        """
        Wait until it's safe to make a request.

        Args:
            key: Identifier for the rate limit bucket (e.g., platform name)
        """
        state = self._get_state(key)
        now = time.time()

        # Check if we're in a backoff period
        if state.blocked_until and now < state.blocked_until:
            wait_time = state.blocked_until - now
            logger.info(f"Rate limit backoff: waiting {wait_time:.1f}s for {key}")
            await asyncio.sleep(wait_time)
            now = time.time()

        # Reset window if needed
        if now - state.window_start > self.window_seconds:
            state.window_start = now
            state.request_count = 0

        # Check if we've hit the window limit
        if state.request_count >= self.max_requests_per_window:
            wait_time = self.window_seconds - (now - state.window_start)
            if wait_time > 0:
                logger.warning(f"Window limit reached for {key}, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                state.window_start = time.time()
                state.request_count = 0

        # Ensure minimum delay between requests
        time_since_last = now - state.last_request
        if time_since_last < self.min_delay:
            await asyncio.sleep(self.min_delay - time_since_last)

        # Update state
        state.last_request = time.time()
        state.request_count += 1

    def report_success(self, key: str = "default") -> None:
        """Report a successful request, reset backoff."""
        if key in self._backoff_multiplier:
            self._backoff_multiplier[key] = 0

        state = self._get_state(key)
        state.blocked_until = None

    def report_failure(self, key: str = "default", is_rate_limit: bool = False) -> float:
        """
        Report a failed request, apply exponential backoff.

        Args:
            key: Rate limit bucket identifier
            is_rate_limit: Whether this was a rate limit error (429)

        Returns:
            The backoff duration in seconds
        """
        multiplier = self._backoff_multiplier.get(key, 0)
        multiplier = min(multiplier + 1, 8)  # Cap at 2^8 = 256x
        self._backoff_multiplier[key] = multiplier

        # Base backoff: 5 seconds for rate limits, 2 seconds for other errors
        base = 5.0 if is_rate_limit else 2.0
        backoff = min(base * (2 ** multiplier), self.max_backoff)

        state = self._get_state(key)
        state.blocked_until = time.time() + backoff

        logger.warning(f"Backoff for {key}: {backoff:.1f}s (multiplier: {multiplier})")
        return backoff

    def get_stats(self, key: str = "default") -> dict:
        """Get current rate limit stats for debugging."""
        state = self._get_state(key)
        now = time.time()

        return {
            "key": key,
            "requests_in_window": state.request_count,
            "window_remaining": max(0, self.window_seconds - (now - state.window_start)),
            "blocked": state.blocked_until is not None and now < state.blocked_until,
            "blocked_remaining": max(0, (state.blocked_until or 0) - now),
        }

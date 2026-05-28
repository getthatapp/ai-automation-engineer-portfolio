"""Async rate limiting utilities."""

import asyncio
import time
from collections import deque
from collections.abc import Awaitable, Callable


class AsyncRateLimiter:
    """Sliding-window async rate limiter.

    The limiter is intentionally small and dependency-free so it can wrap later
    REST, GraphQL and browser-backed calls.
    """

    def __init__(
        self,
        *,
        max_calls: int,
        period_seconds: float,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        """Initialize a sliding-window limiter.

        Args:
            max_calls: Maximum calls allowed per window.
            period_seconds: Window length in seconds.
            clock: Monotonic clock used for tests and runtime.
            sleep: Async sleep function used while waiting.

        Raises:
            ValueError: If limits are not positive.
        """
        if max_calls < 1:
            raise ValueError("max_calls must be at least 1")
        if period_seconds <= 0:
            raise ValueError("period_seconds must be greater than 0")

        self._max_calls = max_calls
        self._period_seconds = period_seconds
        self._clock = clock
        self._sleep = sleep
        self._calls: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until one call is available.

        Side Effects:
            Records the acquisition timestamp in the limiter window.
        """

        while True:
            async with self._lock:
                now = self._clock()
                self._drop_expired_calls(now)

                if len(self._calls) < self._max_calls:
                    self._calls.append(now)
                    return

                wait_for = self._period_seconds - (now - self._calls[0])

            await self._sleep(max(wait_for, 0))

    def _drop_expired_calls(self, now: float) -> None:
        """Remove call timestamps outside the active rate-limit window.

        Args:
            now: Current monotonic timestamp.
        """
        while self._calls and now - self._calls[0] >= self._period_seconds:
            self._calls.popleft()

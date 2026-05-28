"""Retry helpers for transient failures."""

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetryConfig:
    """Configuration for exponential backoff retries."""

    max_attempts: int = 3
    initial_delay_seconds: float = 0.25
    max_delay_seconds: float = 5.0
    backoff_factor: float = 2.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.initial_delay_seconds < 0:
            raise ValueError("initial_delay_seconds must be non-negative")
        if self.max_delay_seconds < 0:
            raise ValueError("max_delay_seconds must be non-negative")
        if self.backoff_factor < 1:
            raise ValueError("backoff_factor must be at least 1")


async def retry_async[T](
    operation: Callable[[], Awaitable[T]],
    *,
    config: RetryConfig | None = None,
    retry_on: tuple[type[BaseException], ...] = (Exception,),
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> T:
    """Run an async operation with bounded retries.

    `asyncio.CancelledError`, `KeyboardInterrupt` and `SystemExit` are not
    retried because they do not inherit from `Exception`.
    """

    retry_config = config or RetryConfig()
    delay = retry_config.initial_delay_seconds

    for attempt in range(1, retry_config.max_attempts + 1):
        try:
            return await operation()
        except retry_on:
            if attempt >= retry_config.max_attempts:
                raise
            await sleep(delay)
            delay = min(delay * retry_config.backoff_factor, retry_config.max_delay_seconds)

    raise RuntimeError("retry loop exhausted unexpectedly")

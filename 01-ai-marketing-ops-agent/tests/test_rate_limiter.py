import pytest

from marketing_ops_agent.utils.rate_limiter import AsyncRateLimiter


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    async def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


@pytest.mark.asyncio
async def test_rate_limiter_waits_after_max_calls() -> None:
    clock = FakeClock()
    limiter = AsyncRateLimiter(
        max_calls=2,
        period_seconds=1.0,
        clock=clock.monotonic,
        sleep=clock.sleep,
    )

    await limiter.acquire()
    await limiter.acquire()
    await limiter.acquire()

    assert clock.sleeps == [1.0]


@pytest.mark.parametrize(
    ("max_calls", "period_seconds"),
    [
        (0, 1.0),
        (1, 0.0),
    ],
)
def test_rate_limiter_rejects_invalid_config(max_calls: int, period_seconds: float) -> None:
    async def fake_sleep(_seconds: float) -> None:
        return None

    with pytest.raises(ValueError):
        AsyncRateLimiter(
            max_calls=max_calls,
            period_seconds=period_seconds,
            sleep=fake_sleep,
            clock=lambda: 0.0,
        )

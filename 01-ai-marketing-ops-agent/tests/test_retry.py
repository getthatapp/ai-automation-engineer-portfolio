import pytest

from marketing_ops_agent.utils.retry import RetryConfig, retry_async


@pytest.mark.asyncio
async def test_retry_async_returns_after_transient_failure() -> None:
    attempts = 0
    sleeps: list[float] = []

    async def flaky_operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise TimeoutError("temporary timeout")
        return "ok"

    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    result = await retry_async(
        flaky_operation,
        config=RetryConfig(max_attempts=3, initial_delay_seconds=0.1),
        retry_on=(TimeoutError,),
        sleep=fake_sleep,
    )

    assert result == "ok"
    assert attempts == 2
    assert sleeps == [0.1]


@pytest.mark.asyncio
async def test_retry_async_raises_after_last_attempt() -> None:
    attempts = 0

    async def always_fails() -> None:
        nonlocal attempts
        attempts += 1
        raise TimeoutError("still failing")

    async def fake_sleep(_seconds: float) -> None:
        return None

    with pytest.raises(TimeoutError):
        await retry_async(
            always_fails,
            config=RetryConfig(max_attempts=2, initial_delay_seconds=0),
            retry_on=(TimeoutError,),
            sleep=fake_sleep,
        )

    assert attempts == 2


def test_retry_config_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        RetryConfig(max_attempts=0)

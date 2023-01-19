from asyncio import CancelledError
from asyncio import TimeoutError as AsyncioTimeoutError
from asyncio import sleep, wait_for

from pytest import mark, raises

from nextcore.common.errors import RateLimitedError
from nextcore.http.global_rate_limiter import UnlimitedGlobalRateLimiter
from tests.utils import match_time


@mark.asyncio
@match_time(0, 0.1)
async def test_no_limit() -> None:
    rate_limiter = UnlimitedGlobalRateLimiter()

    for _ in range(10):
        async with rate_limiter.acquire():
            ...


@mark.asyncio
async def test_locking() -> None:
    rate_limiter = UnlimitedGlobalRateLimiter()

    async def use_lock():
        async with rate_limiter.acquire():
            ...

    await wait_for(use_lock(), timeout=0.1)

    rate_limiter.update(5)
    await sleep(1)
    with raises(AsyncioTimeoutError):
        await wait_for(use_lock(), timeout=0.1)


@mark.asyncio
async def test_no_wait() -> None:
    rate_limiter = UnlimitedGlobalRateLimiter()

    async with rate_limiter.acquire(wait=False):
        # Should be good here

        rate_limiter.update(1)  # Emulate that we got rate limited

    await sleep(0)  # Switch contexts.

    with raises(RateLimitedError):
        async with rate_limiter.acquire(wait=False):
            ...


@mark.asyncio
async def test_cancel() -> None:
    rate_limiter = UnlimitedGlobalRateLimiter()

    with raises(CancelledError):
        async with rate_limiter.acquire():
            raise CancelledError()
    assert len(rate_limiter._pending_requests) == 0, "Pending request was not cleared"  # type: ignore [reportPrivateUsage]

@mark.asyncio
@match_time(1, .1)
async def test_reset() -> None:
    rate_limiter = UnlimitedGlobalRateLimiter()

    rate_limiter.update(1)

    await sleep(.5) # Ensure it registers

    async with rate_limiter.acquire():
        ...

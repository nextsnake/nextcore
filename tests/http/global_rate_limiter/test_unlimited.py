from asyncio import TimeoutError as AsyncioTimeoutError
from asyncio import wait_for, sleep

from pytest import mark, raises

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

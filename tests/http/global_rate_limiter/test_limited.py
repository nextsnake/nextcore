from asyncio import create_task, sleep
from logging import getLogger

from pytest import mark

from nextcore.http.global_rate_limiter import LimitedGlobalRateLimiter
from tests.utils import match_time

@mark.asyncio
@match_time(0, 0.1)
async def test_with_limit() -> None:
    rate_limiter = LimitedGlobalRateLimiter(limit=2)

    for _ in range(2):
        async with rate_limiter.acquire():
            ...


@mark.asyncio
@match_time(1, 0.1)
async def test_exceeds_limit() -> None:
    rate_limiter = LimitedGlobalRateLimiter(limit=2)

    for _ in range(4):
        async with rate_limiter.acquire():
            ...


@mark.asyncio
async def test_exceeds_limit_concurrent() -> None:
    logger = getLogger("testing")

    async def use_rate_limiter():
        async with rate_limiter.acquire():
            ...

    rate_limiter = LimitedGlobalRateLimiter(limit=4)

    for i in range(9):
        logger.debug("Created task %s", i)
        create_task(use_rate_limiter())
    await sleep(1)  # No clue why .1 is needed here...
    pending_requests = rate_limiter._pending_requests.qsize()
    assert pending_requests == 1, f"Expected 1 pending request, got {pending_requests}"

    # Cancel the remaining task for a clean output
    rate_limiter._pending_requests.get_nowait().future.set_result(None)

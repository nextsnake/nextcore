from asyncio import Task, create_task, sleep
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

    await rate_limiter.close()


@mark.asyncio
@match_time(1, 0.1)
async def test_exceeds_limit() -> None:
    rate_limiter = LimitedGlobalRateLimiter(limit=2)

    for _ in range(4):
        async with rate_limiter.acquire():
            ...

    await rate_limiter.close()


@mark.asyncio
async def test_exceeds_limit_concurrent() -> None:
    logger = getLogger("testing")

    async def use_rate_limiter():
        async with rate_limiter.acquire():
            ...

    rate_limiter = LimitedGlobalRateLimiter(limit=4)
    tasks: list[Task[None]] = []

    for i in range(9):
        logger.debug("Created task %s", i)
        tasks.append(create_task(use_rate_limiter()))
    await sleep(1.1)  # Add a bit of extra margin just in case
    pending_requests = [task for task in tasks if not task.done()]
    assert len(pending_requests) == 1, f"Expected 1 pending request, got {len(pending_requests)}"

    await rate_limiter.close()

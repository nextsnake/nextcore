from asyncio import TimeoutError as AsyncioTimeoutError
from asyncio import create_task, sleep, wait_for
from logging import getLogger

from pytest import mark, raises

from nextcore.http.global_lock import GlobalLock
from tests.utils import match_time


@mark.asyncio
@match_time(0, 0.1)
async def test_no_limit() -> None:
    lock = GlobalLock()

    for _ in range(10):
        async with lock:
            ...


@mark.asyncio
@match_time(0, 0.1)
async def test_with_limit() -> None:
    lock = GlobalLock(limit=2)

    for _ in range(2):
        async with lock:
            ...


@mark.asyncio
@match_time(1, 0.1)
async def test_exceeds_limit() -> None:
    lock = GlobalLock(limit=2)

    for _ in range(4):
        async with lock:
            ...


@mark.asyncio
async def test_locking() -> None:
    lock = GlobalLock(None)

    async def use_lock():
        async with lock:
            ...

    await wait_for(use_lock(), timeout=0.1)

    lock.lock()
    with raises(AsyncioTimeoutError):
        await wait_for(use_lock(), timeout=0.1)
    lock.unlock()
    await wait_for(use_lock(), timeout=0.1)


@mark.asyncio
async def test_exceeds_limit_concurrent() -> None:
    logger = getLogger("testing")

    async def use_lock():
        async with lock:
            ...

    lock = GlobalLock(limit=4)

    for i in range(9):
        logger.debug("Created task %s", i)
        create_task(use_lock())
    await sleep(2.1)  # No clue why .1 is needed here...
    assert len(lock._pending) == 1, f"Expected 1 pending lock, got {len(lock._pending)}"

    # Cancel the remaining task for a clean output
    lock._pending[0].cancel()

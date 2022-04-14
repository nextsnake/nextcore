from asyncio import TimeoutError as AsyncioTimeoutError, wait_for, create_task, sleep

from pytest import mark, raises

from nextcore.http.global_lock import GlobalLock
from tests.utils import match_time


@mark.asyncio
@match_time(0, 0.1)
async def test_no_limit():
    lock = GlobalLock()

    for _ in range(10):
        async with lock:
            ...


@mark.asyncio
@match_time(0, 0.1)
async def test_with_limit():
    lock = GlobalLock(limit=2)

    for _ in range(2):
        async with lock:
            ...


@mark.asyncio
@match_time(1, 0.1)
async def test_exceeds_limit():
    lock = GlobalLock(limit=2)

    for _ in range(4):
        async with lock:
            ...


@mark.asyncio
async def test_locking():
    lock = GlobalLock()

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
@match_time(2, 0.1)
async def test_exceeds_limit_concurrent():
    async def use_lock():
        async with lock:
            ...

    lock = GlobalLock(limit=2)

    for _ in range(4):
        create_task(use_lock())
    await sleep(0.5) # Switch context
    await use_lock()
    print(lock._pending)


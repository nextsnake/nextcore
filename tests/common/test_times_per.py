from pytest import mark, raises

from nextcore.common.errors import RateLimitedError
from nextcore.common.times_per import TimesPer
from tests.utils import match_time


@mark.asyncio
@match_time(0, 0.1)
async def test_should_not_sleep():
    rate_limiter = TimesPer(5, 5)

    for _ in range(5):
        async with rate_limiter.acquire():
            ...

    await rate_limiter.close()


@mark.asyncio
@match_time(0.1, 0.01)
async def test_should_sleep():
    rate_limiter = TimesPer(5, 0.1)

    for _ in range(10):
        async with rate_limiter.acquire():
            ...

    await rate_limiter.close()


def test_repr():
    repr(TimesPer(1, 1))


@mark.asyncio
@match_time(0, 0.01)
async def test_exception_undos():
    rate_limiter = TimesPer(1, 1)

    for _ in range(100):
        try:
            async with rate_limiter.acquire():
                raise RuntimeError("This is a test exception to undo the rate limit use!")
        except:
            pass

    await rate_limiter.close()


@mark.asyncio
async def test_no_wait():
    rate_limiter = TimesPer(1, 1)

    async with rate_limiter.acquire(wait=False):
        ...  # Good!

    with raises(RateLimitedError):
        async with rate_limiter.acquire(wait=False):
            ...

    await rate_limiter.close()


@mark.asyncio
@match_time(0, 0.1)
async def test_reset_offset_negative():
    rate_limiter = TimesPer(1, 1)
    rate_limiter.reset_offset_seconds = -1

    for _ in range(100):
        async with rate_limiter.acquire():
            ...


@mark.asyncio
@match_time(2, 0.1)
async def test_reset_offset_positive():
    rate_limiter = TimesPer(1, 1)
    rate_limiter.reset_offset_seconds = 1

    for _ in range(2):
        async with rate_limiter.acquire():
            ...

from pytest import mark

from nextcore.common.times_per import TimesPer
from tests.utils import match_time


@mark.asyncio
@match_time(0, 0.1)
async def test_should_not_sleep():
    rate_limiter = TimesPer(5, 5)

    for _ in range(5):
        async with rate_limiter.acquire():
            ...


@mark.asyncio
@match_time(0.1, 0.01)
async def test_should_sleep():
    rate_limiter = TimesPer(5, 0.1)

    for _ in range(10):
        async with rate_limiter.acquire():
            ...


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

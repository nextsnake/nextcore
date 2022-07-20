from pytest import mark

from nextcore.gateway.times_per import TimesPer
from tests.utils import match_time


@mark.asyncio
@match_time(0, 0.1)
async def test_should_not_sleep():
    ratelimiter = TimesPer(5, 5)

    for _ in range(5):
        await ratelimiter.wait()


@mark.asyncio
@match_time(0.1, 0.01)
async def test_should_sleep():
    ratelimiter = TimesPer(5, 0.1)

    for _ in range(10):
        await ratelimiter.wait()


def test_repr():
    repr(TimesPer(1, 1))

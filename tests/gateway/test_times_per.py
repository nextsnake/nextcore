from time import time

from pytest import mark

from nextcore.gateway.times_per import TimesPer


@mark.asyncio
async def test_should_not_sleep():
    ratelimiter = TimesPer(5, 5)

    start = time()
    for _ in range(5):
        await ratelimiter.wait()
    end = time()
    time_used = end - start
    assert time_used <= 1, f"Time used should be ~0s, but was {time_used}s"


@mark.asyncio
async def test_should_sleep():
    ratelimiter = TimesPer(5, 0.1)

    start = time()
    for _ in range(10):
        await ratelimiter.wait()
    end = time()
    time_used = end - start

    assert time_used >= 0.1, f"Time used should be ~0.1s, but was {time_used}s"
    assert time_used <= 0.2, f"Time used should be ~0.1s, but was {time_used}s"

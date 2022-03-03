import asyncio

from pytest import mark

from nextcore.http.bucket import Bucket
from tests.utils import match_time


@mark.asyncio
@match_time(0.2, 0.1)
async def test_consecutive():
    bucket = Bucket()
    bucket.update(1, 1, 0.1)

    for _ in range(3):
        async with bucket:
            bucket.update(1, 0, 0.1)


async def use_bucket(bucket):
    async with bucket:
        # It needs a update to be reset.
        bucket.update(1, 0, 0.1)


@mark.asyncio
@match_time(0.2, 0.1)
async def test_concurrently():
    bucket = Bucket()

    bucket.update(1, 1, 0.1)

    tasks = [use_bucket(bucket) for _ in range(3)]
    await asyncio.gather(*tasks)


@mark.asyncio
@match_time(0, 0.1)
async def test_failure_no_info():
    bucket = Bucket()

    for _ in range(5):
        async with bucket:
            ...


@mark.asyncio
@match_time(0, 0.1)
async def test_failure_initial_info():
    bucket = Bucket()

    bucket.update(1, 1, 0.1)

    for _ in range(3):
        async with bucket:
            ...

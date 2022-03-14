import asyncio

from pytest import mark

from nextcore.http.bucket import Bucket
from nextcore.http.bucket_metadata import BucketMetadata
from tests.utils import match_time


@mark.asyncio
@match_time(0.2, 0.1)
async def test_consecutive():
    metadata = BucketMetadata(limit=1)
    bucket = Bucket(metadata)
    await bucket.update(1, 0.1)

    for _ in range(3):
        async with bucket.acquire():
            await bucket.update(0, 0.1)


async def use_bucket(bucket: Bucket):
    async with bucket.acquire():
        # It needs a update to be reset.
        await bucket.update(0, 0.1)


@mark.asyncio
@match_time(0.2, 0.1)
async def test_concurrently():
    metadata = BucketMetadata(limit=1)
    bucket = Bucket(metadata)

    await bucket.update(1, 0.1)

    tasks = [use_bucket(bucket) for _ in range(3)]
    await asyncio.gather(*tasks)


@mark.asyncio
@match_time(0, 0.1)
async def test_failure_no_info():
    metadata = BucketMetadata()
    bucket = Bucket(metadata)

    for _ in range(5):
        async with bucket.acquire():
            ...


@mark.asyncio
@match_time(0, 0.1)
async def test_failure_initial_info():
    metadata = BucketMetadata(limit=1)
    bucket = Bucket(metadata)

    await bucket.update(1, 0.1)

    for _ in range(3):
        async with bucket.acquire():
            ...


@mark.asyncio
@match_time(0, 0.1)
async def test_unlimited():
    metadata = BucketMetadata(limit=1)
    bucket = Bucket(metadata)

    await bucket.update(1, 1)
    metadata.unlimited = True

    for _ in range(3):
        async with bucket.acquire():
            ...

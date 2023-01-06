import asyncio

from pytest import mark, raises
from nextcore.common.errors import RateLimitedError

from nextcore.http.bucket import Bucket
from nextcore.http.bucket_metadata import BucketMetadata
from tests.utils import match_time


@mark.asyncio
@match_time(0.2, 0.1)
async def test_consecutive() -> None:
    metadata = BucketMetadata(limit=1)
    bucket = Bucket(metadata)
    await bucket.update(1, 0.1)

    for _ in range(3):
        async with bucket.acquire():
            await bucket.update(0, 0.1)


async def use_bucket(bucket: Bucket) -> None:
    async with bucket.acquire():
        # It needs a update to be reset.
        await bucket.update(0, 0.1)


@mark.asyncio
@match_time(0.2, 0.1)
async def test_concurrently() -> None:
    metadata = BucketMetadata(limit=1)
    bucket = Bucket(metadata)

    await bucket.update(1, 0.1)

    tasks = [use_bucket(bucket) for _ in range(3)]
    await asyncio.gather(*tasks)


@mark.asyncio
@match_time(0, 0.1)
async def test_failure_no_info() -> None:
    metadata = BucketMetadata()
    bucket = Bucket(metadata)

    for _ in range(5):
        async with bucket.acquire():
            ...


@mark.asyncio
@match_time(0, 0.1)
async def test_failure_initial_info() -> None:
    metadata = BucketMetadata(limit=1)
    bucket = Bucket(metadata)

    await bucket.update(1, 0.1)

    for _ in range(3):
        async with bucket.acquire():
            ...


@mark.asyncio
@match_time(0, 0.1)
async def test_unlimited() -> None:
    metadata = BucketMetadata(limit=1)
    bucket = Bucket(metadata)

    await bucket.update(1, 1)
    metadata.unlimited = True

    for _ in range(3):
        async with bucket.acquire():
            ...

@mark.asyncio
async def test_out_no_wait() -> None:
    metadata = BucketMetadata(limit=1)
    bucket = Bucket(metadata)

    await bucket.update(0, 1)

    with raises(RateLimitedError):
        async with bucket.acquire(wait=False):
            ...

@mark.asyncio
@mark.skipif(True, reason="Currently broken")
@match_time(0, 0.1)
async def test_re_release() -> None:
    metadata = BucketMetadata(limit=1)
    bucket = Bucket(metadata)

    started: asyncio.Future[None] = asyncio.Future()
    can_raise: asyncio.Future[None] = asyncio.Future()

    await bucket.update(1, 1)

    async def use():
        try:
            async with bucket.acquire():
                started.set_result(None)
                await can_raise
                raise
        except:
            pass
    
    asyncio.create_task(use())

    await started
    can_raise.set_result(None)
    async with bucket.acquire():
        ...



# Dirty tests
def test_clean_bucket_is_not_dirty() -> None:
    metadata = BucketMetadata()
    bucket = Bucket(metadata)

    assert not bucket.dirty, "Bucket was dirty on a clean bucket."


@mark.asyncio
async def test_dirty_bucket_reserved() -> None:
    metadata = BucketMetadata(limit=1)
    bucket = Bucket(metadata)

    async with bucket.acquire():
        assert bucket.dirty, "Bucket was not dirty on a bucket that was reserved"


@mark.asyncio
async def test_dirty_remaining_used() -> None:
    metadata = BucketMetadata(limit=1)
    bucket = Bucket(metadata)

    async with bucket.acquire():
        await bucket.update(0, 1)

    assert bucket.dirty, "Bucket was not dirty on a bucket that was used"

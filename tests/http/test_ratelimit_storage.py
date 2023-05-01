import gc
import sys

from pytest import mark

from nextcore.http import Bucket, BucketMetadata
from nextcore.http.rate_limit_storage import RateLimitStorage


# Garbage collection
@mark.asyncio
async def test_does_gc_collect_unused_buckets() -> None:
    storage = RateLimitStorage()

    metadata = BucketMetadata()
    bucket = Bucket(metadata)

    nextcore_id = "abc123"

    await storage.store_bucket_by_nextcore_id(nextcore_id, bucket)
    gc.collect()

    assert await storage.get_bucket_by_nextcore_id(nextcore_id) is None, "Bucket was not collected"

    await storage.close()


@mark.asyncio
async def test_does_not_collect_dirty_buckets() -> None:
    storage = RateLimitStorage()

    metadata = BucketMetadata()
    bucket = Bucket(metadata)

    nextcore_id = "abc123"

    await bucket.update(0, 1)

    await storage.store_bucket_by_nextcore_id(nextcore_id, bucket)
    gc.collect()

    assert await storage.get_bucket_by_nextcore_id(nextcore_id) is not None, "Bucket should not be collected"

    await storage.close()


@mark.asyncio
async def test_cleans_up_gc_hook() -> None:
    storage = RateLimitStorage()

    before_callbacks_length = len(gc.callbacks)

    # Run the garbage collector
    await storage.close()

    # Check that the hook was removed
    print(gc.callbacks)
    assert len(gc.callbacks) == before_callbacks_length - 1, "Hook was not removed"


# Getting and storing buckets
@mark.asyncio
async def test_stores_and_get_nextcore_id() -> None:
    storage = RateLimitStorage()

    metadata = BucketMetadata()
    bucket = Bucket(metadata)

    nextcore_id = "abc123"

    assert await storage.get_bucket_by_nextcore_id(nextcore_id) is None, "Bucket should not exist as it is not added yet"

    await storage.store_bucket_by_nextcore_id(nextcore_id, bucket)
    assert await storage.get_bucket_by_nextcore_id(nextcore_id) is bucket, "Bucket was not stored"

    await storage.close()

@mark.asyncio
async def test_stores_and_get_discord_id() -> None:
    storage = RateLimitStorage()

    metadata = BucketMetadata()
    bucket = Bucket(metadata)

    discord_bucket_hash = "abc123"

    assert await storage.get_bucket_by_discord_id(discord_bucket_hash) is None, "Bucket should not exist as it is not added yet"

    await storage.store_bucket_by_discord_id(discord_bucket_hash, bucket)
    assert await storage.get_bucket_by_discord_id(discord_bucket_hash) is bucket, "Bucket was not stored"

    await storage.close()

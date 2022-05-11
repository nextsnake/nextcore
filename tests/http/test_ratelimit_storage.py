import gc

from pytest import mark

from nextcore.http import Bucket, BucketMetadata
from nextcore.http.ratelimit_storage import RatelimitStorage
import sys


# Garbage collection
@mark.asyncio
async def test_does_gc_collect_unused_buckets() -> None:
    storage = RatelimitStorage()

    metadata = BucketMetadata()
    bucket = Bucket(metadata)

    await storage.store_bucket_by_nextcore_id(1, bucket)
    gc.collect()

    assert await storage.get_bucket_by_nextcore_id(1) is None, "Bucket was not collected"


@mark.asyncio
async def test_does_not_collect_dirty_buckets() -> None:
    storage = RatelimitStorage()

    metadata = BucketMetadata()
    bucket = Bucket(metadata)

    await bucket.update(0, 1)

    await storage.store_bucket_by_nextcore_id(1, bucket)
    gc.collect()

    assert await storage.get_bucket_by_nextcore_id(1) is not None, "Bucket should not be collected"

@mark.asyncio
async def test_cleans_up_gc_hook() -> None:
    storage = RatelimitStorage()
    
    before_callbacks_length = len(gc.callbacks)

    # Run the garbage collector
    await storage.close()
    
    # Check that the hook was removed
    print(gc.callbacks)
    assert len(gc.callbacks) == before_callbacks_length - 1, "Hook was not removed"


# Getting and storing buckets
@mark.asyncio
async def test_stores_and_get_nextcore_id() -> None:
    storage = RatelimitStorage()

    metadata = BucketMetadata()
    bucket = Bucket(metadata)

    assert await storage.get_bucket_by_nextcore_id(1) is None, "Bucket should not exist as it is not added yet"

    await storage.store_bucket_by_nextcore_id(1, bucket)
    assert await storage.get_bucket_by_nextcore_id(1) is bucket, "Bucket was not stored"


@mark.asyncio
async def test_stores_and_get_discord_id() -> None:
    storage = RatelimitStorage()

    metadata = BucketMetadata()
    bucket = Bucket(metadata)

    assert await storage.get_bucket_by_discord_id("1") is None, "Bucket should not exist as it is not added yet"

    await storage.store_bucket_by_discord_id("1", bucket)
    assert await storage.get_bucket_by_discord_id("1") is bucket, "Bucket was not stored"

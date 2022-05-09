import gc

from pytest import mark

from nextcore.http import Bucket, BucketMetadata
from nextcore.http.ratelimit_storage import RatelimitStorage


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

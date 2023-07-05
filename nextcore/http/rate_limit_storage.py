# The MIT License (MIT)
# Copyright (c) 2021-present tag-epic
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from __future__ import annotations

import gc
from logging import getLogger
from typing import TYPE_CHECKING
from weakref import WeakValueDictionary

from .global_rate_limiter import BaseGlobalRateLimiter, LimitedGlobalRateLimiter

if TYPE_CHECKING:
    from typing import Final, Literal

    from .bucket import Bucket
    from .bucket_metadata import BucketMetadata

logger = getLogger(__name__)

__all__: Final[tuple[str, ...]] = ("RateLimitStorage",)


class RateLimitStorage:
    """Storage for rate limits for a user.

    One of these should be created for each user.

    .. note::
        This will register a gc callback to clean up the buckets.

    Attributes
    ----------
    global_lock:
        The users per user global rate limit.
    """

    __slots__ = ("_nextcore_buckets", "_discord_buckets", "_bucket_metadata", "global_rate_limiter")

    def __init__(self) -> None:
        self._nextcore_buckets: dict[str, Bucket] = {}
        self._discord_buckets: WeakValueDictionary[str, Bucket] = WeakValueDictionary()
        self._bucket_metadata: dict[
            str, BucketMetadata
        ] = {}  # This will never get cleared however it improves performance so I think not deleting it is fine
        self.global_rate_limiter: BaseGlobalRateLimiter = LimitedGlobalRateLimiter()

        # Register a garbage collection callback
        gc.callbacks.append(self._cleanup_buckets)

    # These are async and not just public dicts because we want to support custom implementations that use asyncio.
    # This does introduce some overhead, but it's not too bad.
    async def get_bucket_by_nextcore_id(self, nextcore_id: str) -> Bucket | None:
        """Get a rate limit bucket from a nextcore created id.

        Parameters
        ----------
        nextcore_id:
            The nextcore generated bucket id. This can be gotten by using :attr:`Route.bucket`
        """
        return self._nextcore_buckets.get(nextcore_id)

    async def store_bucket_by_nextcore_id(self, nextcore_id: str, bucket: Bucket) -> None:
        """Store a rate limit bucket by nextcore generated id.

        Parameters
        ----------
        nextcore_id:
            The nextcore generated id of the
        bucket:
            The bucket to store.
        """
        self._nextcore_buckets[nextcore_id] = bucket

    async def get_bucket_by_discord_id(self, discord_id: str) -> Bucket | None:
        """Get a rate limit bucket from the Discord bucket hash.

        This can be obtained via the ``X-Ratelimit-Bucket`` header.

        Parameters
        ----------
        discord_id:
            The Discord bucket hash
        """
        return self._discord_buckets.get(discord_id)

    async def store_bucket_by_discord_id(self, discord_id: str, bucket: Bucket) -> None:
        """Store a rate limit bucket by the discord bucket hash.

        This can be obtained via the ``X-Ratelimit-Bucket`` header.

        Parameters
        ----------
        discord_id:
            The Discord bucket hash
        bucket:
            The bucket to store.
        """
        self._discord_buckets[discord_id] = bucket

    async def get_bucket_metadata(self, bucket_route: str) -> BucketMetadata | None:
        """Get the metadata for a bucket from the route.

        Parameters
        ----------
        bucket_route:
            The bucket route.
        """
        return self._bucket_metadata.get(bucket_route)

    async def store_metadata(self, bucket_route: str, metadata: BucketMetadata) -> None:
        """Store the metadata for a bucket from the route.

        Parameters
        ----------
        bucket_route:
            The bucket route.
        metadata:
            The metadata to store.
        """
        self._bucket_metadata[bucket_route] = metadata

    # Garbage collection
    def _cleanup_buckets(self, phase: Literal["start", "stop"], info: dict[str, int]) -> None:
        del info  # Unused

        if phase == "stop":
            # No need to clean up buckets after the gc is done.
            return
        logger.debug("Cleaning up buckets")

        # We are copying it due to the size changing during the loop
        for bucket_id, bucket in self._nextcore_buckets.copy().items():
            if not bucket.dirty:
                logger.debug("Cleaning up bucket %s", bucket_id)
                # Delete the main reference. Other references like RateLimitStorage._discord_buckets should get cleaned up automatically as it is a weakref.
                del self._nextcore_buckets[bucket_id]

    async def close(self) -> None:
        """Clean up before deletion.

        .. warning::
            If this is not called before you delete this or it goes out of scope, you will get a memory leak.
        """
        # Remove the garbage collection callback
        gc.callbacks.remove(self._cleanup_buckets)

        await self.global_rate_limiter.close()

        # Clear up the buckets
        for bucket in self._nextcore_buckets.values():
            await bucket.close()

        self._nextcore_buckets.clear()

        # Clear up the metadata
        self._bucket_metadata.clear()

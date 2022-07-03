# The MIT License (MIT)
# Copyright (c) 2021-present nextcore developers
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

from asyncio import get_running_loop
from contextlib import asynccontextmanager
from logging import getLogger
from typing import TYPE_CHECKING

from .request_session import RequestSession

if TYPE_CHECKING:
    from typing import AsyncIterator, Final

    from .bucket_metadata import BucketMetadata

logger = getLogger(__name__)

__all__: Final[tuple[str, ...]] = ("Bucket",)


class Bucket:
    """A discord ratelimit implementation around a bucket.

    Parameters
    ----------
    metadata:
        The metadata for the bucket.

    Attributes
    ----------
    metadata:
        The metadata for the bucket.
    """

    __slots__ = (
        "metadata",
        "_remaining",
        "_reserved",
        "_pending",
        "_pending_reset",
        "_fetched_ratelimit_info",
        "__weakref__",
    )

    def __init__(self, metadata: BucketMetadata) -> None:
        self.metadata: BucketMetadata = metadata
        self._remaining: int | None = self.metadata.limit
        self._reserved: list[RequestSession] = []  # Requests currently being processed
        self._pending: list[RequestSession] = []  # Requests waiting for a spot
        self._pending_reset: bool = False  # Waiting for the bucket to reset
        self._fetched_ratelimit_info: bool = False  # Initial fetch of ratelimit info

    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[None]:  # TODO: Fix type
        """Reserve a spot in the bucket to do a request.

        **Example usage**

        .. code-block:: python

            async with bucket.acquire():
                # Do request
                await bucket.update(...)
        """
        session = await self._aenter()
        try:
            yield None
        finally:
            await self._aexit(session)

    async def _aenter(self) -> RequestSession:
        """Start a request session."""
        session = RequestSession(self.metadata.unlimited)

        if self._remaining is None:
            # No info! Let's do one request at once to fetch ratelimits.
            remaining = 1
        else:
            # Info gathered, let's use it.
            remaining = self._remaining

        # No spots left
        if not self.metadata.unlimited and remaining - self._reserved_count == 0:
            # No more spots, add it as a pending request
            logger.debug(
                "No more spots in ratelimit, waiting! Remaining: %s, reserved: %s", remaining, self._reserved_count
            )
            self._pending.append(session)
            await session.pending_future

        # We have a spot, reserve it!
        self._reserved.append(session)

        return session

    async def _aexit(self, session: RequestSession) -> None:
        """Clean up a request session

        Parameters
        ----------
        session:
            The session to clean up.
        """
        self._reserved.remove(session)

        if not self._fetched_ratelimit_info:
            if self.metadata.unlimited:
                # Unlimited, this is handled in Bucket.update
                pass
            elif self._remaining is not None:
                # Info fetched, let this buckets requests through
                self._fetched_ratelimit_info = True
                self._release_pending(self._remaining)
            else:
                # Request failed, attempt another one!
                self._release_pending(1)

            self._fetched_ratelimit_info = True

    @property
    def _reserved_count(self) -> int:
        """How many requests are currently being processed."""
        limited_reserved = filter(lambda session: not session.unlimited, self._reserved)
        return len(list(limited_reserved))

    async def update(
        self, remaining: int | None = None, reset_after: float | None = None, *, unlimited: bool = False
    ) -> None:
        """Update the internal bucket state with information from the discord headers.

        .. note::
            This should be called before exiting the :func:`Bucket.acquire` context menu.
        .. note::
            This does not update the metadata!

        Parameters
        ----------
        remaining:
            The number of requests remaining in the bucket.
        reset_after:
            The time in seconds until the bucket resets.
        unlimited:
            Whether the bucket is unlimited.
        """
        if not unlimited:
            # Not unlimited

            # Validation
            if remaining is None:
                raise ValueError("Remaining must be set if unlimited is False.")
            if reset_after is None:
                raise ValueError("Reset after must be set if unlimited is False.")

            # Update remaining
            # TODO: Fix race condition where receiving from a old bucket after reset.
            if self._remaining is None:
                self._remaining = remaining
            else:
                # This fixes a race condition when receiving the ratelimit
                self._remaining = min(self._remaining, remaining)
            if not self._pending_reset:
                self._pending_reset = True

                # TODO: Can we use asyncio.call_later or similar?
                loop = get_running_loop()
                loop.call_later(reset_after, self._reset)
        else:
            self._release_pending()

    def _reset(self) -> None:
        self._remaining = self.metadata.limit
        self._pending_reset = False
        self._release_pending(
            self.metadata.limit or len(self._pending)
        )  # Release limit or all if we are suddenly unlimited

    def _release_pending(self, limit: int | None = None) -> None:
        if limit is None:
            limit = len(self._pending)

        # Make sure we don't try to release more requests than is pending
        limit = min(limit, len(self._pending))

        logger.debug("Releasing %s pending requests", limit)

        for session in self._pending[:limit]:
            session.pending_future.set_result(None)
            self._pending.remove(session)

    @property
    def dirty(self) -> bool:
        """Whether the bucket is currently any different from a clean bucket created from a :class:`BucketMetadata`."""
        if self._pending:
            # Requests are pending! Deleting the bucket would cause issues.
            logger.debug("Bucket is dirty due to pending requests.")
            return True
        if self._reserved:
            # Requests are reserved! Deleting the bucket would cause issues.
            logger.debug("Bucket is dirty due to reserved requests.")
            return True
        if self.metadata.unlimited:
            # Returning early as the rest of the checks is irrelevant.
            logger.debug("Bucket is clean due to being unlimited.")
            return False
        if self._remaining != self.metadata.limit:
            # Remaining is different from the metadata
            logger.debug("Bucket is dirty due to remaining being different from limit.")
            return True
        logger.debug("Bucket is clean due to all checks passing.")
        return False

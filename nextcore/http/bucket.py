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

from asyncio import CancelledError, Event, get_running_loop
from contextlib import asynccontextmanager
from logging import getLogger
from queue import PriorityQueue
from typing import TYPE_CHECKING, cast, overload

from nextcore.common.errors import RateLimitedError

from .request_session import RequestSession

if TYPE_CHECKING:
    from typing import AsyncIterator, Final, Literal

    from .bucket_metadata import BucketMetadata

logger = getLogger(__name__)

__all__: Final[tuple[str, ...]] = ("Bucket",)


class Bucket:
    """A discord rate limit implementation around a bucket.

    **Example usage**

    .. code-block:: python3

        bucket_metadata = BucketMetadata()
        bucket = Bucket(bucket_metadata)

        async with bucket.acquire():
            # Do request
            await bucket.update(remaining, reset_after_seconds, unlimited=False)

    Parameters
    ----------
    metadata:
        The metadata for the bucket.

    Attributes
    ----------
    metadata:
        The metadata for the bucket.

        This should also be updated with info that applies to all buckets like limit and if it is unlimited.
    reset_offset_seconds:
        How much the resetting should be offset to account for processing/networking delays.

        This will be added to the reset time, so for example a offset of ``1`` will make resetting 1 second slower.
    """

    __slots__ = (
        "metadata",
        "reset_offset_seconds",
        "_remaining",
        "_pending",
        "_reserved",
        "_resetting",
        "_can_do_blind_request",
        "__weakref__",
    )

    def __init__(self, metadata: BucketMetadata):
        self.metadata: BucketMetadata = metadata
        self.reset_offset_seconds: float = 0
        self._remaining: int | None = None  # None signifies unlimited or not used yet (due to a optimization)
        self._pending: PriorityQueue[RequestSession] = PriorityQueue()
        self._reserved: list[RequestSession] = []
        self._resetting: bool = False
        self._can_do_blind_request: Event = Event()

        self._can_do_blind_request.set()

    @asynccontextmanager
    async def acquire(self, *, priority: int = 0, wait: bool = True) -> AsyncIterator[None]:
        """Use a spot in the rate limit.

        **Example usage**

        .. code-block:: python3

            async with bucket.acquire():
                # Do request
                await bucket.update(remaining, reset_after_seconds, unlimited=False)

        Parameters
        ----------
        priority:
            The priority of a request. A lower number means it will be executed faster.
        wait:
            Wait for a spot in the rate limit.

            If this is set to :data:`False`, this will raise :exc:`RateLimitedError` if no spot is available right now.

        Raises
        ------
        RateLimitedError
            You are rate limited and ``wait`` was set to :data:`False`
        """
        if self.metadata.unlimited:
            # Instantly return and avoid touching any of the state.
            yield
            return

        if self._remaining is None and self.metadata.limit is not None:
            # We have info from metadata! Use that
            self._remaining = self.metadata.limit

        if self._remaining is not None:
            # Already using this bucket

            session = RequestSession(priority=priority)

            estimated_remaining = self._remaining - len(
                self._reserved
            )  # We assume every request is successful, and retry when that is not the case.

            if estimated_remaining == 0:
                if not wait:
                    raise RateLimitedError()
                self._pending.put_nowait(
                    session
                )  # This can't raise a exception as pending is always infinite unless someone else modified it
                await session.pending_future  # Wait for a spot in the rate limit.
                # This will automatically be removed by the waker.

            self._reserved.append(session)
            try:
                yield  # Let the user do the request
            except:
                # Release one request as we assume the request failed.
                if self._pending.qsize() >= 1:
                    self._release_pending(1)

                raise  # Re-raise the exception
            finally:
                self._reserved.remove(session)
            return

        # We have no info on rate limits, so we have to do a "blind" request to find out what the rate limits is.
        # We will only do one "blind" request at a time per bucket though in case the rate limit is small.
        # This could be tweaked to use more on routes with higher rate limits, however this would require hard coding which is not a thing I want
        # for nextcore.
        session = RequestSession(priority=priority)

        if self._can_do_blind_request.is_set():
            self._can_do_blind_request.clear()

            self._reserved.append(session)
            try:
                yield  # Let the user do the request
            except:
                # Release one request as we assume the request failed.
                if self._pending.qsize() >= 1:
                    self._release_pending(1)

                raise  # Re-raise the exception
            else:
                if self._remaining is None:
                    logger.warning("A user of Bucket is not calling .update! This will cause performance issues...")
                    self._release_pending(1)
                else:
                    self._release_pending(self._remaining)
            finally:
                self._reserved.remove(session)
                self._can_do_blind_request.set()
                logger.debug("Done cleaning up blind request!")
            return

        # Currently doing blind request
        await self._can_do_blind_request.wait()

        # Try again
        async with self.acquire(priority=priority, wait=wait):
            yield

    @overload
    async def update(self, *, unlimited: Literal[True]) -> None:
        ...

    @overload
    async def update(self, remaining: int, reset_after: float, *, unlimited: Literal[False] = False) -> None:
        ...

    async def update(
        self, remaining: int | None = None, reset_after: float | None = None, *, unlimited: bool = False
    ) -> None:
        if unlimited:
            # Updating metadata is handled by the HTTPClient, so we do not need to do this.

            # Release remaining requests
            self._release_pending()
        else:
            self._remaining = remaining

            # Start a reset
            if self._resetting:
                return  # Don't do it when there is already a reset in progress

            self._resetting = True

            # Call the reset callback (after the reset duration)
            reset_after = cast(float, reset_after)
            loop = get_running_loop()
            loop.call_later(reset_after + self.reset_offset_seconds, self._reset_callback)

    def _reset_callback(self) -> None:
        self._resetting = False  # Allow future resets
        self._remaining = None  # It should use metadata's limit as a starting point.

        # Reset up to the limit
        self._release_pending(self.metadata.limit)

    def _release_pending(self, max_count: int | None = None):
        if max_count is None:
            max_count = self._pending.qsize()
        else:
            max_count = min(max_count, self._pending.qsize())

        for _ in range(max_count):
            session = self._pending.get_nowait()  # This can't raise a exception due to the guard clause.

            # Mark it as completed in the queue to avoid a infinitly overflowing int
            self._pending.task_done()

            session.pending_future.set_result(None)

    @property
    def dirty(self) -> bool:
        """Whether the bucket is currently any different from a clean bucket created from a :class:`BucketMetadata`.

        This can be for example if any requests is being made, or if the bucket is waiting for a reset.
        """
        if self._reserved:
            return True  # Currently doing a request.

        if self.metadata.unlimited:
            return False  # Unlimited, following stuff does not matter

        if self._remaining is not None:
            return True  # Some edits to remaining has been done

        return False

    async def close(self):
        """Cleanup this instance.

        This should be done when this instance is never going to be used anymore

        .. warning::
            Continued use of this instance will result in instability
        """
        for session in self._pending.queue:
            session.pending_future.set_exception(CancelledError)

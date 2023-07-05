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

from asyncio import CancelledError, Future, Lock, create_task, sleep
from collections import deque
from contextlib import asynccontextmanager
from logging import getLogger
from typing import TYPE_CHECKING, AsyncIterator

from nextcore.common.errors import RateLimitedError

from .base import BaseGlobalRateLimiter

if TYPE_CHECKING:
    from asyncio import Task
    from typing import Final

__all__: Final[tuple[str, ...]] = ("UnlimitedGlobalRateLimiter",)

logger = getLogger(__name__)


class UnlimitedGlobalRateLimiter(BaseGlobalRateLimiter):
    """A global rate-limiting implementation

    This works by allowing infinite requests until one fail,
    and when one fails stop further requests from being made until ``retry_after`` is done.

    .. warning::
        This may cause a lot of 429's. Please use :class:`LimitedGlobalRateLimiter`
        unless you are sure you need this.
    .. warning::
        This is slower than other implementations due to using Discord's time.

        There is some extra delay due to ping due to this.
    """

    __slots__ = ("_pending_requests", "_pending_release", "_async_update_task")

    def __init__(self) -> None:
        self._pending_requests: deque[Future[None]] = deque()
        self._pending_release: Lock = Lock()
        self._async_update_task: Task[None] | None = None

    @asynccontextmanager
    async def acquire(self, *, priority: int = 0, wait: bool = True) -> AsyncIterator[None]:
        """Acquire a spot in the rate-limit

        Parameters
        ----------
        priority:
            .. warning::
                Request priority currently does nothing.
        wait:
            Whether to wait for a spot in the rate limit.

            If this is :data:`False`, this will raise :exc:`RateLimitedError` instead.

        Raises
        ------
        RateLimitedError
            ``wait`` was set to :data:`False` and we are rate limited.

        Returns
        -------
        :class:`typing.AsyncContextManager`
            A context manager that will wait in __aenter__ until a request should be made.
        """
        del priority  # Unused
        if self._pending_release.locked():
            # Rate limited!

            if not wait:
                raise RateLimitedError()

            # Add to queue
            future: Future[None] = Future()
            self._pending_requests.append(future)

            # Wait
            try:
                await future
            except CancelledError:
                logger.debug("Ratelimit use was cancelled while it was pending. Cancelling!")
                self._pending_requests.remove(future)
                raise  # Don't continue
        yield None

    def update(self, retry_after: float) -> None:
        """Updates the rate-limiter with info from a global scoped 429.

        Parameters
        ----------
        retry_after:
            The time from the `retry_after` field in the JSON response or the `retry_after` header.

            .. hint::
                The JSON field has more precision than the header.
        """
        logger.debug("Exceeded global rate-limit, however this is expected.")
        if self._pending_release.locked():
            logger.debug("Ignoring update because of already running update task.")
            return
        self._async_update_task = create_task(self._async_update(retry_after))

    async def _async_update(self, retry_after: float) -> None:
        """Async version of :attr:`UnlimitedGlobalRateLimiter`"""
        # Sanity check due to race conditions
        if self._pending_release.locked():
            logger.debug("Ignoring update because of already running update task.")
            self._async_update_task = None
            return
        async with self._pending_release:
            logger.debug("Resetting global lock after %ss", retry_after)
            await sleep(retry_after)
            logger.debug("Resetting global lock!")

        # Let all requests run again.
        for future in self._pending_requests:
            # Remove it
            self._pending_requests.popleft()

            # Release it to do the request
            future.set_result(None)

        self._async_update_task = None

    async def close(self) -> None:
        """Cleanup this instance.

        This should be done when this instance is never going to be used anymore

        .. warning::
            Continued use of this instance will result in instability
        """

        # No need to run .clear on this, as the .acquire function does it for us.
        for request in self._pending_requests:
            request.set_exception(CancelledError)

        if self._async_update_task is not None:
            self._async_update_task.cancel()

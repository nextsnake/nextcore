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

from asyncio import Future, get_running_loop
from contextlib import asynccontextmanager
from logging import getLogger
from queue import PriorityQueue
from typing import TYPE_CHECKING, AsyncIterator

from .priority_queue_container import PriorityQueueContainer

if TYPE_CHECKING:
    from typing import Final

__all__: Final[tuple[str, ...]] = ("TimesPer",)

logger = getLogger(__name__)


class TimesPer:
    """A smart TimesPer implementation.

    Parameters
    ----------
    limit:
        The amount of times the rate limiter can be used
    per:
        How often this resets in seconds
    """

    __slots__ = ("limit", "per", "remaining", "_pending", "_in_progress", "_pending_reset")

    def __init__(self, limit: int, per: int) -> None:
        self.limit: int = limit
        self.per: float = per
        self.remaining: int = limit
        self._pending: PriorityQueue[PriorityQueueContainer] = PriorityQueue()
        self._in_progress: int = 0
        self._pending_reset: bool = False

    @asynccontextmanager
    async def acquire(self, *, priority: int = 0) -> AsyncIterator[None]:
        """Use a spot in the rate-limit.

        Parameters
        ----------
        priority:
            The priority. **Lower** number means it will be requested earlier.

        Returns
        -------
        :class:`typing.AsyncContextManager`
            A context manager that will wait in __aenter__ until a request should be made.
        """

        calculated_remaining = self.remaining - self._in_progress
        logger.debug("Calculated remaining: %s", calculated_remaining)
        logger.debug("Reserved requests: %s", self._in_progress)

        if calculated_remaining == 0:
            future: Future[None] = Future()
            item = PriorityQueueContainer(priority, future)

            self._pending.put_nowait(item)

            logger.debug("Added request to queue with priority %s", priority)
            await future
            logger.debug("Out of queue, doing request")

        self._in_progress += 1
        try:
            yield None
        except:
            # A exception occured. This will not take from the rate-limit, and as so we have to re-allow a request to run
            if self._pending.qsize() != 0:
                container = self._pending.get_nowait()
                future = container.future

                # Mark it as completed, good practice (and saves a bit of memory due to a infinitly expanding int)
                self._pending.task_done()

                # Release it and allow further requests
                future.set_result(None)

            raise  # Re-raise exception
        finally:
            # Start a reset task
            if not self._pending_reset:
                self._pending_reset = True
                loop = get_running_loop()
                loop.call_later(self.per, self._reset)

            self._in_progress -= 1

        # This only gets called if no exception got raised.
        self.remaining -= 1

    def _reset(self) -> None:
        self._pending_reset = False

        self.remaining = self.limit

        to_release = min(self._pending.qsize(), self.remaining - self._in_progress)
        logger.debug("Releasing %s requests", to_release)
        for _ in range(to_release):
            container = self._pending.get_nowait()
            future = container.future

            # Mark it as completed, good practice (and saves a bit of memory due to a infinitly expanding int)
            self._pending.task_done()

            # Release it and allow further requests
            future.set_result(None)
        if self._pending.qsize():
            self._pending_reset = True

            loop = get_running_loop()
            loop.call_later(self.per, self._reset)

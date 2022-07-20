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

from asyncio import Event, Future, get_running_loop
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

logger = getLogger(__name__)

__all__ = ("GlobalLock",)


class GlobalLock:
    """A ratelimiter that works towards a Discord global lock.

    Example usage:

    .. code-block:: python

        lock = GlobalLock(limit=50)

        async with lock:
            ...

    Parameters
    ----------
    limit: :class:`int`
        The maximum number of requests that can be made per second.

        .. warning::
            If this is :data:`None`, the ratelimiter will try until .lock() is called.
            This can be useful if your global limit is dynamic.

            This can result in a temporary cloudflare ban (1h ban on all requests from your IP).
    """

    def __init__(self, limit: int | None = 50) -> None:
        self._limit: int | None = limit

        # Limit is set
        self._remaining: int | None = limit
        self._pending: list[Future[None]] = []
        self._reserved: int = 0
        self._reset_pending: bool = False

        # Limit is not set
        self._unknown_lock: Event = Event()

        # Initial set to allow by-default passing
        self._unknown_lock.set()

    def lock(self) -> None:
        """Locks the ratelimiter.

        .. warning::
            This will only work if :attr:`GlobalLock.limit` is :data:`None`.

        Raises
        ------
        :exc:`RuntimeError`
            This method cannot be used if :attr:`GlobalLock.limit` is not :data:`None`.
        """
        if self._limit is not None:
            raise RuntimeError("Lock cannot be used while limit is not None")
        self._unknown_lock.clear()

    def unlock(self) -> None:
        """Undoes the effect of :meth:`GlobalLock.lock`.

        Raises
        ------
        :exc:`RuntimeError`
            :meth:`GlobalLock.lock` has to be called before this method.
        """
        if self._unknown_lock.is_set():
            raise RuntimeError("Unlock cannot be used while the GlobalLock is not locked")
        self._unknown_lock.set()

    async def __aenter__(self) -> None:
        # No limit set
        if self._limit is None:
            if not self._unknown_lock.is_set():
                await self._unknown_lock.wait()
                return await self.__aenter__()
            return

        # Limit set

        # Someone could technically modify _remaining to be out of sync with limit
        assert self._remaining is not None, "Remaining is None but limit is not None"

        if self._effective_remaining <= 0:
            future: Future[None] = Future()
            self._pending.append(future)
            logger.debug("Used up this second, adding to pending queue")
            await future

        self._reserved += 1

    async def __aexit__(self, *_: Any) -> None:
        # No limit set
        if self._limit is None:
            return

        # Limit set

        # Someone could technically modify _remaining to be out of sync with limit
        assert self._remaining is not None, "Remaining is None but limit is not None"

        self._reserved -= 1
        self._remaining -= 1

        # Reset
        # Only start one reset task at once. If not, there would be a lot more tasks cleared than it should.
        if not self._reset_pending:
            self._reset_pending = True

            # Reset the global. This will remove up to limit tasks from the pending queue and clear up remaining
            loop = get_running_loop()
            loop.call_later(1, self._reset)

    def _reset(self) -> None:
        assert self._reset_pending, "Reset pending is False but reset is called"
        assert self._limit is not None, "Reset was called but limit is None"
        assert self._remaining is not None, "Remaining is None but limit is not None"

        self._reset_pending = False

        self._remaining = self._limit

        for future_id, future in enumerate(self._pending):
            if future_id >= self._limit:
                logger.debug("Reset done, %s pending left", len(self._pending))
                return
            logger.debug("Letting future %s through", future_id)
            future.set_result(None)
            self._pending.remove(future)

    @property
    def _effective_remaining(self) -> int:
        assert self._remaining is not None, "Remaining is not set"
        return self._remaining - self._reserved

    @property
    def limit(self) -> int | None:
        """How many requests can be made per second.

        Raises
        ------
        :exc:`ValueError`
            Limit cannot be switched between :data:`None` and not :data:`None`
        :exc:`ValueError`
            Limit cannot be switched between not :data:`None` and :data:`None`
        :exc:`ValueError`
            Limit has to be greater than 0
        """
        return self._limit

    @limit.setter
    def limit(self, value: int | None) -> None:
        if self.limit is None and value is not None:
            raise ValueError("Cannot switch limit between None and not None")
        if self.limit is not None and value is None:
            raise ValueError("Cannot switch limit between not None and None")
        if value is not None and value <= 0:
            raise ValueError("Limit must be greater than 0")

        self._limit = value

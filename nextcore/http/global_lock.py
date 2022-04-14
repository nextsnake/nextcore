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
    """Minified version of :class:`Bucket` to allow for no info at all.

    Attributes
    ----------
    limit: :class:`int` | :data:`None`
        .. warning::
            Changing between a :class:`int` and :data:`None` after a use will cause this to break.
        How many times this can be acquired per second.
    """

    __slots__ = ("limit", "_remaining", "_reserved", "_active", "_pending_reset", "_pending")

    def __init__(self, limit: int | None = 50) -> None:
        self.limit: int | None = limit
        self._remaining: int | None = self.limit
        self._reserved: int = 0
        self._active: Event = Event()
        self._pending_reset: bool = False
        self._pending: list[Future[None]] = []

        # Set initial info
        self._active.set()

    async def __aenter__(self) -> None:
        if not self._active.is_set():
            logger.debug("Waiting for global lock")
            await self._active.wait()
            await self.__aenter__()

        # No data handling
        if self.limit is None or self._remaining is None:
            self._reserved += 1
            return  # We have no info, lets just try and see if it works
        
        logger.debug("%s/%s left on ratelimit", self._remaining - self._reserved, self.limit)
        if self._remaining - self._reserved <= 0:
            # Ratelimit is full, wait until ready!
            logger.debug("Ratelimit is full, waiting for it to be ready")

            future: Future[None] = Future()
            self._pending.append(future)
            await future

        self._reserved += 1

        if not self._pending_reset and self.limit is not None:
            self._pending_reset = True

            logger.debug("Creating reset task")

            # Reset
            loop = get_running_loop()
            loop.call_later(1, self._reset)

    async def __aexit__(self, *_: Any) -> None:
        self._reserved -= 1
        if self._remaining is not None:
            logger.debug("Changing remaining to %s", self._remaining - 1)
            # TODO: Return once bug is fixed
            # assert self._remaining <= 0, "Remaining numbers are bugged, remaining was set to less than 0"
            self._remaining -= 1

    def _reset(self) -> None:
        """Resets the internal state letting :attr:`limit` free"""
        assert self.limit is not None, "Limit was not set"
        # Allow future resets
        self._pending_reset = False

        self._remaining = self.limit

        for i, future in enumerate(self._pending):
            if i >= self.limit:
                return
            logger.debug("Resetting %s", i)
            future.set_result(None)
            self._pending.remove(future)

    def lock(self) -> None:
        """Locks the GlobalLock meaning no further calls will go through unless :meth:`GlobalLock.unlock` is called

        .. warning::
            This cannot be used if :attr:`limit` is not :data:`None`
        """
        self._active.clear()

    def unlock(self) -> None:
        """Unlocks the GlobalLock meaning calls will go through again

        .. warning::
            This cannot be used if :attr:`limit` is not :data:`None`
        """
        self._active.set()

    def __repr__(self) -> str:
        return f"<GlobalLock limit={self.limit} remaining={self._remaining} reserved={self._reserved} blocking={not self._active.is_set()} pending={len(self._pending)}>"

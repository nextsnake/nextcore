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
from typing import TYPE_CHECKING
from logging import getLogger

if TYPE_CHECKING:
    from typing import Any, Final

logger = getLogger(__name__)

class GlobalLock:
    """Minified version of :class:`Bucket` to allow for no info at all."""

    def __init__(self, limit: int | None = None) -> None:
        self.limit: Final[int | None] = limit
        """How many times this can be acquired per second"""
        self._remaining: int | None = self.limit
        self._reserved: int = 0
        self._active: Event = Event()
        self._pending_reset: bool = False
        self._pending: list[Future[None]] = []

        # Set initial info
        self._active.set()

    async def __aenter__(self) -> None:
        if not self._active.is_set():
            await self._active.wait()
            await self.__aenter__()

        # No data handling
        if self.limit is None or self._remaining is None:
            self._reserved += 1
            return  # We have no info, lets just try and see if it works

        if self._remaining - self._reserved <= 0:
            # Ratelimit is full, wait until ready!
            logger.debug("Ratelimit is full, waiting for it to be ready")

            future: Future[None] = Future()
            self._pending.append(future)
            await future

        self._reserved += 1

        if not self._pending_reset and self.limit is not None:
            self._pending_reset = True

            # Reset
            loop = get_running_loop()
            loop.call_later(1, self._reset)

            self._pending_reset = False

    async def __aexit__(self, *_: Any) -> None:
        self._reserved -= 1
        if self._remaining is not None:
            self._remaining -= 1

    def _reset(self) -> None:
        """Resets the internal state letting :attr:`limit` free"""
        assert self.limit is not None, "Limit was not set"

        self._remaining = self.limit
        self._active.set()

        for i, future in enumerate(self._pending):
            if i > self.limit:
                return
            future.set_result(None)

    def lock(self) -> None:
        """Locks the GlobalLock meaning no further calls will go through unless :meth:`GlobalLock.unlock` is called"""
        self._active.clear()

    def unlock(self) -> None:
        """Unlocks the GlobalLock meaning calls will go through again"""
        self._active.set()

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

import time
from asyncio import Future, get_running_loop
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional

logger = getLogger(__name__)


class TimesPer:
    """A simple ratelimiting implementation

    .. note::
        This does not reserve when you call :meth:`TimesPer.wait`, for that use :class:`Bucket`
    Parameters
    ----------
    total: int
        The total number of times this can be used per period.
    per: float
        How long each period lasts in seconds.
    """

    __slots__ = ("total", "remaining", "per", "reset_at", "_loop", "_waiting")

    def __init__(self, total: int, per: float):
        self.total: int = total
        self.remaining: int = total
        self.per: float = per
        self.reset_at: Optional[float] = None

        self._waiting: List[Future[None]] = []

    async def wait(self) -> None:
        """Waits until the ratelimit is available
        This will return immediately if the ratelimit is available
        """
        if self.reset_at is None:
            # No info was found, start a reset
            self.reset_at = time.time() + self.per
            loop = get_running_loop()
            loop.call_later(self.per, self._reset)
        if self.remaining <= 0:  # Just in case we get some bad calculations
            # Ran out, lets wait.
            future: Future[None] = Future()
            self._waiting.append(future)
            await future
        self.remaining -= 1

    def _reset(self) -> None:
        """Resets the ratelimit
        This will end the current period.
        If there are any left waiting after removing :attr:`TimesPer.total`, the method will call itself.
        """
        self.reset_at = None
        self.remaining = self.total

        self._drop(self.total)

        if self._waiting:
            # There is still some waiting, they would not be released until someone else uses this if this was not here.
            self.reset_at = time.time() + self.per
            loop = get_running_loop()
            loop.call_later(self.per, self._reset)

    def _drop(self, limit: int) -> None:
        """Releases pending calls to :meth:`TimesPer.wait`

        Parameters
        ----------
        limit: int
            The max number of calls to release.
        """
        for _ in range(limit):
            try:
                self._waiting.pop().set_result(None)
            except IndexError:
                break

    def __repr__(self) -> str:
        return f"TimesPer(total={self.total}, per={self.per}, remaining={self.remaining} waiting={len(self._waiting)} reset_at={self.reset_at})"

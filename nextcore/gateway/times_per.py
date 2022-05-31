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

from asyncio import Lock, sleep
from logging import getLogger
from time import time

logger = getLogger(__name__)

__all__ = ("TimesPer",)


class TimesPer:
    """A simple ratelimiting implementation

    .. note::
        This does not reserve when you call :meth:`TimesPer.wait`, for that use :class:`Bucket`

    Example usage:

    .. code-block:: python

        times_per = TimesPer(10, 1)

        await times_per.wait()

    Parameters
    ----------
    total:
        The total number of times this can be used per period.
    per:
        How long each period lasts in seconds.

    Attributes
    ----------
    total:
        The amount of times this can be used per period.
    remaining:
        How many times this can be used this period.
    per:
        How long each period lasts in seconds.
    """

    __slots__ = ("total", "remaining", "per", "_reset_at", "_lock")

    def __init__(self, total: int, per: float):
        self.total: int = total
        self.remaining: int = total
        self.per: float = per

        self._reset_at: float | None = None
        self._lock: Lock = Lock()

    async def wait(self) -> None:
        """Waits until the ratelimit is available
        This will return immediately if the ratelimit is available
        """
        async with self._lock:
            current_time = time()
            if self._reset_at is None or self._reset_at < current_time:
                # Time expired, reset.
                self._reset_at = current_time + self.per
                self.remaining = self.total
            if self.remaining == 0:
                await sleep(self._reset_at - current_time)
            self.remaining -= 1

    @property
    def reset_at(self) -> float | None:
        """When the ratelimit will reset

        Returns
        -------
        :class:`float`
            Unix timestamp of when the ratelimit will reset.
        :data:`None`
            There is no reset scheduled.
        """
        reset_at = self._reset_at

        if reset_at is None or reset_at <= time():
            return None

        return self._reset_at

    @property
    def reset_after(self) -> float | None:
        """How many seconds until the ratelimit will reset

        Returns
        -------
        :class:`float`
            The number of seconds until the ratelimit will reset
        :data:`None`
            There is no reset scheduled.
        """
        reset_at = self.reset_at

        if reset_at is None:
            return None

        return time() - reset_at

    def __repr__(self) -> str:
        return f"TimesPer(total={self.total}, per={self.per}, remaining={self.remaining} waiting={self._lock.locked} reset_at={self.reset_at})"

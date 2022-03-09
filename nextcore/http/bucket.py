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
from logging import getLogger
from typing import TYPE_CHECKING

from .flood_gate import FloodGate

if TYPE_CHECKING:
    from typing import Any
    from typing_extensions import Self

logger = getLogger(__name__)


class Bucket:
    """A HTTP ratelimit handler

    .. note::
        View the `documentation <https://discord.dev/topics/rate-limits>`_
    """

    __slots__ = ("limit", "_pending", "_pending_reset", "_remaining", "_reserved", "_loop", "_first_fetch_ratelimit")

    def __init__(self) -> None:
        self.limit: int | None = None
        """How many this bucket can hold. This will be None if the info has not been fetched yet."""

        self._pending: list[Future[None]] = []
        self._pending_reset: bool = False
        self._remaining: int | None = None
        self._reserved: int = 0
        self._first_fetch_ratelimit = FloodGate()

        # Let the first request through to fetch initial info
        self._first_fetch_ratelimit.pop()

    def update(self, limit: int, remaining: int, reset_after: float) -> None:
        """Update the internal bucket counters

        Parameters
        ----------
        limit: int
            How many requests this bucket can hold
        remaining: int
            How many requests the current bucket can hold
        reset_after: float
            How many seeconds until we reset.
        """
        self.limit = limit
        self._remaining = remaining

        if not self._pending_reset:
            self._pending_reset = True

            loop = get_running_loop()
            loop.call_later(reset_after, self._reset)

    def _reset(self) -> None:
        """Reset the state of this bucket"""
        self._pending_reset = False
        assert self.limit is not None, "Can't reset when bucket info has not been fetched yet."
        self._remaining = self.limit

        drop_count = self._remaining - self._reserved
        logger.debug("Attempting to drop %s pending requests", drop_count)
        self._drop_pending(drop_count)

    def _drop_pending(self, limit: int) -> None:
        """Make up to limit waiting requests return

        Parameters
        ----------
        limit: :class:`int`
            How many to requests to attempt to return. If there is not enough it will return early.
        """
        # This is not optimal as if there is multiple bots on the same token there would be a few ratelimit responses
        # There is also a issue with globals however there is really no way to solve that.
        for _ in range(limit):
            try:
                future = self._pending.pop(0)
            except IndexError:
                return
            future.set_result(None)

    async def __aenter__(self) -> Self: # type: ignore [valid-type] TODO: Remove this after it's fixed in mypy.
        if self._remaining is not None:
            # Bucket has info.
            if self._remaining - self._reserved <= 0:
                # Bucket used up, wait for it to complete
                future: Future[None] = Future()
                self._pending.append(future)
                await future
        else:
            flood = await self._first_fetch_ratelimit.acquire()
            if flood:
                return await self.__aenter__()
            logger.debug("Letting ratelimit fetcher through")

        self._reserved += 1
        return self

    async def __aexit__(self, *_: Any) -> None:
        # There is no reason to decrement remaining here as it should always be updated by Bucket.update
        self._reserved -= 1

        if self._remaining is not None:
            self._first_fetch_ratelimit.drain()
        else:
            # It failed, try again.
            logger.debug("Could not fetch initial ratelimit info, trying again")
            self._first_fetch_ratelimit.pop()

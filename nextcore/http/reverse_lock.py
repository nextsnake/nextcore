# The MIT License (MIT)
# Copyright (c) 2021-present nextcore developers
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
from __future__ import annotations

from asyncio import AbstractEventLoop, Event, get_event_loop
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Optional


class ReversedTimedEvent:
    """:class:`asyncio.Event` but default-open. It also includes a clear_after time."""

    def __init__(self) -> None:
        self._loop: AbstractEventLoop = get_event_loop()
        self._event: Event = Event()
        self._event.set()

    async def wait(self) -> None:
        """Wait for the event to be unset"""
        await self._event.wait()

    def set(self, clear_after: Optional[float] = None) -> None:
        """Set/lock the event
        This will block anyone who calls :meth:`ReversedTimedEvent.wait`

        Args:
            clear_after (Optional[float]): In seconds when the event gets unset.
        """
        self._event.clear()

        if clear_after is not None:
            self._loop.call_later(clear_after, self._event.set)

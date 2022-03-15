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

from asyncio import Future

__all__ = ("PopEvent",)


class PopEvent:
    """A :class:`asyncio.Event` that allows popping the first waiting task."""

    __slots__ = ("_pending", "_set")

    def __init__(self) -> None:
        self._pending: list[Future[bool]] = []
        """Tasks waiting for a pop or set."""
        self._set: bool = False

    def set(self) -> None:
        """Sets the event and clears all waiting tasks.
        This will also make all future calls to :meth:`PopEvent.wait` instantly return
        """
        self._set = True

        # Clear waiting
        for future in self._pending:
            future.set_result(True)

    def clear(self) -> None:
        """Makes future calls to :meth:`PopEvent.wait` not return unless :meth:`PopEvent.set` or :meth:`PopEvent.pop` is called."""
        self._set = False

    async def wait(self) -> bool:
        """Waits until :meth:`PopEvent.set` or :meth:`PopEvent.pop` is called."""
        if self._set:
            return True

        future: Future[bool] = Future()
        self._pending.append(future)
        return await future

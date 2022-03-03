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

from asyncio import Future


class FloodGate:
    """A class to partially or fully drain a queue

    You can call :meth:`FloodGate.pop` to only remove the first element in.
    You can call :meth:`FloodGate.drain` to empty the entire queue and all future occurences.
    """

    def __init__(self) -> None:
        self._pending: list[Future[bool]] = []
        self._remove_next: bool = False
        self.drained: bool = False

    def drain(self) -> None:
        """Clear out all waiting tasks.
        This will also make all future tasks immidiatly return.
        """
        for future in self._pending:
            future.set_result(True)
        self._pending.clear()
        self.drained = True

    def pop(self) -> None:
        """Make the first task return.
        If there is no task waiting the next task will immidiatly return.

        Raises:
            ValueError: If the FloodGate is drained or if it has already been popped while empty.
        """
        if self.drained:
            raise ValueError("FloodGate has been already been drained") from None
        try:
            self._pending.pop(0).set_result(False)
        except IndexError:
            if self._remove_next:
                raise ValueError("Cannot queue two pops") from None
            self._remove_next = True

    async def acquire(self) -> bool:
        """Wait for a :meth:`FloodGate.drain` or :meth:`FloodGate.pop`

        Returns:
            bool: If the FloodGate was drained.
        """
        if self._remove_next:
            self._remove_next = False
            return False
        if self.drained:
            return False
        future: Future[bool] = Future()
        self._pending.append(future)
        return await future

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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asyncio import Future
    from typing import Final

__all__: Final[tuple[str, ...]] = ("PriorityQueueContainer",)


class PriorityQueueContainer:
    """A container for times per uses for :class:`queue.PriorityQueue` to ignore the future when comparing greater than and less than

    Parameters
    ----------
    priority:
        The request priority. This will be compared!
    future:
        The future for when the request is done

    Attributes
    ----------
    priority:
        The request priority. This will be compared!
    future:
        The future for when the request is done
    """

    __slots__: tuple[str, ...] = ("priority", "future")

    def __init__(self, priority: int, future: Future[None]) -> None:
        self.priority: int = priority
        self.future: Future[None] = future

    def __gt__(self, other: PriorityQueueContainer):
        return self.priority > other.priority

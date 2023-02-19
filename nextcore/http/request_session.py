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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final

__all__: Final[tuple[str, ...]] = ("RequestSession",)


class RequestSession:
    """A metadata class about a pending request. This is used by :class:`Bucket`

    Parameters
    ----------
    unlimited:
        If this request was made when the bucket was unlimited.

        This exists to make sure that there is no bad state when switching between unlimited and limited.
    priority:
        The priority of the request (A lower number means it will be executed faster).

    Attributes
    ----------
    unlimited:
        If this request was made when the bucket was unlimited.

        This exists to make sure that there is no bad state when switching between unlimited and limited.
    pending_future:
        The future that would be executed when set.
    priority:
        The priority of the request (A lower number means it will be executed faster).
    """

    __slots__: Final[tuple[str, ...]] = ("pending_future", "priority", "unlimited")

    def __init__(self, *, priority: int = 0, unlimited: bool = False) -> None:
        self.pending_future: Future[None] = Future()
        self.priority: int = priority
        self.unlimited: bool = unlimited

    def __gt__(self, other: RequestSession):
        return self.priority > other.priority

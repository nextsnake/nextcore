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

from asyncio import sleep
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypeVar

    T = TypeVar("T")

logger = getLogger(__name__)


class ExponentialBackoff:
    def __init__(self, initial: float, base: float, max_value: float) -> None:
        self._current_time: float = initial
        self.base: float = base
        self.max: float = max_value

    @property
    def next(self) -> float:
        return self._current_time * self.base

    def __aiter__(self: T) -> T:
        return self

    async def __anext__(self) -> None:
        self._current_time = min(self.max, self.next)
        logger.debug("Sleeping for %s seconds", self._current_time)
        await sleep(self._current_time)

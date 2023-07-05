# The MIT License (MIT)
# Copyright (c) 2021-present tag-epic
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
    from typing import Final

    from typing_extensions import Self


logger = getLogger(__name__)

__all__: Final[tuple[str, ...]] = ("ExponentialBackoff",)


class ExponentialBackoff:
    """A implementation of exponential backoff

    Parameters
    ----------
    initial:
        The initial value of the backoff
    base:
        What to multiply the current time with when the next iteration of backoff is called
    max_value:
        The max value to cap the backoff at

    Attributes
    ----------
    base: :class:`float`
        What to multiply the current time with when the next iteration of backoff is called
    max: :class:`float`
        The max value to cap the backoff at
    """

    __slots__ = ("_current_time", "base", "max", "_initial")

    def __init__(self, initial: float, base: float, max_value: float) -> None:
        self._current_time: float = initial
        self.base: float = base
        self.max: float = max_value
        self._initial: bool = True

    @property
    def next(self) -> float:
        """What the next value of the backoff should be"""
        return self._current_time * self.base

    # TODO: MyPy does not support typing_extensions.Self yet?
    def __aiter__(self) -> Self:  # type: ignore [valid-type]
        return self

    async def __anext__(self) -> None:
        if not self._initial:
            self._current_time = min(self.max, self.next)
            logger.debug("Sleeping for %s seconds", self._current_time)
            await sleep(self._current_time)
        else:
            self._initial = False

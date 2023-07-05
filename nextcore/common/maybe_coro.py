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

from asyncio import iscoroutine
from typing import TYPE_CHECKING, cast, overload

if TYPE_CHECKING:
    from typing import Any, Callable, Coroutine, Final, TypeVar

    from typing_extensions import ParamSpec

    P = ParamSpec("P")
    T = TypeVar("T")

__all__: Final[tuple[str, ...]] = ("maybe_coro",)


@overload
async def maybe_coro(coro: Callable[P, Coroutine[Any, Any, T]], *args: P.args, **kwargs: P.kwargs) -> T:
    ...


@overload
async def maybe_coro(coro: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    ...


async def maybe_coro(coro: Callable[P, T | Coroutine[Any, Any, T]], *args: P.args, **kwargs: P.kwargs) -> T:
    """Execute a sync or async function

    Parameters
    ----------
    coro:
        The function to execute
    args:
        The arguments to pass to the function
    kwargs:
        The keyword arguments to pass to the function

    Returns
    -------
    :data:`typing.Any`
        The result of the function
    """
    result = coro(*args, **kwargs)

    if iscoroutine(result):
        # coro was a async function
        return await result

    # Not a async function, just return the result
    result = cast("T", result)  # The case where this is Coroutine[Any, Any, T] is handled by iscouroutine.
    return result

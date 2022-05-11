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

from asyncio import iscoroutine
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable

__all__ = ("maybe_coro",)


async def maybe_coro(coro: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Execute a sync or async function

    Parameters
    ----------
    coro: Callable[..., :data:`Any`]
        The function to execute
    args: :data:`typing.Any`
        The arguments to pass to the function
    kwargs: :data:`Any`
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
    return result

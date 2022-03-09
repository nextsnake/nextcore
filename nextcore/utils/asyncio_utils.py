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
from inspect import isawaitable

if TYPE_CHECKING:
    from typing import Callable, Any




async def maybe_coro(coro: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Execute a sync or async function

    Parameters
    ----------
    coro: :class:`Callable[..., Any]`
        The function to execute
    args: Any
        The arguments to pass to the function
    kwargs: Any
        The keyword arguments to pass to the function

    Returns
    -------
    Any
        The result of the function
    """
    result = coro(*args, **kwargs)

    if isawaitable(result):
        return await result
    else:
        return result

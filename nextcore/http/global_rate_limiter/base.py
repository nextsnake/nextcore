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

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import AsyncContextManager, Final, TypeVar

    ExceptionT = TypeVar("ExceptionT", bound=BaseException)

__all__: Final[tuple[str, ...]] = ("BaseGlobalRateLimiter",)


class BaseGlobalRateLimiter(ABC):
    """A base implementation of a rate-limiter for global-scoped rate-limits.

    .. warning::
        This does not contain any implementation!

        You are probably looking for :class:`LimitedGlobalRateLimiter` or :class:`UnlimitedGlobalRateLimiter`
    """

    __slots__ = ()

    @abstractmethod
    def acquire(self, *, priority: int = 0, wait: bool = True) -> AsyncContextManager[None]:
        """Use a spot in the rate-limit.

        Parameters
        ----------
        priority:
            .. warning::
                This can safely be ignored.

            The request priority. **Lower** number means it will be requested earlier.
        wait:
            Whether to wait for a spot in the rate limit.

            If this is set to :data:`False`, this will raise a :exc:`RateLimitedError`

        Returns
        -------
        :class:`typing.AsyncContextManager`
            A context manager that will wait in __aenter__ until a request should be made.
        """
        ...

    @abstractmethod
    def update(self, retry_after: float) -> None:
        """Updates the rate-limiter with info from a global scoped 429.

        Parameters
        ----------
        retry_after:
            The time from the `retry_after` field in the JSON response or the `retry_after` header.

            .. hint::
                The JSON field has more precision than the header.
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """Cleanup this instance.

        This should be done when this instance is never going to be used anymore

        .. warning::
            Continued use of this instance may result in instability
        """
        ...

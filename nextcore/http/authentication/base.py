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
    from typing import Final

__all__: Final[tuple[str, ...]] = ("BaseAuthentication",)


class BaseAuthentication(ABC):
    """A wrapper around discord credentials.

    .. warning::
        This is a base class. You should probably use :class:`BotAuthentication` or :class:`BearerAuthentication` instead.

    **Example implementation**

    .. this is relative to the docs directory
    .. literalinclude:: ../nextcore/http/authentication/bot.py
       :language: python3
       :lines: 34-

    Attributes
    ----------
    prefix:
        The prefix of the authentication.
    token:
        The bot's token.
    """

    __slots__ = ("prefix", "token")

    @property
    @abstractmethod
    def rate_limit_key(self) -> str | None:
        """The key used for rate limiting

        This is usually the prefix + token for for example ``Bot AABBCC.DDEEFF.GGHHII``

        **Example usage**

        .. code-block:: python3

            await http_client.request(route, rate_limit_key=authentication.rate_limit_key, ...)
        """
        ...

    @property
    @abstractmethod
    def headers(self) -> dict[str, str]:
        """Headers used for making a authenticated request.

        This may return a empty dict if headers is not used for authenticating this type of authentication.

        **Example usage**

        .. code-block:: python3

            await http_client.request(route, rate_limit_key=authentication.rate_limit_key, headers=authentication.headers, ...)

        """
        ...

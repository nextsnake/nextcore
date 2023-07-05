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

from typing import TYPE_CHECKING

from .base import BaseAuthentication

if TYPE_CHECKING:
    from typing import Final, Literal

__all__: Final[tuple[str, ...]] = ("BotAuthentication",)


class BotAuthentication(BaseAuthentication):
    """A wrapper around bot token authentication.

    **Example usage**

    .. code-block:: python3

        authentication = BotAuthentication(os.environ["TOKEN"])

        route = Route("GET", "/gateway/bot")
        await http_client.request(route, rate_limit_key=authentication.rate_limit_key, headers=authentication.headers)

    Parameters
    ----------
    token:
        The bot token.

    Attributes
    ----------
    prefix:
        The prefix of the token.
    token:
        The bot token
    """

    __slots__: tuple[str, ...] = ()

    def __init__(self, token: str) -> None:
        self.prefix: Literal["Bot"] = "Bot"
        self.token: str = token

    @property
    def rate_limit_key(self) -> str:
        """The key used for rate limiting

        This will be in the format ``Bot AABBCC.DDEEFF.GGHHII``

        **Example usage**

        .. code-block:: python3

            await http_client.request(route, rate_limit_key=authentication.rate_limit_key, headers=authentication.headers, ...)
        """
        return f"{self.prefix} {self.token}"

    @property
    def headers(self) -> dict[str, str]:
        """Headers for doing a authenticated request.

        This will return a dict with a ``Authorization`` field.

        **Example usage**

        .. code-block:: python3

            await http_client.request(route, rate_limit_key=authentication.rate_limit_key, headers=authentication.headers, ...)
        """

        return {"Authorization": f"{self.prefix} {self.token}"}

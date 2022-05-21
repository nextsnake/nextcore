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

from .base import BaseAuthentication

if TYPE_CHECKING:
    from typing import Literal

__all__ = ("BearerAuthentication",)


class BearerAuthentication(BaseAuthentication):
    """A wrapper around OAuth2 Bearer Token authentication.

    Parameters
    ----------
    token: :class:`str`
        The bot token.

    Attributes
    ----------
    prefix: Literal["Bearer"]
        The prefix of the token.
    token: :class:`str`
        The bot token
    """

    __slots__: tuple[str, ...] = ()

    def __init__(self, token: str):
        self.prefix: Literal["Bearer"] = "Bearer"
        self.token: str = token
        self.rate_limit_key: str = f"{self.prefix} {self.token}"

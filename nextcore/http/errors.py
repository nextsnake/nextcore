# The MIT License (MIT)
# Copyright (c) 2021-present nextsnake developers

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp.client_reqrep import ClientResponse


class HTTPError(Exception):
    """Base class for exceptions raised by the nextcore.http module."""

    ...


class RateLimitFailedError(HTTPError):
    """Raised when ratelimiting has failed over max_retries times.

    This can happen if you are running multiple bots on a single bot account.
    If you want to do this you need to subclass :class:`Bucket` and implement syncing between bots.
    """

    def __init__(self, times: int) -> None:
        self.times = times
        """How many times ratelimiting was attempted, but failed."""
        super().__init__(
            "Ratelimiting failed %s times. This should only happen if there is a library issue", self.times
        )


class HTTPRequestError(HTTPError):
    """Raised when a HTTP request got a bad status code.

    Parameters
    ----------
    discord_error_code: :class:`int`
        The discord spesific status code of the error.
    message: :class:`str`
        Error message included in the response.
    response: :class:`aiohttp.ClientResponse`
        Response object from aiohttp.
    """

    def __init__(self, discord_error_code: int, message: str, response: ClientResponse) -> None:
        self.response: ClientResponse = response
        """Response object from aiohttp."""
        self.discord_error_code: int = discord_error_code
        """The discord spesific status code of the error."""
        self.message: str = message
        """Error message included in the response."""

        super().__init__(f"({discord_error_code}) {message}")


class BadRequestError(HTTPRequestError):
    """Raised when a HTTP request got a 400 status code.

    Parameters
    ----------
    discord_error_code: :class:`int`
        The discord spesific status code of the error.
    message: :class:`str`
        Error message included in the response.
    response: :class:`aiohttp.ClientResponse`
        Response object from aiohttp.

    """

    ...


class ForbiddenError(HTTPRequestError):
    """Raised when a HTTP request got a 403 status code.

    Parameters
    ----------
    discord_error_code: :class:`int`
        The discord spesific status code of the error.
    message: :class:`str`
        Error message included in the response.
    response: :class:`aiohttp.ClientResponse`
        Response object from aiohttp.

    """

    ...


class NotFoundError(HTTPRequestError):
    """Raised when a HTTP request got a 404 status code.

    Parameters
    ----------
    discord_error_code: :class:`int`
        The discord spesific status code of the error.
    message: :class:`str`
        Error message included in the response.
    response: :class:`aiohttp.ClientResponse`
        Response object from aiohttp.

    """

    ...

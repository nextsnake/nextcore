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

if TYPE_CHECKING:
    from aiohttp import ClientResponse

    from nextcore.typings.http.error import HTTPError as HTTPErrorTyping


class HTTPError(Exception):
    """A generic error for anything from this module."""

    ...


class UnexpectedError(HTTPError):
    """An error for unexpected errors."""

    ...


class RateLimitingFailedError(UnexpectedError):
    """When ratelimiting has failed more than max_retries times"""

    def __init__(self, max_retries: int, response: ClientResponse) -> None:
        self.max_retries: int = max_retries
        self.response: ClientResponse = response

        super().__init__(f"Ratelimiting failed more than {max_retries} times")


# Expected errors
class HTTPRequestError(HTTPError):
    """A base error for receiving a status code the library doesn't expect."""

    def __init__(self, error: HTTPErrorTyping, response: ClientResponse) -> None:
        self.response: ClientResponse = response

        self.error_code: int = error["code"]
        self.message: str = error["message"]

        super().__init__(f"({self.error_code}) {self.message}")


# TODO: Can the docstrings be improved here?
class BadRequestError(HTTPRequestError):
    """A 400 error."""

    ...


class UnauthorizedError(HTTPRequestError):
    """A 401 error."""

    ...


class ForbiddenError(HTTPRequestError):
    """A 403 error."""

    ...


class NotFoundError(HTTPRequestError):
    """A 404 error."""

    ...


class InternalServerError(HTTPRequestError):
    """A 5xx error."""

    ...
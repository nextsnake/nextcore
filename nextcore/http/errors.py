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

if TYPE_CHECKING:
    from typing import Final

    from aiohttp import ClientResponse
    from discord_typings import HTTPErrorResponseData

__all__: Final[tuple[str, ...]] = (
    "RateLimitingFailedError",
    "HTTPRequestStatusError",
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "InternalServerError",
    "CloudflareBanError",
)


class RateLimitingFailedError(Exception):
    """When rate limiting has failed more than :attr:`HTTPClient.max_retries` times

    .. hint::
        This can be due to a un-syncronized clock.

        You can change :attr:`HTTPClient.trust_local_time` to :data:`False` to disable using your local clock,
        or you could sync your clock.

        .. tab:: Ubuntu

            You can check if your clock is synchronized by running the following command:

            .. code-block:: bash

                timedatectl

            If it is synchronized, it will show "System clock synchronized: yes" and "NTP service: running"

            If the system clock is not synchronized but the ntp service is running you will have to wait a few minutes for it to sync.

            To enable the ntp service run the following command:

            .. code-block:: bash

                sudo timedatectl set-ntp on

            This will automatically sync the system clock every once in a while.

        .. tab:: Arch

            You can check if your clock is synchronized by running the following command:

            .. code-block:: bash

                timedatectl

            If it is synchronized, it will show "System clock synchronized: yes" and "NTP service: running"

            If the system clock is not synchronized but the ntp service is running you will have to wait a few minutes for it to sync.

            To enable the ntp service run the following command:

            .. code-block:: bash

                sudo timedatectl set-ntp on

            This will automatically sync the system clock every once in a while.

        .. tab:: Windows

            This can be turned on by going to ``Settings -> Time & language -> Date & time`` and turning on ``Set time automatically``.




    Parameters
    ----------
    max_retries:
        How many retries the request used that failed.
    response:
        The response to the last request that failed.

    Attributes
    ----------
    max_retries:
        How many retries the request used that failed.
    response:
        The response to the last request that failed.
    """

    def __init__(self, max_retries: int, response: ClientResponse) -> None:
        self.max_retries: int = max_retries
        self.response: ClientResponse = response

        super().__init__(f"Ratelimiting failed more than {max_retries} times")


# Expected errors
class HTTPRequestStatusError(Exception):
    """A base error for receiving a status code the library doesn't expect.

    Parameters
    ----------
    error:
        The error json from the body.
    response:
        The response to the request.

    Attributes
    ----------
    response:
        The response to the request.
    error_code:
        The error code.
    message:
        The error message.
    error:
        The error json from the body.
    """

    def __init__(self, error: HTTPErrorResponseData, response: ClientResponse) -> None:
        self.response: ClientResponse = response

        self.error_code: int = error["code"]
        self.message: str = error["message"]

        self.error: HTTPErrorResponseData = error

        super().__init__(f"({self.error_code}) {self.message}")


# TODO: Can the docstrings be improved here?
class BadRequestError(HTTPRequestStatusError):
    """A 400 error."""


class UnauthorizedError(HTTPRequestStatusError):
    """A 401 error."""


class ForbiddenError(HTTPRequestStatusError):
    """A 403 error."""


class NotFoundError(HTTPRequestStatusError):
    """A 404 error."""


class InternalServerError(HTTPRequestStatusError):
    """A 5xx error."""


class CloudflareBanError(Exception):
    """A error for when you get banned by cloudflare

    This happens due to getting too many ``401``, ``403`` or ``429`` responses from discord.
    This will block your access to the API temporarily for an hour.

    See the `documentation <https://discord.dev/topics/rate-limits#invalid-request-limit-aka-cloudflare-bans>`__ for more info.
    """

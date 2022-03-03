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

from collections import defaultdict
from logging import getLogger
from time import time
from typing import TYPE_CHECKING

from aiohttp import ClientSession

from nextcore import __version__ as nextcore_version

from .bucket import Bucket
from .errors import (
    BadRequestError,
    ForbiddenError,
    HTTPRequestError,
    NotFoundError,
    RateLimitFailedError,
)
from .reverse_event import ReversedTimedEvent
from .route import Route

if TYPE_CHECKING:
    from typing import Any, Optional, Type

    from aiohttp import ClientResponse, ClientWebSocketResponse

    from ..typings.http import GetGateway, GetGatewayBot

logger = getLogger(__name__)

__all__ = ("HTTPClient",)


class HTTPClient:
    """A HTTP client to interact with the Discord API.
    This handles ratelimits for you.

    Parameters
    ----------
    token_type: Optional[str]
        The type of token to use. This will be prepended to the token.
    token: Optional[str]
        The token to use.
    base_url: Optional[str]
        The discord API url to use. This should generally be left as the default, unless you are running a compatible server.
    trust_local_time: bool
        Whether to trust the local time or not. Having it on will make your bot faster, however if your local time is wrong it might lead to ratelimits being exceeded.
    library_info: Optional[tuple[str, str]]
        The library information to pass to Discord for analytics. First element is a URL, second is the version.
    """

    __slots__ = (
        "trust_local_time",
        "max_retries",
        "base_url",
        "_global_webhook_lock",
        "_global_lock",
        "_buckets",
        "_session",
        "_status_to_exception",
        "default_headers",
    )

    def __init__(
        self,
        token_type: Optional[str] = None,
        token: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        trust_local_time: bool = True,
        max_retries: int = 5,
        library_info: Optional[tuple[str, str]] = None,
    ) -> None:
        self.trust_local_time: bool = trust_local_time
        self.max_retries: int = max_retries
        self.base_url: str = base_url or "https://discord.com/api/v9"

        # Internals
        self._global_webhook_lock = ReversedTimedEvent()
        self._global_lock = ReversedTimedEvent()
        self._buckets: defaultdict[int, Bucket] = defaultdict(Bucket)
        self._session = ClientSession()
        self._status_to_exception: dict[int, Type[HTTPRequestError]] = {
            400: BadRequestError,
            403: ForbiddenError,
            404: NotFoundError,
        }

        # User agent
        if library_info is not None:
            user_agent = f"DiscordBot ({library_info[0]}, {library_info[1]}) nextcore/{nextcore_version}"
        else:
            user_agent = f"DiscordBot (https://github.com/nextsnake/nextcore, {nextcore_version})"

        self.default_headers: dict[str, str] = {"User-Agent": user_agent}

        # Token
        if token_type is not None and token is not None:
            self.default_headers["Authorization"] = f"{token_type} {token}"

    async def _request(self, route: Route, **kwargs: Any) -> ClientResponse:
        """Makes a request to the Discord API.

        Parameters
        ----------
        route: Route
            Metadata about the route and ratelimits.
        kwargs:
            Arguments to pass to `ClientSession.request <https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession.trace_config>`_

        Returns
        -------
        ClientResponse
            The response from the API.
        """
        if route.use_webhook_global:
            global_lock = self._global_webhook_lock
        else:
            global_lock = self._global_lock

        bucket = self._buckets[route.bucket]

        headers = kwargs.pop("headers", {})
        headers = {**self.default_headers, **headers}

        for _ in range(self.max_retries):
            await global_lock.wait()
            async with bucket:
                logger.debug("%s: %s", route.method, route.path)
                r = await self._session.request(route.method, self.base_url + route.path, headers=headers, **kwargs)

                self._update_ratelimits(r, bucket)

                # Handle http errors
                if r.status >= 300:
                    # Some sort of error
                    if r.status == 429:
                        # Ratelimit
                        if "X-RateLimit-Global" in r.headers.keys():
                            # Global ratelimit
                            data = await r.json()
                            global_lock.set(data["retry_after"])
                            logger.info("Global ratelimit exceeded")
                            continue
                        else:
                            # Per route ratelimit
                            logger.warning(
                                "Ratelimit exceeded on bucket %s. This should only happen if you are clustering which is not supported."
                            )
                            continue
                    else:
                        await self._handle_http_exception(r)
                        assert False, "Reached post handle http exception"
                return r
        # Generally only happens when running multiple bots on the same bot account.
        raise RateLimitFailedError(self.max_retries)

    async def ws_connect(self, url: str) -> ClientWebSocketResponse:
        """Connects to a websocket.

        Parameters
        ----------
        url: :class:`str`
            The url to connect to.

        Returns
        -------
        :class:`ClientWebSocketResponse`
            The websocket response.
        """
        return await self._session.ws_connect(url, autoclose=False)

    async def _handle_http_exception(self, response: ClientResponse) -> None:
        """Handles an HTTP error.

        Parameters
        ----------
        response: ClientResponse
            The response from the API to process the errors for.
        """
        # TODO: Not sure if this should be a seperate method or not
        error = self._status_to_exception.get(response.status, HTTPRequestError)

        data = await response.json()
        message = data["message"]
        code = data["code"]

        raise error(code, message, response)

    def _update_ratelimits(self, response: ClientResponse, bucket: Bucket) -> None:
        """Updates a :class:`Bucket` with the ratelimits from the response.

        Parameters
        ----------
        response: ClientResponse
            The response from the API.
        bucket: Bucket
            The bucket to update.
        """
        headers = response.headers
        try:
            remaining = int(headers["X-RateLimit-Remaining"])
            limit = int(headers["X-RateLimit-Limit"])
            reset_after = float(headers["X-RateLimit-Reset-After"])
            reset_at = float(headers["X-RateLimit-Reset"])
        except KeyError:
            return

        if self.trust_local_time:
            reset_after = reset_at - time()

        bucket.update(limit, remaining, reset_after)
        logger.debug("Ratelimiter updated by headers!")

    # Util functions
    # Gateway related
    async def get_gateway(self) -> GetGateway:
        """Gets the gateway URL to connect to discord.
        See the `documentation <https://discord.dev/topics/gateway#gateway-get-gateway>`_

        .. note::
            This endpoint does not require any authentication.
        """
        route = Route("GET", "/gateway", requires_auth=False)
        r = await self._request(route)
        return await r.json()  # type: ignore

    async def get_gateway_bot(self) -> GetGatewayBot:
        """Gets gateway connection information.
        See the `documentation <https://discord.dev/topics/gateway#gateway-get-gateway-bot>`_

        .. note::
            This endpoint requires a bot token.
        """
        route = Route("GET", "/gateway/bot")
        r = await self._request(route)
        return await r.json()  # type: ignore

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
    from typing import Any, Type

    from aiohttp import ClientResponse, ClientWebSocketResponse

    from ..typings.http import GetGateway, GetGatewayBot

logger = getLogger(__name__)

__all__ = ("HTTPClient",)


class HTTPClient:
    """A HTTP client to interact with the Discord API.
    This handles ratelimits for you.

    Parameters
    ----------
    token_type: str | None
        The type of token to use. This will be prepended to the token.
    token: str | None
        The token to use.
    base_url: str | None
        The discord API url to use. This should generally be left as the default, unless you are running a compatible server.
    trust_local_time: bool
        Whether to trust the local time or not. Having it on will make your bot faster, however if your local time is wrong it might lead to ratelimits being exceeded.
    library_info: Optional[tuple[str, str]]
        The library information to pass to Discord for analytics. First element is a URL, second is the version.
    """

    __slots__ = (
        "trust_local_time",
        "max_retries",
        "_global_webhook_lock",
        "_global_lock",
        "_buckets",
        "_discord_bucket_to_bucket",
        "_session",
        "_status_to_exception",
        "default_headers",
    )

    def __init__(
        self,
        token_type: str | None = None,
        token: str | None = None,
        *,
        trust_local_time: bool = True,
        max_retries: int = 5,
        library_info: tuple[str, str] | None = None,
    ) -> None:
        self.trust_local_time: bool = trust_local_time
        self.max_retries: int = max_retries

        # Internals
        self._global_lock = ReversedTimedEvent()
        self._buckets: defaultdict[int, Bucket] = defaultdict(Bucket)
        self._discord_bucket_to_bucket: dict[str, Bucket] = {}
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
        bucket = self._buckets[route.bucket]

        headers = kwargs.pop("headers", {})
        headers = {**self.default_headers, **headers}

        for _ in range(self.max_retries):
            async with bucket:
                if not route.ignore_global:
                    # Some routes are not affected by the global ratelimit.
                    # WARNING: This sucks!
                    # There is a issue where more requests are fired before we get this info. This can't be fixed until
                    # discord adds a way for us to get the global limit.
                    await self._global_lock.wait()

                logger.debug("%s: %s", route.method, route.path)
                r = await self._session.request(route.method, route.BASE_URL + route.path, headers=headers, **kwargs)

                self._update_ratelimits(r, route, bucket)

                # Handle http errors
                if r.status >= 300:
                    # Some sort of error
                    if r.status == 429:
                        # Ratelimit
                        if "X-RateLimit-Global" in r.headers.keys():
                            # Global ratelimit
                            data = await r.json()
                            self._global_lock.set(data["retry_after"])
                            logger.info("Global ratelimit exceeded. Retrying in %ss.", data["retry_after"])
                            continue
                        else:
                            # Per route ratelimit
                            logger.warning(
                                "Ratelimit exceeded on bucket %s. Bucket expires in ~%ss",
                                route.bucket,
                                r.headers["X-RateLimit-Reset-After"],
                            )
                            continue
                    else:
                        # This should always error, if not we have a serious issue
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
        error = self._status_to_exception.get(response.status, HTTPRequestError)

        data = await response.json()
        message = data["message"]
        code = data["code"]

        raise error(code, message, response)

    def _update_ratelimits(self, response: ClientResponse, route: Route, bucket: Bucket) -> None:
        """Updates a :class:`Bucket` with the ratelimits from the response.

        Parameters
        ----------
        response: ClientResponse
            The response from the API.
        route: Route
            The route to update the ratelimits for.
        bucket: Bucket
            The bucket to update.
        """
        headers = response.headers
        try:
            remaining = int(headers["X-RateLimit-Remaining"])
            limit = int(headers["X-RateLimit-Limit"])
            reset_after = float(headers["X-RateLimit-Reset-After"])
            reset_at = float(headers["X-RateLimit-Reset"])
            bucket_hash = headers["X-RateLimit-Bucket"]
        except KeyError:
            # Some endpoints don't have ratelimits, some error responses don't show ratelimits.
            if response.status < 300 and not bucket.unlimited:
                logger.debug("Bucket %s is now unlimited", repr(bucket))
            return

        if self.trust_local_time:
            reset_after = reset_at - time()

        bucket.update(limit, remaining, reset_after)

        # Scoped bucket linking.
        if bucket_hash in self._discord_bucket_to_bucket.keys():
            if (correct_bucket := self._discord_bucket_to_bucket[bucket_hash]) != bucket:
                logger.debug("Linking bucket %s to bucket %s", bucket_hash, route.bucket)
                self._buckets[route.bucket] = correct_bucket
        else:
            logger.debug("Setting discord bucket mapping for bucket %s", bucket_hash)
            self._discord_bucket_to_bucket[bucket_hash] = bucket

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

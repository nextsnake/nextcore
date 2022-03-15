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

from logging import getLogger
from time import time
from typing import TYPE_CHECKING

from aiohttp import ClientSession
from asyncio import get_running_loop

from .bucket import Bucket
from .bucket_metadata import BucketMetadata
from .global_lock import GlobalLock
from .route import Route

if TYPE_CHECKING:
    from typing import Any, ClassVar, Final

    from aiohttp import ClientResponse, ClientWebSocketResponse
    from ..typings.http.get_gateway_bot import GetGatewayBot

logger = getLogger(__name__)


class HTTPClient:
    """The HTTP client to interface with the Discord API.

    Parameters
    ----------
    trust_local_time: :class:`bool`
        Whether to trust local time.
        If this is not set HTTP ratelimiting will be a bit slower but may be a bit more accurate on systems where the local time is off.
    timeout: :class:`float`
        The default request timeout in seconds.
    max_ratelimit_retries: :class:`int`
        How many times to attempt to retry a request after ratelimiting failed.
    global_ratelimit: :class:`int`
        The global ratelimit your bot has.
        Unless you have contacted support about a raise, this will always be 50.
        Leaving this as None will cause the ratelimiter to allow until a failure which is not ideal.
    """
    API_BASE: ClassVar[str] = "https://discord.com/api/v10"
    """The API base URL. This is what changes the API version or if the canary API is used."""

    def __init__(self, *, trust_local_time: bool = True, timeout: float = 60, max_ratelimit_retries: int = 10, global_ratelimit: int | None = None):
        self.trust_local_time: bool = trust_local_time
        """Whether to trust local time."""
        self.timeout: float = timeout
        """The default request timeout in seconds."""
        self.default_headers: Final[dict[str, str]] = {
            "User-Agent": f"DiscordBot (https://github.com/nextsnake/nextcore)"
        }
        """Headers attached by default to every request."""
        self.max_retries: int = max_ratelimit_retries
        """How many times to attempt to retry a request."""

        # Internals
        # Buckets
        self._buckets: dict[str | int, Bucket] = {}  # Route.bucket -> Bucket
        self._discord_buckets: dict[str, Bucket] = {}  # X-RateLimit-Bucket -> Bucket
        self._bucket_metadata: dict[str, BucketMetadata] = {}  # Route.route -> BucketMetadata

        self._global_lock: GlobalLock = GlobalLock(global_ratelimit)
        self._session: ClientSession | None = None

    async def _request(self, route: Route, *, headers: dict[str, str] | None = None, **kwargs: Any) -> ClientResponse:
        """Requests a route from the Discord API

        Parameters
        ----------
        route: :class:`Route`
            The route to request
        headers: :class:`dict[str, str]`
            Headers to mix with :attr:`HTTPClient.default_headers` to pass to :meth:`aiohttp.ClientSession.request`
        kwargs: :data:`typing.Any`
            Keyword arguments to pass to :meth:`aiohttp.ClientSession.request`

        Returns
        -------
        :class:`ClientResponse`
            The response from the request.
        """
        # Make a ClientSession if we don't have one
        await self._ensure_session()
        assert self._session is not None, "Session was not set after HTTPClient._ensure_session()"

        # Ensure headers exists
        if headers is None:
            headers = {}

        # Merge default headers with user provided ones
        headers = {**self.default_headers, **headers}

        for _ in range(self.max_retries):
            bucket = await self._get_bucket(route)
            async with bucket.acquire():
                if not route.ignore_global:
                    async with self._global_lock:
                        logger.info("Requesting %s %s", route.method, route.path)
                        response = await self._session.request(
                            route.method, route.BASE_URL + route.path, headers=headers, timeout=self.timeout, **kwargs
                        )
                else:
                    logger.info("Requesting %s %s (non-global)", route.method, route.path)
                    response = await self._session.request(
                        route.method, route.BASE_URL + route.path, headers=headers, timeout=self.timeout, **kwargs
                    )

                await self._update_bucket(response, route, bucket)

                # Handle ratelimit errors
                if response.status == 429:
                    scope = response.headers["X-RateLimit-Scope"]
                    if scope == "global":
                        # Global ratelimit handling
                        # We use retry_after from the body instead of the headers as they have more precision than the headers.
                        data = await response.json()
                        retry_after = data["retry_after"]

                        logger.info("Global ratelimit hit. Retrying in %s seconds", retry_after)

                        self._global_lock.lock()

                        loop = get_running_loop()
                        # Unlock it
                        logger.debug("Unlocking global!")
                        loop.call_later(retry_after, self._global_lock.unlock)

                        continue
                    elif scope == "user":
                        # Failure in Bucket or clustering?
                        logger.warning(
                            "Ratelimit exceeded on bucket %s. This should not happen unless you are running multiple bots on the same token.",
                            route.bucket,
                        )
                    elif scope == "resource":
                        # Can't really be avoided. Shit happens.
                        logger.info("Ratelimit exceeded on bucket %s.", route.bucket)
                    else:
                        # Well shit... Lets try again and hope for the best.
                        logger.warning("Unknown ratelimit scope %s received. Maybe try updating?", scope)
                elif response.status >= 300:
                    raise NotImplementedError("Error handling")
                else:
                    # Should be in 0-200 range
                    return response

        raise RateLimitFailedError(self.max_retries)

    async def ws_connect(self, url: str, **kwargs: Any) -> ClientWebSocketResponse:
        """Connects to a websocket.

        Parameters
        ----------
        url: :class:`str`
            The url to connect to.
        kwargs: :data:`typing.Any`
            Keyword arguments to pass to :meth:`aiohttp.ClientSession.ws_connect`

        Returns
        -------
        :class:`aiohttp.ClientWebSocketResponse`
            The websocket response.
        """
        await self._ensure_session()
        assert self._session is not None, "Session was not set after HTTPClient._ensure_session()"
        return await self._session.ws_connect(url, autoclose=False, **kwargs)

    async def _ensure_session(self) -> None:
        """Makes sure :attr:`HTTPClient._session` is set.

        This is made due to
        """
        if self._session is None:
            self._session = ClientSession()

    async def _get_bucket(self, route: Route) -> Bucket:
        """Gets a bucket object for a route.

        Strategy:
        - Get by calculated id (:attr:`Route.bucket`)
        - Create new based on :class:`BucketMetadata` found through the route (:attr:`Route.route`)
        - Create a new bucket with no info

        Parameters
        ----------
        route: :class:`Route`
            The route to get the bucket for.
        """
        if (bucket := self._buckets.get(route.bucket)) is not None:
            # Bucket already exists
            return bucket
        elif (metadata := self._bucket_metadata.get(route.route)) is not None:
            # Create a new bucket with info from the metadata
            bucket = Bucket(metadata)
            self._buckets[route.bucket] = bucket
            return bucket
        else:
            # Create a new bucket with no info
            # Create metadata
            metadata = BucketMetadata()
            self._bucket_metadata[route.route] = metadata

            # Create the bucket
            bucket = Bucket(metadata)
            self._buckets[route.bucket] = bucket

            return bucket

    async def _update_bucket(self, response: ClientResponse, route: Route, bucket: Bucket) -> None:
        """Updates the bucket and metadata from the info received from the API."""
        headers = response.headers
        try:
            remaining = int(headers["X-RateLimit-Remaining"])
            limit = int(headers["X-RateLimit-Limit"])
            reset_after = float(headers["X-RateLimit-Reset-After"])
            reset_at = float(headers["X-RateLimit-Reset"])
            bucket_hash = headers["X-RateLimit-Bucket"]
        except KeyError:
            # No ratelimit headers
            if response.status < 300:
                # No ratelimit headers and no error, this is likely a route with no ratelimits.
                bucket.metadata.unlimited = True
                await bucket.update(unlimited=True)
            return
        # Convert reset_at to reset_after
        if self.trust_local_time:
            reset_after = reset_at - time()

        # Update bucket
        await bucket.update(remaining, reset_after, unlimited=False)

        # Update metadata
        bucket.metadata.limit = limit
        bucket.metadata.unlimited = False

        # Auto-link buckets based on bucket_hash
        if (linked_bucket := self._discord_buckets.get(bucket_hash)) is not None:
            self._buckets[route.bucket] = linked_bucket
        self._discord_buckets[bucket_hash] = bucket

    # Wrapper functions for requests
        # Wrapper functions
    async def get_gateway_bot(self) -> GetGatewayBot:
        """Gets gateway connection information.
        See the `documentation <https://discord.dev/topics/gateway#gateway-get-gateway-bot>`_

        .. note::
            This endpoint requires a bot token.
        """
        route = Route("GET", "/gateway/bot")
        r = await self._request(route)
        return await r.json()  # type: ignore

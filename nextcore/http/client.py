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

from asyncio import get_running_loop
from logging import getLogger
from time import time
from typing import TYPE_CHECKING

from aiohttp import ClientSession

from .. import __version__ as nextcore_version
from .bucket import Bucket
from .bucket_metadata import BucketMetadata
from .errors import (
    BadRequestError,
    ForbiddenError,
    HTTPRequestError,
    InternalServerError,
    NotFoundError,
    RateLimitingFailedError,
    UnauthorizedError,
)
from .ratelimit_storage import RatelimitStorage
from .route import Route

if TYPE_CHECKING:
    from typing import Any, Final

    from aiohttp import ClientResponse, ClientWebSocketResponse

    from ..typings.http import GetGatewayBot

logger = getLogger(__name__)

__all__ = ("HTTPClient",)


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

    __slots__ = (
        "trust_local_time",
        "timeout",
        "default_headers",
        "max_retries",
        "ratelimit_storages",
        "_buckets",
        "_discord_buckets",
        "_bucket_metadata",
        "_session",
    )

    def __init__(
        self,
        *,
        trust_local_time: bool = True,
        timeout: float = 60,
        max_ratelimit_retries: int = 10,
    ):
        self.trust_local_time: bool = trust_local_time
        self.timeout: float = timeout
        self.default_headers: Final[dict[str, str]] = {
            "User-Agent": f"DiscordBot (https://github.com/nextsnake/nextcore, {nextcore_version})"
        }
        self.max_retries: int = max_ratelimit_retries
        self.ratelimit_storages: dict[int, RatelimitStorage] = {}  # User ID -> RatelimitStorage

        # Internals
        self._session: ClientSession | None = None

    async def _request(
        self, route: Route, ratelimit_key: int, *, headers: dict[str, str] | None = None, **kwargs: Any
    ) -> ClientResponse:
        """Requests a route from the Discord API

        Parameters
        ----------
        route: :class:`Route`
            The route to request
        ratelimit_key: :class:`int`
            A ID used for differentiating ratelimits. This should be used when
            A user/bot ID to use for ratelimiting.
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

        # Get the per user ratelimit storage
        ratelimit_storage = self.ratelimit_storages.get(ratelimit_key)
        if ratelimit_storage is None:
            # None exists, create one
            ratelimit_storage = RatelimitStorage()
            self.ratelimit_storages[ratelimit_key] = ratelimit_storage

        # Ensure headers exists
        if headers is None:
            headers = {}

        # Merge default headers with user provided ones
        headers = {**self.default_headers, **headers}

        retries = max(self.max_retries + 1, 1)

        for _ in range(retries):
            bucket = await self._get_bucket(route, ratelimit_storage)
            async with bucket.acquire():
                if not route.ignore_global:
                    async with ratelimit_storage.global_lock:
                        logger.info("Requesting %s %s", route.method, route.path)
                        response = await self._session.request(
                            route.method, route.BASE_URL + route.path, headers=headers, timeout=self.timeout, **kwargs
                        )
                else:
                    # Interactions are immune to global ratelimits, ignore them here.
                    logger.info("Requesting (NO-GLOBAL) %s %s", route.method, route.path)
                    response = await self._session.request(
                        route.method, route.BASE_URL + route.path, headers=headers, timeout=self.timeout, **kwargs
                    )
                await self._update_bucket(response, route, bucket, ratelimit_storage)

                logger.debug("Response status: %s", response.status)

                # Handle ratelimit errors
                if response.status == 429:
                    scope = response.headers["X-RateLimit-Scope"]
                    if scope == "global":
                        # Global ratelimit handling
                        # We use retry_after from the body instead of the headers as they have more precision than the headers.
                        data = await response.json()
                        retry_after = data["retry_after"]

                        if ratelimit_storage.global_lock.limit is None:
                            # User decided that they don't want to set a static global ratelimit (hopefully using large bot sharding, if not shame on you)
                            logger.info(
                                "Global ratelimit hit, but no static was set. Blame the user and move on. Retrying in %s seconds.",
                                retry_after,
                            )
                        else:
                            logger.warning(
                                "Global ratelimit hit! This should usually not happen... Discord says to retry in %s, global: %s",
                                retry_after,
                                ratelimit_storage.global_lock,
                            )

                        # Lock the global lock temporarily
                        if ratelimit_storage.global_lock.limit is None:
                            loop = get_running_loop()
                            ratelimit_storage.global_lock.lock()
                            loop.call_later(retry_after, ratelimit_storage.global_lock.unlock)
                    elif scope == "user":
                        # Failure in Bucket or clustering?
                        logger.warning(
                            "Ratelimit exceeded on bucket %s! Retry after: %s. Bucket state: %s",
                            route.bucket,
                            response.headers["X-RateLimit-Retry-After"],
                            bucket,
                        )
                    elif scope == "shared":
                        # Resource is shared between multiple users.
                        # This can't be avoided however it doesnt count towards your ban limit so nothing to do here.

                        logger.info("Ratelimit exceeded on bucket %s.", route.bucket)
                    else:
                        # Well shit... Lets try again and hope for the best.
                        logger.warning("Unknown ratelimit scope %s received. Maybe try updating?", scope)
                elif response.status >= 300:
                    error = await response.json()
                    if response.status == 400:
                        raise BadRequestError(error, response)
                    elif response.status == 401:
                        raise UnauthorizedError(error, response)
                    elif response.status == 403:
                        raise ForbiddenError(error, response)
                    elif response.status == 404:
                        raise NotFoundError(error, response)
                    elif response.status >= 500:
                        raise InternalServerError(error, response)
                    else:
                        raise HTTPRequestError(error, response)
                else:
                    # Should be in 0-200 range
                    return response
        # This should always be set as it has to pass through the loop atleast once.
        raise RateLimitingFailedError(self.max_retries, response)  # type: ignore [reportUnboundVariable]

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

        This is made due to :class:`aiohttp.ClientSession` requring to being created in a async context.
        """
        # Maybe merge this into _request?
        if self._session is None:
            self._session = ClientSession()

    async def _get_bucket(self, route: Route, ratelimit_storage: RatelimitStorage) -> Bucket:
        """Gets a bucket object for a route.

        Strategy:
        - Get by calculated id (:attr:`Route.bucket`)
        - Create new based on :class:`BucketMetadata` found through the route (:attr:`Route.route`)
        - Create a new bucket with no info

        Parameters
        ----------
        route: :class:`Route`
            The route to get the bucket for.
        ratelimit_storage: :class:`RatelimitStorage`
            The user's ratelimits.
        """
        # TODO: Can this be written better?
        bucket = await ratelimit_storage.get_bucket_by_nextcore_id(route.bucket)
        if bucket is not None:
            # Bucket already exists
            return bucket

        metadata = await ratelimit_storage.get_bucket_metadata(route.route)

        if metadata is not None:
            # Create a new bucket with info from the metadata
            bucket = Bucket(metadata)
            await ratelimit_storage.store_bucket_by_nextcore_id(route.bucket, bucket)
            return bucket

        # Create a new bucket with no info
        # Create metadata
        metadata = BucketMetadata()
        await ratelimit_storage.store_metadata(route.route, metadata)

        # Create the bucket
        bucket = Bucket(metadata)
        await ratelimit_storage.store_bucket_by_nextcore_id(route.bucket, bucket)

        return bucket

    async def _update_bucket(
        self, response: ClientResponse, route: Route, bucket: Bucket, ratelimit_storage: RatelimitStorage
    ) -> None:
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
        # TODO: This isnt very extensible. Maybe make a async .update function?
        bucket.metadata.limit = limit
        bucket.metadata.unlimited = False

        # Auto-link buckets based on bucket_hash
        linked_bucket = await ratelimit_storage.get_bucket_by_discord_id(bucket_hash)
        if linked_bucket is not None:
            # TODO: Migrate pending requests to the linked bucket
            await ratelimit_storage.store_bucket_by_nextcore_id(route.bucket, linked_bucket)
        else:
            # Automatically linking them
            await ratelimit_storage.store_bucket_by_discord_id(bucket_hash, bucket)

    # Wrapper functions for requests
    # Wrapper functions
    async def get_gateway_bot(self) -> GetGatewayBot:
        """Gets gateway connection information.
        See the `documentation <https://discord.dev/topics/gateway#gateway-get-gateway-bot>`_

        .. note::
            This endpoint requires a bot token.
        """
        route = Route("GET", "/gateway/bot")
        # No ratelimit key needed as its unauthenticated. This will use up a bit of memory... oops
        # TODO: Make this clearer via None?
        r = await self._request(route, ratelimit_key=-1)
        return await r.json()  # type: ignore

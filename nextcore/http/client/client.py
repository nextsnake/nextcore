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

from collections import defaultdict
from logging import getLogger
from time import time
from typing import TYPE_CHECKING

from aiohttp import ClientSession

from ... import __version__ as nextcore_version
from ...common import UNDEFINED, Dispatcher, UndefinedType
from ..bucket import Bucket
from ..bucket_metadata import BucketMetadata
from ..errors import (
    BadRequestError,
    CloudflareBanError,
    ForbiddenError,
    HTTPRequestStatusError,
    InternalServerError,
    NotFoundError,
    RateLimitingFailedError,
    UnauthorizedError,
)
from ..rate_limit_storage import RateLimitStorage
from ..route import Route
from .base_client import BaseHTTPClient

if TYPE_CHECKING:
    from typing import Any, Final, Literal

    from aiohttp import ClientResponse, ClientWebSocketResponse

logger = getLogger(__name__)

__all__: Final[tuple[str, ...]] = ("HTTPClient",)


class HTTPClient(BaseHTTPClient):
    """The HTTP client to interface with the Discord API.

    **Example usage**


    .. literalinclude:: ../examples/http/get_gateway/get_gateway.py
       :lines: 30-42
       :language: python
       :dedent: 4

    Parameters
    ----------
    trust_local_time:
        Whether to trust local time.
        If this is not set HTTP rate limiting will be a bit slower but may be a bit more accurate on systems where the local time is off.
    timeout:
        The default request timeout in seconds.
    max_rate_limit_retries:
        How many times to attempt to retry a request after rate limiting failed.

    Attributes
    ----------
    trust_local_time:
        If this is enabled, the rate limiter will use the local time instead of the discord provided time. This may improve your bot's speed slightly.

        .. warning::
            If your time is not correct, and this is set to :data:`True`, this may result in more rate limits being hit.

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
    timeout:
        The default request timeout in seconds.
    default_headers:
        The default headers to pass to every request.
    max_retries:
        How many times to attempt to retry a request after rate limiting failed.

        .. note::
            This does not retry server errors.
    rate_limit_storages:
        Classes to store rate limit information.

        The key here is the rate_limit_key (often a user ID).
    dispatcher:
        Events from the HTTPClient. See the :ref:`events<HTTPClient dispatcher>`
    """

    __slots__ = (
        "trust_local_time",
        "timeout",
        "default_headers",
        "max_retries",
        "rate_limit_storages",
        "dispatcher",
        "_session",
    )

    def __init__(
        self,
        *,
        trust_local_time: bool = True,
        timeout: float = 60,
        max_rate_limit_retries: int = 10,
    ) -> None:
        self.trust_local_time: bool = trust_local_time
        self.timeout: float = timeout
        self.default_headers: dict[str, str] = {
            "User-Agent": f"DiscordBot (https://github.com/nextsnake/nextcore, {nextcore_version})"
        }
        self.max_retries: int = max_rate_limit_retries
        self.rate_limit_storages: defaultdict[str | None, RateLimitStorage] = defaultdict(
            RateLimitStorage
        )  # User ID -> RateLimitStorage
        self.dispatcher: Dispatcher[Literal["request_response"]] = Dispatcher()

        # Internals
        self._session: ClientSession | None = None

    async def setup(self) -> None:
        """Sets up the HTTP session

        .. warning::
            This has to be called before :meth:`HTTPClient._request` or :meth:`HTTPClient.connect_to_gateway`

        Raises
        ------
        RuntimeError
            This can only be called once
        """
        if self._session is not None:
            raise RuntimeError("This method can only be called once!")
        self._session = ClientSession()

    async def close(self) -> None:
        """Clean up internal state"""
        for rate_limit_storage in self.rate_limit_storages.values():
            await rate_limit_storage.close()
        self.rate_limit_storages.clear()

        self.dispatcher.close()

        if self._session is not None:
            await self._session.close()

    async def request(
        self,
        route: Route,
        rate_limit_key: str | None,
        *,
        headers: dict[str, str] | None = None,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
        **kwargs: Any,
    ) -> ClientResponse:
        """Requests a route from the Discord API

        Parameters
        ----------
        route:
            The route to request
        rate_limit_key:
            A ID used for differentiating rate limits.
            This should be a bot or oauth2 token.

            .. note::
                This should be :data:`None` for unauthenticated routes or webhooks (does not include modifying the webhook via a bot).
        headers:
            Headers to mix with :attr:`HTTPClient.default_headers` to pass to :meth:`aiohttp.ClientSession.request`
        bucket_priority:
            The request priority to pass to :class:`Bucket`. **Lower** priority will be picked first.
        global_priority:
            The request priority for global requests. **Lower** priority will be picked first.

            .. warning::
                This may be ignored by your :class:`BaseGlobalRateLimiter`.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.
        kwargs:
            Keyword arguments to pass to :meth:`aiohttp.ClientSession.request`

        Returns
        -------
        ClientResponse
            The response from the request.

        Raises
        ------
        RuntimeError
            :meth:`HTTPClient.setup` was not called yet.
        RuntimeError
            HTTPClient was closed.
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        CloudflareBanError
            You have been temporarily banned from the Discord API for 1 hour due to too many requests.
            Read the `documentation <https://discord.dev/opics/rate-limits#invalid-request-limit-aka-cloudflare-bans>`__ for more information.
        BadRequestError
            The request data was invalid.
        UnauthorizedError
            No token was provided on a endpoint that requires a token.
        ForbiddenError
            The token was valid but you do not have permission to use do this.
        NotFoundError
            The endpoint you requested was not found or a route parameter was invalid.
        InternalServerError
            Discord is having issues. Try again later.
        HTTPRequestStatusError
            A non-200 status code was returned.
        """
        # Make sure we have a session
        if self._session is None:
            raise RuntimeError("HTTPClient.setup has to be called before request")
        if self._session.closed:
            raise RuntimeError("HTTPClient is closed")

        # Get the per user rate limit storage
        rate_limit_storage = self.rate_limit_storages[rate_limit_key]

        # Ensure headers exists
        if headers is None:
            headers = {}

        # Merge default headers with user provided ones
        headers = {**self.default_headers, **headers}

        retries = max(self.max_retries + 1, 1)

        for _ in range(retries):
            bucket = await self._get_bucket(route, rate_limit_storage)
            async with bucket.acquire(priority=bucket_priority, wait=wait):
                if not route.ignore_global:
                    async with rate_limit_storage.global_rate_limiter.acquire(priority=global_priority, wait=wait):
                        logger.info("Requesting %s %s", route.method, route.path)
                        response = await self._session.request(
                            route.method, route.BASE_URL + route.path, headers=headers, timeout=self.timeout, **kwargs
                        )
                else:
                    # Interactions are immune to global rate limits, ignore them here.
                    logger.info("Requesting (NO-GLOBAL) %s %s", route.method, route.path)
                    response = await self._session.request(
                        route.method, route.BASE_URL + route.path, headers=headers, timeout=self.timeout, **kwargs
                    )
                await self._update_bucket(response, route, bucket, rate_limit_storage)

                logger.debug("Response status: %s", response.status)
                await self.dispatcher.dispatch("request_response", response)

                # Response handling
                if response.status < 300:
                    # Ok!
                    return response

                await self._handle_response_error(route, response, rate_limit_storage)

        raise RateLimitingFailedError(self.max_retries, response)  # pyright: ignore [reportUnboundVariable]

    async def _handle_response_error(self, route: Route, response: ClientResponse, storage: RateLimitStorage) -> None:
        if response.status == 429:
            await self._handle_rate_limited_error(route, response, storage)
        else:
            error = await response.json()
            if response.status == 400:
                raise BadRequestError(error, response)
            if response.status == 401:
                raise UnauthorizedError(error, response)
            if response.status == 403:
                raise ForbiddenError(error, response)
            if response.status == 404:
                raise NotFoundError(error, response)
            if response.status >= 500:
                raise InternalServerError(error, response)
            raise HTTPRequestStatusError(error, response)

    async def _handle_rate_limited_error(
        self, route: Route, response: ClientResponse, storage: RateLimitStorage
    ) -> None:
        # Cloudflare bans arent proxied so via is not sent
        # These bans are usually 1h, however they can be permenant due to repeat offense.
        if "via" not in response.headers:
            raise CloudflareBanError()

        error = await response.json()

        if "X-RateLimit-Scope" in response.headers:
            scope = response.headers["X-RateLimit-Scope"]

            if scope == "shared":
                logger.info(
                    "Exceeded rate-limit on shared route! (%s)"
                    "This is not unexpected as shared rate-limits are shared by multiple users (and therefore, are out of our control). "
                    "This does not count towards a cloudflare ban. Retry after: %s",
                    route.bucket,
                    error["retry_after"],
                )
            elif scope == "user":
                logger.warning(
                    "Exceeded bucket rate-limit on bucket %s! This may be a bug in your bucket implementation. Retry after: %s",
                    route.bucket,
                    error["retry_after"],
                )
            elif scope == "global":
                # This will be logged by the global rate-limiter the user chose
                storage.global_rate_limiter.update(error["retry_after"])
            else:
                logger.warning("Received unknown rate limiting scope %s", scope)
        else:
            logger.debug("Received rate-limited response with no scope header")
            is_global = error["global"]

            if is_global:
                storage.global_rate_limiter.update(error["retry_after"])
            else:
                logger.warning(
                    "Received rate-limited response from a shared or bucket rate limit! No header was present. Bucket: %s",
                    route.bucket,
                )

    async def connect_to_gateway(
        self,
        *,
        version: Literal[6, 7, 8, 9, 10] | UndefinedType = UNDEFINED,
        encoding: Literal["json", "etf"] | UndefinedType = UNDEFINED,
        compress: Literal["zlib-stream"] | UndefinedType = UNDEFINED,
    ) -> ClientWebSocketResponse:
        """Connects to the gateway

        **Example usage:**

        .. code-block:: python

            ws = await http_client.connect_to_gateway()


        Parameters
        ----------
        version:
            The major API version to use

            .. hint::
                It is a good idea to pin this to make sure something doesn't unexpectedly change
        encoding:
            Whether to use json or etf for payloads
        compress:
            Payload compression from data sent from Discord.

        Raises
        ------
        RuntimeError
            :meth:`HTTPClient.setup` was not called yet.
        RuntimeError
            HTTPClient was closed.

        Returns
        -------
        aiohttp.ClientWebSocketResponse
            The gateway websocket
        """

        if self._session is None:
            raise RuntimeError("HTTPClient.setup was not called yet!")
        if self._session.closed:
            raise RuntimeError("HTTPClient is closed!")

        params = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if version is not UNDEFINED:
            params["v"] = version
        if encoding is not UNDEFINED:
            params["encoding"] = encoding
        if compress is not UNDEFINED:
            params["compress"] = compress

        # TODO: Aiohttp bug
        return await self._session.ws_connect("wss://gateway.discord.gg", params=params)  # type: ignore [reportUnknownMemberType]

    async def _get_bucket(self, route: Route, rate_limit_storage: RateLimitStorage) -> Bucket:
        """Gets a bucket object for a route.

        Strategy:
        - Get by calculated id (:attr:`Route.bucket`)
        - Create new based on :class:`BucketMetadata` found through the route (:attr:`Route.route`)
        - Create a new bucket with no info

        Parameters
        ----------
        route:
            The route to get the bucket for.
        rate_limit_storage:
            The user's rate limits.
        """
        # TODO: Can this be written better?
        bucket = await rate_limit_storage.get_bucket_by_nextcore_id(route.bucket)
        if bucket is not None:
            # Bucket already exists
            return bucket

        metadata = await rate_limit_storage.get_bucket_metadata(route.route)

        if metadata is not None:
            # Create a new bucket with info from the metadata
            bucket = Bucket(metadata)
            await rate_limit_storage.store_bucket_by_nextcore_id(route.bucket, bucket)
            return bucket

        # Create a new bucket with no info
        # Create metadata
        metadata = BucketMetadata()
        await rate_limit_storage.store_metadata(route.route, metadata)

        # Create the bucket
        bucket = Bucket(metadata)
        await rate_limit_storage.store_bucket_by_nextcore_id(route.bucket, bucket)

        return bucket

    async def _update_bucket(
        self, response: ClientResponse, route: Route, bucket: Bucket, rate_limit_storage: RateLimitStorage
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
            # No rate limit headers
            if response.status < 300:
                # No rate limit headers and no error, this is likely a route with no rate limits.
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
        linked_bucket = await rate_limit_storage.get_bucket_by_discord_id(bucket_hash)
        if linked_bucket is not None:
            # TODO: Migrate pending requests to the linked bucket
            await rate_limit_storage.store_bucket_by_nextcore_id(route.bucket, linked_bucket)
        else:
            # Automatically linking them
            await rate_limit_storage.store_bucket_by_discord_id(bucket_hash, bucket)

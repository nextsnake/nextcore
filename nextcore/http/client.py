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
from typing import TYPE_CHECKING, overload
from urllib.parse import quote

from aiohttp import ClientSession, FormData

from .. import __version__ as nextcore_version
from ..common import Dispatcher, UndefinedType, json_dumps, UNDEFINED
from .bucket import Bucket
from .bucket_metadata import BucketMetadata
from .errors import (
    BadRequestError,
    CloudflareBanError,
    ForbiddenError,
    HTTPRequestStatusError,
    InternalServerError,
    NotFoundError,
    RateLimitingFailedError,
    UnauthorizedError,
)
from .ratelimit_storage import RatelimitStorage
from .route import Route

if TYPE_CHECKING:
    from typing import Any, Final, Iterable, Literal

    from aiohttp import ClientResponse, ClientWebSocketResponse
    from discord_typings import (
        ActionRowData,
        AllowedMentionsData,
        AttachmentData,
        AuditLogData,
        ChannelData,
        EmbedData,
        FollowedChannelData,
        GetGatewayBotData,
        GetGatewayData,
        InviteData,
        InviteMetadata,
        MessageData,
        MessageReferenceData,
        ThreadChannelData,
        ThreadMemberData,
        UserData,
    )
    from discord_typings.resources.audit_log import AuditLogEvents

    from .authentication import BearerAuthentication, BotAuthentication
    from .file import File

logger = getLogger(__name__)

__all__: Final[tuple[str, ...]] = ("HTTPClient",)


class HTTPClient:
    """The HTTP client to interface with the Discord API.

    Parameters
    ----------
    trust_local_time:
        Whether to trust local time.
        If this is not set HTTP ratelimiting will be a bit slower but may be a bit more accurate on systems where the local time is off.
    timeout:
        The default request timeout in seconds.
    max_ratelimit_retries:
        How many times to attempt to retry a request after ratelimiting failed.

    Attributes
    ----------
    trust_local_time:
        If this is enabled, the ratelimiter will use the local time instead of the discord provided time. This may improve your bot's speed slightly.

        .. warning::
            If your time is not correct, and this is set to :data:`True`, this may result in more ratelimits being hit.

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
        How many times to attempt to retry a request after ratelimiting failed.

        .. note::
            This does not retry server errors.
    ratelimit_storages:
        Classes to store ratelimit information.

        The key here is the ratelimit_key (often a user ID).
    dispatcher:
        Events from the HTTPClient. See the :ref:`events<HTTPClient dispatcher>`
    """

    __slots__ = (
        "trust_local_time",
        "timeout",
        "default_headers",
        "max_retries",
        "ratelimit_storages",
        "dispatcher",
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
        self.default_headers: dict[str, str] = {
            "User-Agent": f"DiscordBot (https://github.com/nextsnake/nextcore, {nextcore_version})"
        }
        self.max_retries: int = max_ratelimit_retries
        self.ratelimit_storages: dict[str | None, RatelimitStorage] = {}  # User ID -> RatelimitStorage
        self.dispatcher: Dispatcher[Literal["request_response"]] = Dispatcher()

        # Internals
        self._session: ClientSession | None = None

    async def _request(
        self, route: Route, ratelimit_key: str | None, *, headers: dict[str, str] | None = None, global_priority: int = 0, **kwargs: Any
    ) -> ClientResponse:
        """Requests a route from the Discord API

        Parameters
        ----------
        route:
            The route to request
        ratelimit_key:
            A ID used for differentiating ratelimits.
            This should be a bot or oauth2 token.

            .. note::
                This should be :data:`None` for unauthenticated routes or webhooks (does not include modifying the webhook via a bot).
        global_priority:
            The request priority for global requests. **Lower** priority will be picked first.

            .. warning::
                This may be ignored by your :class:`BaseGlobalRateLimiter`.
        headers:
            Headers to mix with :attr:`HTTPClient.default_headers` to pass to :meth:`aiohttp.ClientSession.request`
        kwargs:
            Keyword arguments to pass to :meth:`aiohttp.ClientSession.request`

        Returns
        -------
        :class:`ClientResponse`
            The response from the request.

        Raises
        ------
        :exc:`CloudflareBanError`
            You have been temporarily banned from the Discord API for 1 hour due to too many requests.
            See the `documentation <https://discord.dev/opics/rate-limits#invalid-request-limit-aka-cloudflare-bans>`__ for more information.
        :exc:`BadRequestError`
            The request data was invalid.
        :exc:`UnauthorizedError`
            No token was provided on a endpoint that requires a token.
        :exc:`ForbiddenError`
            The token was valid but you do not have permission to use do this.
        :exc:`NotFoundError`
            The endpoint you requested was not found or a route parameter was invalid.
        :exc:`InternalServerError`
            Discord is having issues. Try again later.
        :exc:`HTTPRequestStatusError`
            A non-200 status code was returned.
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
                    async with ratelimit_storage.global_rate_limiter.acquire(priority=global_priority):
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
                await self.dispatcher.dispatch("request_response", response)

                # Handle ratelimit errors
                if response.status == 429:
                    # Cloudflare ban check
                    if "via" not in response.headers:
                        raise CloudflareBanError()

                    scope = response.headers["X-RateLimit-Scope"]
                    if scope == "global":
                        # Global rate-limit handling
                        # We use retry_after from the body instead of the headers as they have more precision than the headers.
                        data = await response.json()
                        retry_after = data["retry_after"]
                        
                        # Notify the global rate-limiter.
                        ratelimit_storage.global_rate_limiter.update(retry_after)
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
                    if response.status == 401:
                        raise UnauthorizedError(error, response)
                    if response.status == 403:
                        raise ForbiddenError(error, response)
                    if response.status == 404:
                        raise NotFoundError(error, response)
                    if response.status >= 500:
                        raise InternalServerError(error, response)
                    raise HTTPRequestStatusError(error, response)
                else:
                    # Should be in 0-200 range
                    return response
        # This should always be set as it has to pass through the loop atleast once.
        raise RateLimitingFailedError(self.max_retries, response)  # pyright: ignore [reportUnboundVariable]

    async def ws_connect(self, url: str, **kwargs: Any) -> ClientWebSocketResponse:
        """Connects to a websocket.

        **Example usage:**

        .. code-block:: python

            ws = await http_client.ws_connect("wss://gateway.discord.gg")


        Parameters
        ----------
        url:
            The url to connect to.
        kwargs:
            Keyword arguments to pass to :meth:`aiohttp.ClientSession.ws_connect`

        Returns
        -------
        :class:`aiohttp.ClientWebSocketResponse`
            The websocket response.
        """
        await self._ensure_session()
        assert self._session is not None, "Session was not set after HTTPClient._ensure_session()"
        return await self._session.ws_connect(url, heartbeat=None, **kwargs)

    async def _ensure_session(self) -> None:
        """Makes sure :attr:`HTTPClient._session` is set.

        This is made due to :class:`aiohttp.ClientSession` requring to being created in a async context.
        """
        # Maybe merge this into _request?
        if self._session is None:
            self._session = ClientSession(json_serialize=json_dumps)

    async def _get_bucket(self, route: Route, ratelimit_storage: RatelimitStorage) -> Bucket:
        """Gets a bucket object for a route.

        Strategy:
        - Get by calculated id (:attr:`Route.bucket`)
        - Create new based on :class:`BucketMetadata` found through the route (:attr:`Route.route`)
        - Create a new bucket with no info

        Parameters
        ----------
        route:
            The route to get the bucket for.
        ratelimit_storage:
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
    async def get_gateway(self) -> GetGatewayData:
        """Gets gateway connection info.

        See the `documentation <https://discord.dev/topics/gateway#get-gateway>`__ for more info.

        **Example usage:**

        .. code-block:: python

            gateway_info = await http_client.get_gateway()

        Returns
        -------
        :class:`dict`
            The gateway info.

            .. hint::
                A list of fields are available in the documentation.
        """
        route = Route("GET", "/gateway", ignore_global=True)
        r = await self._request(route, ratelimit_key=None)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_gateway_bot(self, authentication: BotAuthentication, *, global_priority: int = 0) -> GetGatewayBotData:
        """Gets gateway connection information.

        See the `documentation <https://discord.dev/topics/gateway#gateway-get-gateway-bot>`__

        **Example usage:**

        .. code-block:: python

            bot_info = await http_client.get_gateway_bot(token)

        .. note::
            This endpoint requires a bot token.

        Parameters
        ----------
        authentication:
            Authentication info.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        :class:`dict`
            Gateway connection info.

            .. hint::
                A list of fields are available in the documentation.
        """
        route = Route("GET", "/gateway/bot")
        r = await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers={"Authorization": str(authentication)}, global_priority=global_priority
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # Audit log
    async def get_guild_audit_log(
        self,
        authentication: BotAuthentication,
        guild_id: str | int,
        *,
        user_id: int | None = None,
        action_type: AuditLogEvents | None = None,
        before: int | None = None,
        limit: int = 50,
        global_priority: int = 0
    ) -> AuditLogData:
        """Gets the guild audit log.
        See the `documentation <https://discord.dev/resources/audit-log#get-guild-audit-log>`__

        .. note::
            This requires the ``VIEW_AUDIT_LOG`` permission.

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The guild to query the audit log for.
        user_id:
            The user to filter the audit log by.

            This will be the user that did the action if present, if not it will be the user that got actioned.

            If this is :data:`None` this will not filter.
        action_type:
            The action type to filter the audit log by.

            If this is :data:`None` this will not filter.
        before:
            Get entries before this entry.

            .. note::
                This does not have to be a valid entry id.
        limit:
            The amount of entries to get.

            This has a minimum of 1 and a maximum of 100.
        global_priority:
            The priority of the request for the global rate-limiter.
        
        Returns
        -------
        :class:`AuditLogData`
            The guild audit log.

            .. hint::
                A list of fields are available in the documentation.
        """
        route = Route("GET", f"/guilds/{guild_id}/audit-logs", guild_id=guild_id)
        params = {  # TODO: Use a typehint
            "limit": limit,
        }

        # They are NotRequired but can't be None.
        # This converts None to NotRequired
        if user_id is not None:
            params["user_id"] = user_id
        if action_type is not None:
            params["action_type"] = action_type
        if before is not None:
            params["before"] = before

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            params=params,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # Channel
    async def get_channel(self, authentication: BotAuthentication, channel_id: str | int, *, global_priority: int = 0) -> ChannelData:
        """Gets a channel by ID.

        See the `documentation <https://discord.dev/resources/channels#get-channel>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The channel ID to get.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        :class:`ChannelData`
            The channel.

            .. hint::
                A list of fields are available in the documentation.
        """
        route = Route("GET", "/channels/{channel_id}", channel_id=channel_id)
        r = await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers={"Authorization": str(authentication)}, global_priority=global_priority
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # These 3 requests are 1 route but are split up for convinience
    async def modify_group_dm(
        self,
        authentication: BearerAuthentication,
        channel_id: str | int,
        *,
        name: str | UndefinedType = UNDEFINED,
        icon: str | None | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0
    ) -> ChannelData:
        """Modifies the group dm.

        See the `docoumentation <https://discord.dev/resources/channel#modify-channel>`__

        .. warning::
            This shares ratelimits with :attr:`HTTPClient.modify_guild_channel` and :attr:`HTTPClient.modify_thread`.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the group dm channel to update
        name:
            The name of the group dm.

            .. note::
                This has to be between 1 to 100 characters long.
        icon:
            A base64 encoded image of what to change the group dm icon to.
        reason:
            A reason for the audit log.

            .. note::
                This has to be between 1 and 512 characters
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("PATCH", "/channels/{channel_id}", channel_id=channel_id)
        payload = {}  # TODO: Use a typehint for payload

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name

        if icon is not UNDEFINED:
            payload["icon"] = icon

        headers = {"Authorization": str(authentication)}

        if reason is not UNDEFINED:
            headers["reason"] = reason

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, json=payload, global_priority=global_priority)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_guild_channel(
        self,
        authentication: BearerAuthentication,
        channel_id: str | int,
        *,
        name: str | UndefinedType = UNDEFINED,
        channel_type: Literal[0, 5] | UndefinedType = UNDEFINED,
        position: int | None | UndefinedType = UNDEFINED,
        topic: str | None | UndefinedType = UNDEFINED,
        nsfw: bool | None | UndefinedType = UNDEFINED,
        rate_limit_per_user: int | None | UndefinedType = UNDEFINED,
        bitrate: int | None | UndefinedType = UNDEFINED,
        user_limit: int | None | UndefinedType = UNDEFINED,
        permission_overwrites: list[dict[Any, Any]] | None | UndefinedType = UNDEFINED,  # TODO: implement a partial
        parent_id: int | str | UndefinedType = UNDEFINED,
        rtc_region: str | None | UndefinedType = UNDEFINED,
        video_quality_mode: Literal[1, 2] | None | UndefinedType = UNDEFINED,  # TODO: Implement VideoQualityMode
        default_auto_archive_duration: Literal[60, 1440, 4320, 10080] | None | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0
    ) -> ChannelData:
        """Modifies a guild channel.

        See the `docoumentation <https://discord.dev/resources/channel#modify-channel>`__


        .. warning::
            This shares ratelimits with :attr:`HTTPClient.modify_group_dm` and :attr:`HTTPClient.modify_thread`.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to update.
        name:
            The name of the channel.
        channel_type:
            The type of the channel.

            .. note::
                This is named ``type`` in the API, however to not overwrite the type function in python this is changed here.
        position:
            The position of the channel.

            .. note::
                If this is set to :data:`None` it will default to ``0``.
        topic:
            The channel topic.
        nsfw:
            Whether the channel marked as age restricted.

            .. note::
                If this is set to :data:`None` it will default to :data:`False`.
        rate_limit_per_user:
            How many seconds a user has to wait before sending another message or create a thread.

            Bots, as well as users with the ``manage_messages`` or ``manage_channel`` are unaffected
            A member can send one message and create one thread per period.

            .. note::
                This has to be between 0-21600 seconds.
        bitrate:
            The bitrate of the channel in bits per second.

            .. note::
                This only works for stage / voice channels.
            .. note::
                This has to be between 8000-96000 for guilds without the ``VIP_REGIONS`` feature.

                For guilds with the ``VIP_REGIONS`` feature this has to be between 8000-128000.
        user_limit:
            The maximum amount of users that can be in a voice channel at a time.
        permission_overwrites:
            The permission overwrites for the channel.

            .. note::
                If this is set to :data:`None` it will default to an empty list.
        parent_id:
            The id of the parent channel.

            This can be a text channel for threads or a category channel.
        rtc_region:
            The voice region of the channel.

            .. note::
                If this is :data:`None` it is automatic. Every time someone joins a empty channel, the closest region will be used.
        video_quality_mode:
            The video quality mode of the channel.

            .. note::
                If this is :data:`None` it will not be present in the Guild payload.

                This is rougly the same as setting it to ``1``.
        default_auto_archive_duration:
            The default auto archive duration for threads created in this channel.

            .. note::
                If this is :data:`None` it will not be present in the Guild payload.

                The client treats this as it being set to 24 hours however this may change without notice.
        reason:
            The reason to put in the audit log.
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route("PATCH", "/channels/{channel_id}", channel_id=channel_id)
        payload = {}  # TODO: Use a typehint for payload

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name
        if channel_type is not UNDEFINED:
            payload["type"] = channel_type
        if position is not UNDEFINED:
            payload["position"] = position
        if topic is not UNDEFINED:
            payload["topic"] = topic
        if nsfw is not UNDEFINED:
            payload["nsfw"] = nsfw
        if rate_limit_per_user is not UNDEFINED:
            payload["rate_limit_per_user"] = rate_limit_per_user
        if bitrate is not UNDEFINED:
            payload["bitrate"] = bitrate
        if user_limit is not UNDEFINED:
            payload["user_limit"] = user_limit
        if permission_overwrites is not UNDEFINED:
            payload["permission_overwrites"] = permission_overwrites
        if parent_id is not UNDEFINED:
            payload["parent_id"] = parent_id
        if rtc_region is not UNDEFINED:
            payload["rtc_region"] = rtc_region
        if video_quality_mode is not UNDEFINED:
            payload["video_quality_mode"] = video_quality_mode
        if default_auto_archive_duration is not UNDEFINED:
            payload["default_auto_archive_duration"] = default_auto_archive_duration

        headers = {"Authorization": str(authentication)}

        if reason is not UNDEFINED:
            headers["reason"] = reason

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, json=payload, global_priority=global_priority)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_thread(
        self,
        authentication: BotAuthentication,
        thread_id: int | str,
        *,
        name: str | UndefinedType = UNDEFINED,
        archived: bool | UndefinedType = UNDEFINED,
        auto_archive_duration: Literal[60, 1440, 4320, 10080] | UndefinedType = UNDEFINED,
        locked: bool | UndefinedType = UNDEFINED,
        invitable: bool | UndefinedType = UNDEFINED,
        rate_limit_per_user: int | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0
    ) -> ThreadChannelData:
        """Modifies a thread.

        See the `docoumentation <https://discord.dev/resources/channel#modify-channel>`__

        .. warning::
            This shares ratelimits with :attr:`HTTPClient.modify_group_dm` and :attr:`HTTPClient.modify_guild_channel`.

        Parameters
        ----------
        authentication:
            Authentication info.
        thread_id:
            The id of the thread to update.
        name:
            The name of the thread.
        archived:
            Whether the thread is archived.
        auto_archive_duration:
            How long in minutes to automatically archive the thread after recent activity
        locked:
            Whether the thread can only be un-archived by members with the ``manage_threads`` permission.
        invitable:
            Whether members without the ``manage_threads`` permission can invite members without the ``manage_channels`` permission to the thread.
        rate_limit_per_user:
            The duration in seconds that a user must wait before sending another message to the thread.

            Bots, as well as users with the ``manage_messages`` or ``manage_channel`` are unaffected

            .. note::
                This has to be between 0-21600 seconds.
        reason:
            The reason to put in the audit log.
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route("PATCH", "/channels/{channel_id}", channel_id=thread_id)
        payload = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name
        if archived is not UNDEFINED:
            payload["archived"] = archived
        if auto_archive_duration is not UNDEFINED:
            payload["auto_archive_duration"] = auto_archive_duration
        if locked is not UNDEFINED:
            payload["locked"] = locked
        if invitable is not UNDEFINED:
            payload["invitable"] = invitable
        if rate_limit_per_user is not UNDEFINED:
            payload["rate_limit_per_user"] = rate_limit_per_user

        headers = {"Authorization": str(authentication)}

        if reason is not UNDEFINED:
            headers["reason"] = reason

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, json=payload, global_priority=global_priority)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_channel(
        self, authentication: BotAuthentication | BearerAuthentication, channel_id: int | str, *, global_priority: int = 0
    ) -> None:
        """Deletes a channel.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to delete.
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route("DELETE", "/channels/{channel_id}", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}

        await self._request(route, headers=headers, ratelimit_key=authentication.rate_limit_key, global_priority=global_priority)

    @overload
    async def get_channel_messages(
        self, authentication: BotAuthentication, channel_id: int | str, *, around: int, limit: int | UndefinedType, global_priority: int = 0
    ) -> list[MessageData]:
        ...

    @overload
    async def get_channel_messages(
        self, authentication: BotAuthentication, channel_id: int | str, *, before: int, limit: int | UndefinedType, global_priority: int = 0
    ) -> list[MessageData]:
        ...

    @overload
    async def get_channel_messages(
        self, authentication: BotAuthentication, channel_id: int | str, *, after: int, limit: int | UndefinedType, global_priority: int = 0
    ) -> list[MessageData]:
        ...

    @overload
    async def get_channel_messages(self, authentication: BotAuthentication, channel_id: int | str, *, global_priority: int = 0) -> list[MessageData]:
        ...

    async def get_channel_messages(
        self,
        authentication: BotAuthentication,
        channel_id: int | str,
        *,
        around: int | UndefinedType = UNDEFINED,
        before: int | UndefinedType = UNDEFINED,
        after: int | UndefinedType = UNDEFINED,
        limit: int | UndefinedType = UNDEFINED,
        global_priority: int = 0
    ) -> list[MessageData]:
        """Gets messages from a channel.

        See the `documentation <https://discord.dev/resources/channel#get-channel-messages>`__

        .. note::
            This requires the ``view_channel`` permission..

        .. note::
            If the ``read_message_history`` permission is not given, this will return an empty list.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to get messages from.
        around:
            The id of the message to get messages around.

            .. note::
                This does not have to be a valid message id.
        before:
            The id of the message to get messages before.

            .. note::
                This does not have to be a valid message id.
        after:
            The id of the message to get messages after.

            .. note::
                This does not have to be a valid message id.
        limit:
            The number of messages to get.

            .. note::
                This has to be between 1-100.
            .. note::
                If this is not provided it will default to ``50``.
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route("GET", "/channels/{channel_id}/messages", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}

        params = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if around is not UNDEFINED:
            params["around"] = around
        if before is not UNDEFINED:
            params["before"] = before
        if after is not UNDEFINED:
            params["after"] = after
        if limit is not UNDEFINED:
            params["limit"] = limit

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, params=params, global_priority=global_priority)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def create_message(
        self,
        authentication: BotAuthentication,
        channel_id: int | str,
        *,
        content: str | UndefinedType = UNDEFINED,
        tts: bool | UndefinedType = UNDEFINED,
        embeds: list[EmbedData] | UndefinedType = UNDEFINED,
        allowed_mentions: AllowedMentionsData | UndefinedType = UNDEFINED,
        message_reference: MessageReferenceData | UndefinedType = UNDEFINED,
        componenets: list[ActionRowData] | UndefinedType = UNDEFINED,
        sticker_ids: list[int] | UndefinedType = UNDEFINED,
        files: Iterable[File] | UndefinedType = UNDEFINED,
        attachments: list[AttachmentData] | UndefinedType = UNDEFINED,  # TODO: Partial
        flags: int | UndefinedType = UNDEFINED,
        global_priority: int = 0
    ) -> MessageData:
        """Creates a message in a channel.

        See the `documentation <https://discord.dev/resources/channel#create-message>`__

        .. note::
            This requires the ``view_channel`` and ``send_messages`` permission.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to create a message in.
        content:
            The content of the message.
        tts:
            Whether the ``content`` should be spoken out by the Discord client upon send.

            .. note::
                This will still set ``Message.tts`` to :data:`True` even if ``content`` is not provided.
        embeds:
            The embeds to send with the message.

            .. hint::
                The fields are in the `Embed <https://discord.dev/resources/channel#embed-object>`__ documentation.

            .. note::
                There is a maximum 6,000 character limit across all embeds.

                See the `embed limits documentation <https://discord.dev/resources/channel#embed-object-embed-limits>`__ for more info.
        allowed_mentions:
            The allowed mentions for the message.
        message_reference:
            The message to reply to.
        componenets:
            The components to send with the message.
        sticker_ids:
            A list of sticker ids to attach to the message.

            .. note::
                This has a max of 3 stickers.
        files:
            The files to send with the message.
        attachments:
            Metadata about the ``files`` parameter.

            .. note::
                This only includes the ``filename`` and ``description`` fields.
        flags:
            Bitwise flags to send with the message.

            .. note::
                Only the ``SUPRESS_EMBEDS`` flag can be set.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        :class:`discord_typings.MessageData`
            The message that was sent.
        """
        route = Route("POST", "/channels/{channel_id}/messages", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}

        # We use payload_json here as the format is more strictly defined than form data.
        # This means we don't have to manually format the data.
        payload = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if content is not UNDEFINED:
            payload["content"] = content
        if tts is not UNDEFINED:
            payload["tts"] = tts
        if embeds is not UNDEFINED:
            payload["embeds"] = embeds
        if allowed_mentions is not UNDEFINED:
            payload["allowed_mentions"] = allowed_mentions
        if message_reference is not UNDEFINED:
            payload["message_reference"] = message_reference
        if componenets is not UNDEFINED:
            payload["componenets"] = componenets
        if sticker_ids is not UNDEFINED:
            payload["sticker_ids"] = sticker_ids
        if attachments is not UNDEFINED:
            payload["attachments"] = attachments
        if flags is not UNDEFINED:
            payload["flags"] = flags

        # Create a form data response as files cannot be uploaded via json.
        form = FormData()
        form.add_field("payload_json", json_dumps(payload))

        # Add files
        if files is not UNDEFINED:
            for file_id, file in enumerate(files):
                # Content type seems to have no effect here.
                form.add_field(f"file[{file_id}]", file.contents, filename=file.name)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            data=form,
            global_priority=global_priority
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def crosspost_message(
        self, authentication: BotAuthentication, channel_id: int | str, message_id: int | str, *, global_priority: int = 0
    ) -> MessageData:
        """Crossposts a message from another channel.

        See the `documentation <https://discord.dev/resources/channel#crosspost-message>`__

        .. note::
            This requires the ``send_messages`` permission when trying to crosspost a message sent by the current user.

            If not this requires the ``manage_messages`` permission.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to crosspost the message to.
        message_id:
            The id of the message to crosspost.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        :class:`discord_typings.MessageData`
            The message that was crossposted.
        """
        route = Route(
            "POST",
            "/channels/{channel_id}/messages/{message_id}/crosspost",
            channel_id=channel_id,
            message_id=message_id,
        )
        headers = {"Authorization": str(authentication)}

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def create_reaction(
        self, authentication: BotAuthentication, channel_id: int | str, message_id: int | str, emoji: str, *, global_priority: int = 0
    ) -> None:
        """Creates a reaction to a message.

        See the `documentation <https://discord.dev/resources/channel#create-reaction>`__

        .. note::
            This requires the ``read_message_history`` permission.

            This also requires the ``add_reactions`` permission if noone else has reacted to the message with this emoji.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel where the message is located.
        message_id:
            The id of the message to add a reaction to.
        emoji:
            The emoji to add to the message.

            This is either a unicode emoji or a custom emoji in the format ``name:id``.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "PUT",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
            channel_id=channel_id,
            message_id=message_id,
            emoji=quote(emoji),
        )
        headers = {"Authorization": str(authentication)}

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority)

    async def delete_own_reaction(
        self, authentication: BotAuthentication, channel_id: int | str, message_id: int | str, emoji: str, *, global_priority: int = 0
    ) -> None:
        """Deletes a reaction from a message.

        See the `documentation <https://discord.dev/resources/channel#delete-own-reaction>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel where the message is located.
        message_id:
            The id of the message to remove a reaction from.
        emoji:
            The emoji to remove from the message.

            This is either a unicode emoji or a custom emoji in the format ``name:id``.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
            channel_id=channel_id,
            message_id=message_id,
            emoji=quote(emoji),
        )
        headers = {"Authorization": str(authentication)}

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority)

    async def delete_user_reaction(
        self,
        authentication: BotAuthentication,
        channel_id: int | str,
        message_id: int | str,
        emoji: str,
        user_id: int | str,
        *,
        global_priority: int = 0
    ) -> None:
        """Deletes a reaction from a message from another user.

        See the `documentation <https://discord.dev/resources/channel#delete-user-reaction>`__

        .. note::
            This requires the ``manage_messages`` permission.

        .. note::
            This does not error when attempting to remove a reaction that does not exist.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel where the message is located.
        message_id:
            The id of the message to remove a reaction from.
        emoji:
            The emoji to remove from the message.

            This is either a unicode emoji or a custom emoji in the format ``name:id``.
        user_id:
            The id of the user to remove the reaction from.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}",
            channel_id=channel_id,
            message_id=message_id,
            emoji=quote(emoji),
            user_id=user_id,
        )
        headers = {"Authorization": str(authentication)}

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority)

    async def get_reactions(
        self,
        authentication: BotAuthentication,
        channel_id: int | str,
        message_id: int | str,
        emoji: str,
        *,
        after: str | int | UndefinedType = UNDEFINED,
        limit: int | UndefinedType = UNDEFINED,
        global_priority: int = 0
    ) -> list[UserData]:
        """Gets the reactions to a message.

        See the `documentation <https://discord.dev/resources/channel#get-reactions>`__

        .. note::
            This requires the ``read_message_history`` permission.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel where the message is located.
        message_id:
            The id of the message to get the reactions from.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[:class:`UserData`]
            The users that has reacted with this emoji.
        """
        route = Route(
            "GET",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}",
            channel_id=channel_id,
            message_id=message_id,
            emoji=quote(emoji),
        )
        headers = {"Authorization": str(authentication)}

        params = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if after is not UNDEFINED:
            params["after"] = after
        if limit is not UNDEFINED:
            params["limit"] = limit

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, params=params, global_priority=global_priority)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_all_reactions(
        self, authentication: BotAuthentication, channel_id: int | str, message_id: int | str, *, global_priority: int = 0
    ) -> None:
        """Deletes all reactions from a message.

        See the `documentation <https://discord.dev/resources/channel#delete-all-reactions>`__

        .. note::
            This requires the ``manage_messages`` permission.

        .. note::
            This will cause a ``MESSAGE_REACTION_REMOVE_ALL`` dispatch event.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel where the message is located.
        message_id:
            The id of the message to remove all reactions from.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions",
            channel_id=channel_id,
            message_id=message_id,
        )
        headers = {"Authorization": str(authentication)}

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority)

    async def delete_all_reactions_for_emoji(
        self, authentication: BotAuthentication, channel_id: int | str, message_id: int | str, emoji: str, *, global_priority: int = 0
    ) -> None:
        """Deletes all reactions from a message with a specific emoji.

        See the `documentation <https://discord.dev/resources/channel#delete-all-reactions-for-emoji>`__

        .. note::
            This requires the ``manage_messages`` permission.

        .. note::
            This will cause a ``MESSAGE_REACTION_REMOVE_EMOJI`` dispatch event.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel where the message is located.
        message_id:
            The id of the message to remove all reactions from.
        emoji:
            The emoji to remove from the message.

            This is either a unicode emoji or a custom emoji in the format ``name:id``.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}",
            channel_id=channel_id,
            message_id=message_id,
            emoji=quote(emoji),
        )
        headers = {"Authorization": str(authentication)}

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority)

    async def edit_message(
        self,
        authentication: BotAuthentication,
        channel_id: int | str,
        message_id: int | str,
        *,
        content: str | None | UndefinedType = UNDEFINED,
        embeds: list[EmbedData] | None | UndefinedType = UNDEFINED,
        flags: int | None | UndefinedType = UNDEFINED,
        allowed_mentions: AllowedMentionsData | None | UndefinedType = UNDEFINED,
        components: list[ActionRowData] | None | UndefinedType = UNDEFINED,
        files: list[File] | None | UndefinedType = UNDEFINED,
        attachments: list[AttachmentData] | None | UndefinedType = UNDEFINED,  # TODO: Partial
        global_priority: int = 0
    ) -> MessageData:
        """Edits a message.

        See the `documentation <https://discord.dev/resources/channel#edit-message>`__

        .. note::
            This requires the ``manage_messages`` permission.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel where the message is located.
        message_id:
            The id of the message to edit.
        content:
            The new content of the message.

            .. note::
                If this is set to ``None``, there will be no message contents.

            .. note::
                Adding/removing mentions will not affect mentions.
        embeds:
            The new embeds of the message.

            This overwrites the previous embeds
        flags:
            The new flags of the message.

            .. warning::
                Only the ``SUPPRESS_EMBEDS`` flag can be set. Trying to set other flags will be ignored.
        allowed_mentions:
            The new allowed mentions of the message.

            .. note::
                Setting this to ``None`` will make it use the default allowed mentions.
        components:
            The new components of the message.
        files:
            The new files of the message.
        attachments:
            The new attachments of the message.

            .. warning::
                This has to include previous and current attachments or they will be removed.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        :class:`MessageData`
            The edited message.
        """
        route = Route(
            "PATCH", "/channels/{channel_id}/messages/{message_id}", channel_id=channel_id, message_id=message_id
        )

        headers = {"Authorization": str(authentication)}
        payload = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if content is not UNDEFINED:
            payload["content"] = content
        if embeds is not UNDEFINED:
            payload["embeds"] = embeds
        if flags is not UNDEFINED:
            payload["flags"] = flags
        if allowed_mentions is not UNDEFINED:
            payload["allowed_mentions"] = allowed_mentions
        if components is not UNDEFINED:
            payload["components"] = components
        if attachments is not UNDEFINED:
            payload["attachments"] = attachments

        # This is a special case where we need to send the files as a multipart form
        form = FormData()
        if files is not UNDEFINED:
            if files is None:
                raise NotImplementedError("What is this even supposed to do?")
            for file in files:
                form.add_field("file", file.contents, filename=file.name)

        form.add_field("payload_json", json_dumps(payload))

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, data=form, global_priority=global_priority)

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def delete_message(
        self,
        authentication: BotAuthentication,
        channel_id: str | int,
        message_id: str | int,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0
    ) -> None:
        """Deletes a message.

        See the `documentation <https://discord.dev/resources/channel#delete-message>`__

        .. note::
            This requires the ``manage_messages`` permission.

        .. note::
            This will cause a ``MESSAGE_DELETE`` dispatch event.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel where the message is located.
        message_id:
            The id of the message to delete.
        reason:
            The reason for deleting the message.

            .. note::
                If this is set to ``Undefined``, there will be no reason.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "DELETE", "/channels/{channel_id}/messages/{message_id}", channel_id=channel_id, message_id=message_id
        )
        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority)

    async def bulk_delete_messages(
        self,
        authentication: BotAuthentication,
        channel_id: str | int,
        messages: list[str] | list[int] | list[str | int],
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0
    ) -> None:
        """Deletes multiple messages.

        See the `documentation <https://discord.dev/resources/channel#delete-message>`__

        .. note::
            This requires the ``manage_messages`` permission.

        .. note::
            This will cause a ``MESSAGE_DELETE_BULK`` dispatch event.

        .. warning::
            This will not delete messages older than two weeks.

            If any of the messages provided are older than 2 weeks this will error.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel where the message is located.
        messages:
            The ids of the messages to delete.

            .. note::
                This has to be between 2 and 100 messages.

                Invalid messages still count towards the limit.
        reason:
            The reason for deleting the message.

            .. note::
                If this is set to ``Undefined``, there will be no reason.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("POST", "/channels/{channel_id}/messages/bulk-delete", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers=headers, json={"messages": messages}, global_priority=global_priority
        )

    async def edit_channel_permissions(
        self,
        authentication: BotAuthentication,
        channel_id: str | int,
        target_type: Literal[0, 1],
        target_id: str | int,
        *,
        allow: str | None | UndefinedType = UNDEFINED,
        deny: str | None | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0
    ) -> None:
        """Edits the permissions of a channel.

        See the `documentation <https://discord.dev/resources/channel#edit-channel-permissions>`__

        .. note::
            This requires the ``manage_roles`` permission.

            This also requires the permissions you want to grant/deny unless your bot has a ``manage_roles`` overwrite.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to edit.
        target_type:
            The type of the target.

            0: Role
            1: User
        target_id:
            The id of the target to edit permissions for.
        allow:
            A bitwise flag of permissions to allow.

            .. note::
                If this is set to :data:`None`, it will default to ``0``.
        deny:
            A bitwise flag of permissions to allow.

            .. note::
                If this is set to :data:`None`, it will default to ``0``.
        reason:
            The reason to show in audit log

            .. note::
                If this is set to ``Undefined``, there will be no reason.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "PUT",
            "/channels/{channel_id}/permissions/{target_id}",
            channel_id=channel_id,
            target_id=target_id,
        )
        headers = {"Authorization": str(authentication)}

        payload = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if allow is not UNDEFINED:
            payload["allow"] = allow
        if deny is not UNDEFINED:
            payload["deny"] = deny

        payload["type"] = target_type

        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, json=payload, global_priority=global_priority)

    async def get_channel_invites(
        self, authentication: BotAuthentication, channel_id: str | int, *, global_priority: int = 0
    ) -> list[InviteMetadata]:
        """Gets the invites for a channel.

        See the `documentation <https://discord.dev/resources/channel#get-channel-invites>`__

        .. note::
            This requires the ``manage_channels`` permission.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to get invites for.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[:class:`InviteMetadata`]
            The invites for the channel.
        """
        route = Route("GET", "/channels/{channel_id}/invites", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority)

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    @overload
    async def create_channel_invite(
        self,
        authentication: BotAuthentication,
        channel_id: str | int,
        *,
        max_age: int | UndefinedType = UNDEFINED,
        max_uses: int | UndefinedType = UNDEFINED,
        temporary: bool | UndefinedType = UNDEFINED,
        unique: bool | UndefinedType = UNDEFINED,
        target_type: Literal[0],
        target_user_id: str | int,
        target_application_id: UndefinedType = UNDEFINED,
        global_priority: int = 0
    ) -> InviteData:
        ...

    @overload
    async def create_channel_invite(
        self,
        authentication: BotAuthentication,
        channel_id: str | int,
        *,
        max_age: int | UndefinedType = UNDEFINED,
        max_uses: int | UndefinedType = UNDEFINED,
        temporary: bool | UndefinedType = UNDEFINED,
        unique: bool | UndefinedType = UNDEFINED,
        target_type: Literal[1],
        target_user_id: UndefinedType = UNDEFINED,
        target_application_id: str | int,
        global_priority: int = 0
    ) -> InviteData:
        ...

    @overload
    async def create_channel_invite(
        self,
        authentication: BotAuthentication,
        channel_id: str | int,
        *,
        max_age: int | UndefinedType = UNDEFINED,
        max_uses: int | UndefinedType = UNDEFINED,
        temporary: bool | UndefinedType = UNDEFINED,
        unique: bool | UndefinedType = UNDEFINED,
        target_type: UndefinedType = UNDEFINED,
        target_user_id: UndefinedType = UNDEFINED,
        target_application_id: UndefinedType = UNDEFINED,
        global_priority: int = 0
    ) -> InviteData:
        ...

    async def create_channel_invite(
        self,
        authentication: BotAuthentication,
        channel_id: str | int,
        *,
        max_age: int | UndefinedType = UNDEFINED,
        max_uses: int | UndefinedType = UNDEFINED,
        temporary: bool | UndefinedType = UNDEFINED,
        unique: bool | UndefinedType = UNDEFINED,
        target_type: Literal[0, 1] | UndefinedType = UNDEFINED,
        target_user_id: str | int | UndefinedType = UNDEFINED,
        target_application_id: str | int | UndefinedType = UNDEFINED,
        global_priority: int = 0
    ) -> InviteData:
        """Creates an invite for a channel.

        Read the `documentation <https://discord.dev/resources/channel#create-channel-invite>`__

        Parameters
        -----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to create an invite for.
        max_age:
            How long the invite should last.

            .. note::
                This has to be between 0 and 604800 seconds. (7 days)

                Setting this to ``0`` will make it never expire.
        max_uses:
            How many times the invite can be used before getting deleted.
        temporary:
            Whether the invite grants temporary membership.

            This will kick members if they havent got a role when logging off.
        unique:
            Whether discord will make a new invite regardless of existing invites.
        target_type:
            The type of the target.

            0: A user's stream
            1: ``EMBEDDED`` Activity
        target_user_id:
            The id of the user streaming to invite to.

            .. note::
                This can only be set if ``target_type`` is ``0``.
        target_application_id:
            The id of the ``EMBEDDED`` activity to play.

            .. note::
                This can only be set if ``target_type`` is ``1``.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        :class:`InviteData`
            The invite data.
        """
        route = Route("POST", "/channels/{channel_id}/invites", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}

        payload = {}

        if max_age is not UNDEFINED:
            payload["max_age"] = max_age
        if max_uses is not UNDEFINED:
            payload["max_uses"] = max_uses
        if temporary is not UNDEFINED:
            payload["temporary"] = temporary
        if unique is not UNDEFINED:
            payload["unique"] = unique
        if target_type is not UNDEFINED:
            payload["target_type"] = target_type
        if target_user_id is not UNDEFINED:
            payload["target_user_id"] = target_user_id
        if target_application_id is not UNDEFINED:
            payload["target_application_id"] = target_application_id

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, json=payload, global_priority=global_priority)

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def delete_channel_permission(
        self,
        authentication: BotAuthentication,
        channel_id: str | int,
        target_id: str | int,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0
    ) -> None:
        """Deletes a channel permission.

        Read the `documentation <https://discord.dev/resources/channel#delete-channel-permission>`__

        Parameters
        -----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to delete the permission from.
        target_id:
            The id of the user or role to delete the permission from.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "DELETE", "/channels/{channel_id}/permissions/{target_id}", channel_id=channel_id, target_id=target_id
        )
        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority)

    async def follow_news_channel(
        self, authentication: BotAuthentication, channel_id: str | int, webhook_channel_id: str | int, *, global_priority: int = 0
    ) -> FollowedChannelData:
        """Follows a news channel.

        Read the `documentation <https://discord.dev/resources/channel#follow-news-channel>`__

        .. note::
            This requires the ``manage_webhooks`` permission.

        Parameters
        -----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to follow.
        webhook_channel_id:
            The id of the channel to receive posts to.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        :class:`FollowedChannelData`
            The followed channel data.
        """
        route = Route("POST", "/channels/{channel_id}/followers", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}
        payload = {"webhook_channel_id": webhook_channel_id}

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, json=payload, global_priority=global_priority)

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def trigger_typing_indicator(self, authentication: BotAuthentication, channel_id: str | int, *, global_priority: int = 0) -> None:
        """Triggers a typing indicator.

        Read the `documentation <https://discord.dev/resources/channel#trigger-typing-indicator>`__

        Parameters
        -----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to trigger the typing indicator on.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("POST", "/channels/{channel_id}/typing", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers)

    async def get_pinned_messages(self, authentication: BotAuthentication, channel_id: str | int, *, global_priority: int = 0) -> list[MessageData]:
        """Gets the pinned messages of a channel.

        Read the `documentation <https://discord.dev/resources/channel#get-pinned-messages>`__

        .. note::
            This requires the ``read_messages`` permission.

        Parameters
        -----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to get the pinned messages of.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[:class:`discord_typings.MessageData`]
            The pinned messages.
        """
        route = Route("GET", "/channels/{channel_id}/pins", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers)

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def pin_message(
        self,
        authentication: BotAuthentication,
        channel_id: str | int,
        message_id: str | int,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0
    ) -> None:
        """Pins a message.

        Read the `documentation <https://discord.dev/resources/channel#pin-message>`__

        .. note::
            This requires the ``manage_messages`` permission.

        .. warning::
            This will fail if there is ``50`` or more messages pinned.

        Parameters
        -----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to pin the message in.
        message_id:
            The id of the message to pin.
        reason:
            The reason to put in the audit log.

            .. note::
                This has to be between 1 and 512 characters.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("PUT", "/channels/{channel_id}/pins/{message_id}", channel_id=channel_id, message_id=message_id)
        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers)

    async def unpin_message(
        self, authentication: BotAuthentication, channel_id: str | int, message_id: str | int, *, global_priority: int = 0
    ) -> None:
        """Unpins a message.

        Read the `documentation <https://discord.dev/resources/channel#unpin-message>`__

        .. note::
            This requires the ``manage_messages`` permission.

        Parameters
        -----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to unpin the message in.
        message_id:
            The id of the message to unpin.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "DELETE", "/channels/{channel_id}/pins/{message_id}", channel_id=channel_id, message_id=message_id
        )
        headers = {"Authorization": str(authentication)}

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority)

    async def group_dm_add_recipient(
        self, authentication: BearerAuthentication, channel_id: str | int, user_id: str | int, *, global_priority: int = 0
    ) -> None:
        """Adds a recipient to a group DM.

        Read the `documentation <https://discord.dev/resources/channel#group-dm-add-recipient>`__

        Parameters
        -----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to add the recipient to.
        user_id:
            The id of the user to add.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("PUT", "/channels/{channel_id}/recipients/{user_id}", channel_id=channel_id, user_id=user_id)
        headers = {"Authorization": str(authentication)}

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority)

    async def group_dm_remove_recipient(
        self, authentication: BearerAuthentication, channel_id: str | int, user_id: str | int, *, global_priority: int = 0
    ) -> None:
        """Removes a recipient from a group DM.

        Read the `documentation <https://discord.dev/resources/channel#group-dm-remove-recipient>`__

        Parameters
        -----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to remove the recipient from.
        user_id:
            The id of the user to remove.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("DELETE", "/channels/{channel_id}/recipients/{user_id}", channel_id=channel_id, user_id=user_id)
        headers = {"Authorization": str(authentication)}

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority)

    async def start_thread_from_message(
        self,
        authentication: BotAuthentication,
        channel_id: str | int,
        message_id: str | int,
        name: str,
        *,
        auto_archive_duration: Literal[60, 1440, 4320, 10080] | UndefinedType = UNDEFINED,
        rate_limit_per_user: int | None | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0
    ) -> ChannelData:
        """Starts a thread from a message.

        Read the `documentation <https://discord.dev/resources/channel#start-thread-from-message>`__

        Parameters
        -----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to start the thread in.
        message_id:
            The id of the message to start the thread from.
        name:
            The name of the thread.
        auto_archive_duration:
            The auto archive duration of the thread.
        rate_limit_per_user: :class:`int` | :data:`None` | :class:`UndefinedType`
            The time every member has to wait before sending another message.

            .. note::
                This has to be between 0 and 21600.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "POST",
            "/channels/{channel_id}/messages/{message_id}/threads",
            channel_id=channel_id,
            message_id=message_id,
        )

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        payload = {
            "name": name,
        }

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if auto_archive_duration is not UNDEFINED:
            payload["auto_archive_duration"] = auto_archive_duration
        if rate_limit_per_user is not UNDEFINED:
            payload["rate_limit_per_user"] = rate_limit_per_user

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, json=payload, global_priority=global_priority)

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def start_thread_without_message(
        self,
        authentication: BotAuthentication,
        channel_id: str | int,
        name: str,
        *,
        auto_archive_duration: Literal[60, 1440, 4320, 10080] | UndefinedType = UNDEFINED,
        thread_type: Literal[11, 12] | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        invitable: bool | UndefinedType = UNDEFINED,
        rate_limit_per_user: int | None | UndefinedType = UNDEFINED,
        global_priority: int = 0
    ) -> ChannelData:
        """Starts a thread without a message

        Read the `documentation <https://discord.dev/resources/channel#start-thread-without-message>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The channel to create the thread in.
        name:
            The name of the thread.

            .. note::
                This has to be between 1-100 characters long.
        auto_archive_duration:
            The time to automatically archive the thread after no activity.
        rate_limit_per_user:
            The time every member has to wait before sending another message

            .. note::
                This has to be between 0 and 21600.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        :class:`ChannelData`
            The channel data.
        """
        route = Route(
            "POST",
            "/channels/{channel_id}/threads",
            channel_id=channel_id,
        )

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        payload = {
            "name": name,
        }

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if auto_archive_duration is not UNDEFINED:
            payload["auto_archive_duration"] = auto_archive_duration
        if thread_type is not UNDEFINED:
            payload["type"] = thread_type
        if invitable is not UNDEFINED:
            payload["invitable"] = invitable
        if rate_limit_per_user is not UNDEFINED:
            payload["rate_limit_per_user"] = rate_limit_per_user

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, json=payload, global_priority=global_priority)

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Add start thread in forum channel here!

    async def join_thread(self, authentication: BotAuthentication, channel_id: str | int, *, global_priority: int = 0) -> None:
        """Joins a thread.

        Read the `documentation <https://discord.dev/resources/channel#join-thread>`__

        Parameters
        -----------
        authentication:
            Authentication info.
        channel_id:
            The thread to join.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("PUT", "/channels/{channel_id}/thread-members/@me", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority)

    async def add_thread_member(
        self, authentication: BotAuthentication, channel_id: str | int, user_id: str | int, *, global_priority: int = 0
    ) -> None:
        """Adds a member to a thread

        .. note::
            This will dispatch a ``THREAD_MEMBERS_UPDATE`` event.

        Parameters
        ----------
        authentication:
            The auth info.
        channel_id:
            The thread to add the member to.
        user_id:
            The id of the member to add.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("PUT", "/channels/{channel_id}/thread-members/{user_id}", channel_id=channel_id, user_id=user_id)

        await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers={"Authorization": str(authentication)}, global_priority=global_priority
        )

    async def leave_thread(self, authentication: BotAuthentication, channel_id: str | int, *, global_priority: int = 0) -> None:
        """Leaves a thread

        .. note::
            This will dispatch a ``THREAD_MEMBERS_UPDATE`` event.

        Parameters
        ----------
        authentication:
            The auth info.
        channel_id:
            The channel to leave
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("DELETE", "/channels/{channel_id}/thread-members/@me", channel_id=channel_id)

        await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers={"Authorization": str(authentication)}, global_priority=global_priority
        )

    async def remove_thread_member(
        self, authentication: BotAuthentication, channel_id: str | int, user_id: str | int, *, global_priority: int = 0
    ) -> None:
        """Removes a member from a thread

        .. note::
            This will dispatch a ``THREAD_MEMBERS_UPDATE`` event.

        .. note::
            This requires the ``MANAGE_THREADS`` permission.

            You can also be the owner of the thread if it is a private thread.

        Parameters
        ----------
        authentication:
            The auth info.
        channel_id:
            The thread to add the member to.
        user_id:
            The id of the member to add.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "DELETE", "/channels/{channel_id}/thread-members/{user_id}", channel_id=channel_id, user_id=user_id
        )

        await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers={"Authorization": str(authentication)}, global_priority=global_priority
        )

    async def get_thread_member(
        self, authentication: BotAuthentication, channel_id: str | int, user_id: str | int, *, global_priority: int = 0
    ) -> ThreadMemberData:
        """Gets a thread member.

        Parameters
        ----------
        authentication:
            The auth info.
        channel_id:
            The thread to get from
        user_id:
            The member to get info from.
        global_priority:
            The priority of the request for the global rate-limiter.

        Raises
        ------
        :exc:`NotFoundError`
            The member is not part of the thread.
        """
        route = Route("GET", "/channels/{channel_id}/thread-members/{user_id}", channel_id=channel_id, user_id=user_id)

        r = await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers={"Authorization": str(authentication)}, global_priority=global_priority
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def list_thread_members(self, authentication: BotAuthentication, channel_id: str | int, *, global_priority: int = 0) -> list[ThreadMemberData]:
        """Gets all thread members

        .. warning::
            You need the ``GUILD_MEMBERS`` privileged intent!

        Parameters
        ----------
        authentication:
            The auth info.
        channel_id:
            The thread to get members from.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("GET", "/channels/{channel_id}/thread-members", channel_id=channel_id)

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers={"Authorization": str(authentication)}, global_priority=global_priority)

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

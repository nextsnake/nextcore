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
from ..common import Dispatcher, Undefined, UndefinedType, json_dumps
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
    from typing import Any, Iterable, Literal

    from aiohttp import ClientResponse, ClientWebSocketResponse
    from discord_typings import (
        ActionRowData,
        AllowedMentionsData,
        AttachmentData,
        AuditLogData,
        ChannelData,
        EmbedData,
        GetGatewayBotData,
        GetGatewayData,
        InviteData,
        InviteMetadata,
        MessageData,
        MessageReferenceData,
        ThreadChannelData,
        UserData,
    )
    from discord_typings.resources.audit_log import AuditLogEvents

    from .authentication import BearerAuthentication, BotAuthentication
    from .file import File

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

    Attributes
    ----------
    trust_local_time: :class:`bool`
        If this is enabled, the ratelimiter will use the local time instead of the discord provided time. This may improve your bot's speed slightly.

        .. warning::
            If your time is not correct, and this is set to :data:`True`, this may result in more ratelimits being hit.
    timeout: :class:`float`
        The default request timeout in seconds.
    default_headers: dict[:class:`str`, :class:`str`]
        The default headers to pass to every request.
    max_retries: :class:`int`
        How many times to attempt to retry a request after ratelimiting failed.

        .. note::
            This does not retry server errors.
    ratelimit_storages: dict[:class:`int`, :class:`RatelimitStorage`]
        Classes to store ratelimit information.

        The key here is the ratelimit_key (often a user ID).
    dispatcher: :class:`Dispatcher`
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
        self, route: Route, ratelimit_key: str | None, *, headers: dict[str, str] | None = None, **kwargs: Any
    ) -> ClientResponse:
        """Requests a route from the Discord API

        Parameters
        ----------
        route: :class:`Route`
            The route to request
        ratelimit_key: :class:`str` | :data:`None`
            A ID used for differentiating ratelimits.
            This should be a bot or oauth2 token.

            .. note::
                This should be :data:`None` for unauthenticated routes or webhooks (does not include modifying the webhook via a bot).
        headers: :class:`dict[str, str]`
            Headers to mix with :attr:`HTTPClient.default_headers` to pass to :meth:`aiohttp.ClientSession.request`
        kwargs: :data:`typing.Any`
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
                await self.dispatcher.dispatch("request_response", response)

                # Handle ratelimit errors
                if response.status == 429:
                    # Cloudflare ban check
                    if "via" not in response.headers:
                        raise CloudflareBanError()

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
                        raise HTTPRequestStatusError(error, response)
                else:
                    # Should be in 0-200 range
                    return response
        # This should always be set as it has to pass through the loop atleast once.
        raise RateLimitingFailedError(self.max_retries, response)  # pyright: ignore [reportUnboundVariable]

    async def ws_connect(self, url: str, **kwargs: Any) -> ClientWebSocketResponse:
        """Connects to a websocket.

        Example usage:

        .. code-block:: python

            ws = await http_client.ws_connect("wss://gateway.discord.gg")


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
    async def get_gateway(self) -> GetGatewayData:
        """Gets gateway connection info.
        See the `documentation <https://discord.dev/topics/gateway#get-gateway>`__ for more info.

        Example usage:

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

    async def get_gateway_bot(self, authentication: BotAuthentication) -> GetGatewayBotData:
        """Gets gateway connection information.
        See the `documentation <https://discord.dev/topics/gateway#gateway-get-gateway-bot>`__

        Example usage:

        .. code-block:: python

            bot_info = await http_client.get_gateway_bot(token)

        .. note::
            This endpoint requires a bot token.

        Parameters
        ----------
        authentication: :class:`BotAuthentication`
            Authentication info.

        Returns
        -------
        :class:`dict`
            Gateway connection info.

            .. hint::
                A list of fields are available in the documentation.
        """
        route = Route("GET", "/gateway/bot")
        r = await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers={"Authorization": str(authentication)}
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
    ) -> AuditLogData:
        """Gets the guild audit log.
        See the `documentation <https://discord.dev/resources/audit-log#get-guild-audit-log>`__

        .. note::
            This requires the ``VIEW_AUDIT_LOG`` permission.

        Parameters
        ----------
        authentication: :class:`BotAuthentication`
            Authentication info.
        guild_id: :class:`int`
            The guild to query the audit log for.
        user_id: :class:`int` | :data:`None`
            The user to filter the audit log by.

            This will be the user that did the action if present, if not it will be the user that got actioned.

            If this is :data:`None` this will not filter.
        action_type: :class:`AuditLogEvents` | :data:`None`
            The action type to filter the audit log by.

            If this is :data:`None` this will not filter.
        before: :class:`int` | :data:`None`
            Get entries before this entry.

            .. note::
                This does not have to be a valid entry id.
        limit: :class:`int`
            The amount of entries to get.

            This has a minimum of 1 and a maximum of 100.

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
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # Channel
    async def get_channel(self, authentication: BotAuthentication, channel_id: str | int) -> ChannelData:
        """Gets a channel by ID.
        See the `documentation <https://discord.dev/resources/channels#get-channel>`__

        Parameters
        ----------
        authentication: :class:`BotAuthentication`
            Authentication info.
        channel_id: :class:`int`
            The channel ID to get.

        Returns
        -------
        :class:`ChannelData`
            The channel.

            .. hint::
                A list of fields are available in the documentation.
        """
        route = Route("GET", "/channels/{channel_id}", channel_id=channel_id)
        r = await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers={"Authorization": str(authentication)}
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # These 3 requests are 1 route but are split up for convinience
    async def modify_group_dm(
        self,
        authentication: BearerAuthentication,
        channel_id: str | int,
        *,
        name: str | UndefinedType = Undefined,
        icon: str | None | UndefinedType = Undefined,
        reason: str | UndefinedType = Undefined,
    ) -> ChannelData:
        """Modifies the group dm.

        See the `docoumentation <https://discord.dev/resources/channel#modify-channel>`__

        .. warning::
            This shares ratelimits with :attr:`HTTPClient.modify_guild_channel` and :attr:`HTTPClient.modify_thread`.

        Parameters
        ----------
        authentication: :class:`BearerAuthentication`
            Authentication info.
        channel_id: :class:`str` | :class:`int`
            The id of the group dm channel to update
        name: :class:`str` | :class:`UndefinedType`
            The name of the group dm.

            .. note::
                This has to be between 1 to 100 characters long.
        icon: :class:`str` | :class:`UndefinedType`
            A base64 encoded image of what to change the group dm icon to.
        reason: :class:`str` | :class:`UndefinedType`
            A reason for the audit log.

            .. note::
                This has to be between 1 and 512 characters
        """
        route = Route("PATCH", "/channels/{channel_id}", channel_id=channel_id)
        payload = {}  # TODO: Use a typehint for payload

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if not isinstance(name, UndefinedType):
            payload["name"] = name

        if not isinstance(icon, UndefinedType):
            payload["icon"] = icon

        headers = {"Authorization": str(authentication)}

        if not isinstance(reason, UndefinedType):
            headers["reason"] = reason

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, json=payload)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_guild_channel(
        self,
        authentication: BearerAuthentication,
        channel_id: str | int,
        *,
        name: str | UndefinedType = Undefined,
        channel_type: Literal[0, 5] | UndefinedType = Undefined,
        position: int | None | UndefinedType = Undefined,
        topic: str | None | UndefinedType = Undefined,
        nsfw: bool | None | UndefinedType = Undefined,
        rate_limit_per_user: int | None | UndefinedType = Undefined,
        bitrate: int | None | UndefinedType = Undefined,
        user_limit: int | None | UndefinedType = Undefined,
        permission_overwrites: list[dict[Any, Any]] | None | UndefinedType = Undefined,  # TODO: implement a partial
        parent_id: int | str | UndefinedType = Undefined,
        rtc_region: str | None | UndefinedType = Undefined,
        video_quality_mode: Literal[1, 2] | None | UndefinedType = Undefined,  # TODO: Implement VideoQualityMode
        default_auto_archive_duration: Literal[60, 1440, 4320, 10080] | None | UndefinedType = Undefined,
        reason: str | UndefinedType = Undefined,
    ) -> ChannelData:
        """Modifies a guild channel.

        See the `docoumentation <https://discord.dev/resources/channel#modify-channel>`__


        .. warning::
            This shares ratelimits with :attr:`HTTPClient.modify_group_dm` and :attr:`HTTPClient.modify_thread`.

        Parameters
        ----------
        authentication: :class:`BotAuthentication`
            Authentication info.
        channel_id: :class:`str` | :class:`int`
            The id of the channel to update.
        name: :class:`str` | :class:`UndefinedType`
            The name of the channel.
        channel_type: Literal[0, 5] | :class:`UndefinedType`
            The type of the channel.

            .. note::
                This is named ``type`` in the API, however to not overwrite the type function in python this is changed here.
        position: :class:`int` | :data:`None` | :class:`UndefinedType`
            The position of the channel.

            .. note::
                If this is set to :data:`None` it will default to ``0``.
        topic: :class:`str` | :data:`None` | :class:`UndefinedType`
            The channel topic.
        nsfw: :class:`bool` | :data:`None` | :class:`UndefinedType`
            Whether the channel marked as age restricted.

            .. note::
                If this is set to :data:`None` it will default to :data:`False`.
        rate_limit_per_user: :class:`int` | :data:`None` | :class:`UndefinedType`
            How many seconds a user has to wait before sending another message or create a thread.

            Bots, as well as users with the ``manage_messages`` or ``manage_channel`` are unaffected
            A member can send one message and create one thread per period.

            .. note::
                This has to be between 0-21600 seconds.
        bitrate: :class:`int` | :data:`None` | :class:`UndefinedType`
            The bitrate of the channel in bits per second.

            .. note::
                This only works for stage / voice channels.
            .. note::
                This has to be between 8000-96000 for guilds without the ``VIP_REGIONS`` feature.

                For guilds with the ``VIP_REGIONS`` feature this has to be between 8000-128000.
        user_limit: :class:`int` | :data:`None` | :class:`UndefinedType`
            The maximum amount of users that can be in a voice channel at a time.
        permission_overwrites: list[:class:`discord_typings.PartialPermissionOverwriteData`] | :data:`None` | :class:`UndefinedType`
            The permission overwrites for the channel.

            .. note::
                If this is set to :data:`None` it will default to an empty list.
        parent_id: :class:`int` | :class:`str` | :class:`UndefinedType`
            The id of the parent channel.

            This can be a text channel for threads or a category channel.
        rtc_region: :class:`str` | :data:`None` | :class:`UndefinedType`
            The voice region of the channel.

            .. note::
                If this is :data:`None` it is automatic. Every time someone joins a empty channel, the closest region will be used.
        video_quality_mode: Literal[1, 2] | :data:`None` | :class:`UndefinedType`
            The video quality mode of the channel.

            .. note::
                If this is :data:`None` it will not be present in the Guild payload.

                This is rougly the same as setting it to ``1``.
        default_auto_archive_duration: Literal[60, 1440, 4320, 10080] | :data:`None` | :class:`UndefinedType`
            The default auto archive duration for threads created in this channel.

            .. note::
                If this is :data:`None` it will not be present in the Guild payload.

                The client treats this as it being set to 24 hours however this may change without notice.
        reason: :class:`str` | :class:`UndefinedType`
            The reason to put in the audit log.
        """

        route = Route("PATCH", "/channels/{channel_id}", channel_id=channel_id)
        payload = {}  # TODO: Use a typehint for payload

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if not isinstance(name, UndefinedType):
            payload["name"] = name
        if not isinstance(channel_type, UndefinedType):
            payload["type"] = channel_type
        if not isinstance(position, UndefinedType):
            payload["position"] = position
        if not isinstance(topic, UndefinedType):
            payload["topic"] = topic
        if not isinstance(nsfw, UndefinedType):
            payload["nsfw"] = nsfw
        if not isinstance(rate_limit_per_user, UndefinedType):
            payload["rate_limit_per_user"] = rate_limit_per_user
        if not isinstance(bitrate, UndefinedType):
            payload["bitrate"] = bitrate
        if not isinstance(user_limit, UndefinedType):
            payload["user_limit"] = user_limit
        if not isinstance(permission_overwrites, UndefinedType):
            payload["permission_overwrites"] = permission_overwrites
        if not isinstance(parent_id, UndefinedType):
            payload["parent_id"] = parent_id
        if not isinstance(rtc_region, UndefinedType):
            payload["rtc_region"] = rtc_region
        if not isinstance(video_quality_mode, UndefinedType):
            payload["video_quality_mode"] = video_quality_mode
        if not isinstance(default_auto_archive_duration, UndefinedType):
            payload["default_auto_archive_duration"] = default_auto_archive_duration

        headers = {"Authorization": str(authentication)}

        if not isinstance(reason, UndefinedType):
            headers["reason"] = reason

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, json=payload)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_thread(
        self,
        authentication: BotAuthentication,
        thread_id: int | str,
        *,
        name: str | UndefinedType = Undefined,
        archived: bool | UndefinedType = Undefined,
        auto_archive_duration: Literal[60, 1440, 4320, 10080] | UndefinedType = Undefined,
        locked: bool | UndefinedType = Undefined,
        invitable: bool | UndefinedType = Undefined,
        rate_limit_per_user: int | UndefinedType = Undefined,
        reason: str | UndefinedType = Undefined,
    ) -> ThreadChannelData:
        """Modifies a thread.

        See the `docoumentation <https://discord.dev/resources/channel#modify-channel>`__

        .. warning::
            This shares ratelimits with :attr:`HTTPClient.modify_group_dm` and :attr:`HTTPClient.modify_guild_channel`.

        Parameters
        ----------
        authentication: :class:`BotAuthentication`
            Authentication info.
        thread_id: :class:`str` | :class:`int`
            The id of the thread to update.
        name: :class:`str` | :class:`UndefinedType`
            The name of the thread.
        archived: :class:`bool` | :class:`UndefinedType`
            Whether the thread is archived.
        auto_archive_duration: Literal[60, 1440, 4320, 10080] | :class:`UndefinedType`
            How long in minutes to automatically archive the thread after recent activity
        locked: :class:`bool` | :class:`UndefinedType`
            Whether the thread can only be un-archived by members with the ``manage_threads`` permission.
        invitable: :class:`bool` | :class:`UndefinedType`
            Whether members without the ``manage_threads`` permission can invite members without the ``manage_channels`` permission to the thread.
        rate_limit_per_user: :class:`int` | :data:`None` | :class:`UndefinedType`
            The duration in seconds that a user must wait before sending another message to the thread.

            Bots, as well as users with the ``manage_messages`` or ``manage_channel`` are unaffected

            .. note::
                This has to be between 0-21600 seconds.
        reason: :class:`str` | :class:`UndefinedType`
            The reason to put in the audit log.
        """

        route = Route("PATCH", "/channels/{channel_id}", channel_id=thread_id)
        payload = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if not isinstance(name, UndefinedType):
            payload["name"] = name
        if not isinstance(archived, UndefinedType):
            payload["archived"] = archived
        if not isinstance(auto_archive_duration, UndefinedType):
            payload["auto_archive_duration"] = auto_archive_duration
        if not isinstance(locked, UndefinedType):
            payload["locked"] = locked
        if not isinstance(invitable, UndefinedType):
            payload["invitable"] = invitable
        if not isinstance(rate_limit_per_user, UndefinedType):
            payload["rate_limit_per_user"] = rate_limit_per_user

        headers = {"Authorization": str(authentication)}

        if not isinstance(reason, UndefinedType):
            headers["reason"] = reason

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, json=payload)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_channel(
        self, authentication: BotAuthentication | BearerAuthentication, channel_id: int | str
    ) -> None:
        """Deletes a channel.

        Parameters
        ----------
        authentication: :class:`BotAuthentication` | :class:`BearerAuthentication`
            Authentication info.
        channel_id: :class:`str` | :class:`int`
            The id of the channel to delete.
        """

        route = Route("DELETE", "/channels/{channel_id}", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}

        await self._request(route, headers=headers, ratelimit_key=authentication.rate_limit_key)

    @overload
    async def get_channel_messages(
        self, authentication: BotAuthentication, channel_id: int | str, *, around: int, limit: int | UndefinedType
    ) -> list[MessageData]:
        ...

    @overload
    async def get_channel_messages(
        self, authentication: BotAuthentication, channel_id: int | str, *, before: int, limit: int | UndefinedType
    ) -> list[MessageData]:
        ...

    @overload
    async def get_channel_messages(
        self, authentication: BotAuthentication, channel_id: int | str, *, after: int, limit: int | UndefinedType
    ) -> list[MessageData]:
        ...

    @overload
    async def get_channel_messages(self, authentication: BotAuthentication, channel_id: int | str) -> list[MessageData]:
        ...

    async def get_channel_messages(
        self,
        authentication: BotAuthentication,
        channel_id: int | str,
        *,
        around: int | UndefinedType = Undefined,
        before: int | UndefinedType = Undefined,
        after: int | UndefinedType = Undefined,
        limit: int | UndefinedType = Undefined,
    ) -> list[MessageData]:
        """Gets messages from a channel.

        See the `documentation <https://discord.dev/resources/channel#get-channel-messages>`__

        .. note::
            This requires the ``view_channel`` permission..

        .. note::
            If the ``read_message_history`` permission is not given, this will return an empty list.

        Parameters
        ----------
        authentication: :class:`BotAuthentication`
            Authentication info.
        channel_id: :class:`str` | :class:`int`
            The id of the channel to get messages from.
        around: :class:`int` | :class:`UndefinedType`
            The id of the message to get messages around.

            .. note::
                This does not have to be a valid message id.
        before: :class:`int` | :class:`UndefinedType`
            The id of the message to get messages before.

            .. note::
                This does not have to be a valid message id.
        after: :class:`int` | :class:`UndefinedType`
            The id of the message to get messages after.

            .. note::
                This does not have to be a valid message id.
        limit: :class:`int`
            The number of messages to get.

            .. note::
                This has to be between 1-100.
            .. note::
                If this is not provided it will default to ``50``.
        """

        route = Route("GET", "/channels/{channel_id}/messages", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}

        params = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if not isinstance(around, UndefinedType):
            params["around"] = around
        if not isinstance(before, UndefinedType):
            params["before"] = before
        if not isinstance(after, UndefinedType):
            params["after"] = after
        if not isinstance(limit, UndefinedType):
            params["limit"] = limit

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, params=params)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def create_message(
        self,
        authentication: BotAuthentication,
        channel_id: int | str,
        *,
        content: str | UndefinedType = Undefined,
        tts: bool | UndefinedType = Undefined,
        embeds: list[EmbedData] | UndefinedType = Undefined,
        allowed_mentions: AllowedMentionsData | UndefinedType = Undefined,
        message_reference: MessageReferenceData | UndefinedType = Undefined,
        componenets: list[ActionRowData] | UndefinedType = Undefined,
        sticker_ids: list[int] | UndefinedType = Undefined,
        files: Iterable[File] | UndefinedType = Undefined,
        attachments: list[AttachmentData] | UndefinedType = Undefined,  # TODO: Partial
        flags: int | UndefinedType = Undefined,
    ) -> MessageData:
        """Creates a message in a channel.

        See the `documentation <https://discord.dev/resources/channel#create-message>`__

        .. note::
            This requires the ``view_channel`` and ``send_messages`` permission.

        Parameters
        ----------
        authentication: :class:`BotAuthentication`
            Authentication info.
        channel_id: :class:`str` | :class:`int`
            The id of the channel to create a message in.
        content: :class:`str` | :class:`UndefinedType`
            The content of the message.
        tts: :class:`bool`
            Whether the ``content`` should be spoken out by the Discord client upon send.

            .. note::
                This will still set ``Message.tts`` to :data:`True` even if ``content`` is not provided.
        embeds: list[:class:`discord_typings.EmbedData`] | :class:`UndefinedType`
            The embeds to send with the message.

            .. hint::
                The fields are in the `Embed <https://discord.dev/resources/channel#embed-object>`__ documentation.

            .. note::
                There is a maximum 6,000 character limit across all embeds.

                See the `embed limits documentation <https://discord.dev/resources/channel#embed-object-embed-limits>`__ for more info.
        allowed_mentions: :class:`discord_typings.AllowedMentionsData` | :class:`UndefinedType`
            The allowed mentions for the message.
        message_reference: :class:`discord_typings.MessageReferenceData` | :class:`UndefinedType`
            The message to reply to.
        componenets: list[:class:`discord_typings.ActionRowData`] | :class:`UndefinedType`
            The components to send with the message.
        sticker_ids: list[:class:`int`] | :class:`UndefinedType`
            A list of sticker ids to attach to the message.

            .. note::
                This has a max of 3 stickers.
        files: :class:`Iterable[:class:`discord_typings.File`]` | :class:`UndefinedType`
            The files to send with the message.
        attachments: list[:class:`discord_typings.CreateMessagePartialAttachmentData`] | :class:`UndefinedType`
            Metadata about the ``files`` parameter.

            .. note::
                This only includes the ``filename`` and ``description`` fields.
        flags: :class:`int` | :class:`UndefinedType`
            Bitwise flags to send with the message.

            .. note::
                Only the ``SUPRESS_EMBEDS`` flag can be set.

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
        if not isinstance(content, UndefinedType):
            payload["content"] = content
        if not isinstance(tts, UndefinedType):
            payload["tts"] = tts
        if not isinstance(embeds, UndefinedType):
            payload["embeds"] = embeds
        if not isinstance(allowed_mentions, UndefinedType):
            payload["allowed_mentions"] = allowed_mentions
        if not isinstance(message_reference, UndefinedType):
            payload["message_reference"] = message_reference
        if not isinstance(componenets, UndefinedType):
            payload["componenets"] = componenets
        if not isinstance(sticker_ids, UndefinedType):
            payload["sticker_ids"] = sticker_ids
        if not isinstance(attachments, UndefinedType):
            payload["attachments"] = attachments
        if not isinstance(flags, UndefinedType):
            payload["flags"] = flags

        # Create a form data response as files cannot be uploaded via json.
        form = FormData()
        form.add_field("payload_json", json_dumps(payload))

        # Add files
        if not isinstance(files, UndefinedType):
            for file_id, file in enumerate(files):
                # Content type seems to have no effect here.
                form.add_field(f"file[{file_id}]", file.contents, filename=file.name)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            data=form,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def crosspost_message(
        self, authentication: BotAuthentication, channel_id: int | str, message_id: int | str
    ) -> MessageData:
        """Crossposts a message from another channel.

        See the `documentation <https://discord.dev/resources/channel#crosspost-message>`__

        .. note::
            This requires the ``send_messages`` permission when trying to crosspost a message sent by the current user.

            If not this requires the ``manage_messages`` permission.

        Parameters
        ----------
        authentication: :class:`BotAuthentication`
            Authentication info.
        channel_id: :class:`str` | :class:`int`
            The id of the channel to crosspost the message to.
        message_id: :class:`str` | :class:`int`
            The id of the message to crosspost.

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

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def create_reaction(
        self, authentication: BotAuthentication, channel_id: int | str, message_id: int | str, emoji: str
    ) -> None:
        """Creates a reaction to a message.

        See the `documentation <https://discord.dev/resources/channel#create-reaction>`__

        .. note::
            This requires the ``read_message_history`` permission.

            This also requires the ``add_reactions`` permission if noone else has reacted to the message with this emoji.

        Parameters
        ----------
        authentication: :class:`BotAuthentication`
            Authentication info.
        channel_id: :class:`str` | :class:`int`
            The id of the channel where the message is located.
        message_id: :class:`str` | :class:`int`
            The id of the message to add a reaction to.
        emoji: :class:`str`
            The emoji to add to the message.

            This is either a unicode emoji or a custom emoji in the format ``name:id``.
        """
        route = Route(
            "PUT",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
            channel_id=channel_id,
            message_id=message_id,
            emoji=quote(emoji),
        )
        headers = {"Authorization": str(authentication)}

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers)

    async def delete_own_reaction(
        self, authentication: BotAuthentication, channel_id: int | str, message_id: int | str, emoji: str
    ) -> None:
        """Deletes a reaction from a message.

        See the `documentation <https://discord.dev/resources/channel#delete-own-reaction>`__

        Parameters
        ----------
        authentication: :class:`BotAuthentication`
            Authentication info.
        channel_id: :class:`str` | :class:`int`
            The id of the channel where the message is located.
        message_id: :class:`str` | :class:`int`
            The id of the message to remove a reaction from.
        emoji: :class:`str`
            The emoji to remove from the message.

            This is either a unicode emoji or a custom emoji in the format ``name:id``.
        """
        route = Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
            channel_id=channel_id,
            message_id=message_id,
            emoji=quote(emoji),
        )
        headers = {"Authorization": str(authentication)}

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers)

    async def delete_user_reaction(
        self,
        authentication: BotAuthentication,
        channel_id: int | str,
        message_id: int | str,
        emoji: str,
        user_id: int | str,
    ) -> None:
        """Deletes a reaction from a message from another user.

        See the `documentation <https://discord.dev/resources/channel#delete-user-reaction>`__

        .. note::
            This requires the ``manage_messages`` permission.

        .. note::
            This does not error when attempting to remove a reaction that does not exist.

        Parameters
        ----------
        authentication: :class:`BotAuthentication`
            Authentication info.
        channel_id: :class:`str` | :class:`int`
            The id of the channel where the message is located.
        message_id: :class:`str` | :class:`int`
            The id of the message to remove a reaction from.
        emoji: :class:`str`
            The emoji to remove from the message.

            This is either a unicode emoji or a custom emoji in the format ``name:id``.
        user_id: :class:`str` | :class:`int`
            The id of the user to remove the reaction from.
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

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers)

    async def get_reactions(
        self,
        authentication: BotAuthentication,
        channel_id: int | str,
        message_id: int | str,
        emoji: str,
        *,
        after: str | int | UndefinedType = Undefined,
        limit: int | UndefinedType = Undefined,
    ) -> list[UserData]:
        """Gets the reactions to a message.

        See the `documentation <https://discord.dev/resources/channel#get-reactions>`__

        .. note::
            This requires the ``read_message_history`` permission.

        Parameters
        ----------
        authentication: :class:`BotAuthentication`
            Authentication info.
        channel_id: :class:`str` | :class:`int`
            The id of the channel where the message is located.
        message_id: :class:`str` | :class:`int`
            The id of the message to get the reactions from.

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
        if not isinstance(after, UndefinedType):
            params["after"] = after
        if not isinstance(limit, UndefinedType):
            params["limit"] = limit

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, params=params)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_all_reactions(
        self, authentication: BotAuthentication, channel_id: int | str, message_id: int | str
    ) -> None:
        """Deletes all reactions from a message.

        See the `documentation <https://discord.dev/resources/channel#delete-all-reactions>`__

        .. note::
            This requires the ``manage_messages`` permission.

        .. note::
            This will cause a ``MESSAGE_REACTION_REMOVE_ALL`` dispatch event.

        Parameters
        ----------
        authentication: :class:`BotAuthentication`
            Authentication info.
        channel_id: :class:`str` | :class:`int`
            The id of the channel where the message is located.
        message_id: :class:`str` | :class:`int`
            The id of the message to remove all reactions from.
        """
        route = Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions",
            channel_id=channel_id,
            message_id=message_id,
        )
        headers = {"Authorization": str(authentication)}

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers)

    async def delete_all_reactions_for_emoji(
        self, authentication: BotAuthentication, channel_id: int | str, message_id: int | str, emoji: str
    ) -> None:
        """Deletes all reactions from a message with a specific emoji.

        See the `documentation <https://discord.dev/resources/channel#delete-all-reactions-for-emoji>`__

        .. note::
            This requires the ``manage_messages`` permission.

        .. note::
            This will cause a ``MESSAGE_REACTION_REMOVE_EMOJI`` dispatch event.

        Parameters
        ----------
        authentication: :class:`BotAuthentication`
            Authentication info.
        channel_id: :class:`str` | :class:`int`
            The id of the channel where the message is located.
        message_id: :class:`str` | :class:`int`
            The id of the message to remove all reactions from.
        emoji: :class:`str`
            The emoji to remove from the message.

            This is either a unicode emoji or a custom emoji in the format ``name:id``.
        """
        route = Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}",
            channel_id=channel_id,
            message_id=message_id,
            emoji=quote(emoji),
        )
        headers = {"Authorization": str(authentication)}

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers)

    async def edit_message(
        self,
        authentication: BotAuthentication,
        channel_id: int | str,
        message_id: int | str,
        *,
        content: str | None | UndefinedType = Undefined,
        embeds: list[EmbedData] | None | UndefinedType = Undefined,
        flags: int | None | UndefinedType = Undefined,
        allowed_mentions: AllowedMentionsData | None | UndefinedType = Undefined,
        components: list[ActionRowData] | None | UndefinedType = Undefined,
        files: list[File] | None | UndefinedType = Undefined,
        attachments: list[AttachmentData] | None | UndefinedType = Undefined,  # TODO: Partial
    ) -> MessageData:
        """Edits a message.

        See the `documentation <https://discord.dev/resources/channel#edit-message>`__

        .. note::
            This requires the ``manage_messages`` permission.

        Parameters
        ----------
        authentication: :class:`BotAuthentication`
            Authentication info.
        channel_id: :class:`str` | :class:`int`
            The id of the channel where the message is located.
        message_id: :class:`str` | :class:`int`
            The id of the message to edit.
        content: :class:`str` | :class:`None` | :class:`UndefinedType`
            The new content of the message.

            .. note::
                If this is set to ``None``, there will be no message contents.

            .. note::
                Adding/removing mentions will not affect mentions.
        embeds: :class:`list[:class:`EmbedData`]` | :data:`None` | :class:`UndefinedType`
            The new embeds of the message.

            This overwrites the previous embeds
        flags: :class:`int` | :class:`None` | :class:`UndefinedType`
            The new flags of the message.

            .. warning::
                Only the ``SUPPRESS_EMBEDS`` flag can be set. Trying to set other flags will be ignored.
        allowed_mentions: :class:`AllowedMentionsData` | :class:`None` | :class:`UndefinedType`
            The new allowed mentions of the message.

            .. note::
                Setting this to ``None`` will make it use the default allowed mentions.
        components: :class:`list[:class:`ActionRowData`]` | :class:`None` | :class:`UndefinedType`
            The new components of the message.
        files: list[:class:`File`] | :class:`None` | :class:`UndefinedType`
            The new files of the message.
        attachments: list[:class:`AttachmentData`] | :class:`None` | :class:`UndefinedType`
            The new attachments of the message.

            .. warning::
                This has to include previous and current attachments or they will be removed.

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
        if not isinstance(content, UndefinedType):
            payload["content"] = content
        if not isinstance(embeds, UndefinedType):
            payload["embeds"] = embeds
        if not isinstance(flags, UndefinedType):
            payload["flags"] = flags
        if not isinstance(allowed_mentions, UndefinedType):
            payload["allowed_mentions"] = allowed_mentions
        if not isinstance(components, UndefinedType):
            payload["components"] = components
        if not isinstance(attachments, UndefinedType):
            payload["attachments"] = attachments

        # This is a special case where we need to send the files as a multipart form
        form = FormData()
        if not isinstance(files, UndefinedType):
            if files is None:
                raise NotImplementedError("What is this even supposed to do?")
            for file in files:
                form.add_field("file", file.contents, filename=file.name)

        form.add_field("payload_json", json_dumps(payload))

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, data=form)

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def delete_message(
        self,
        authentication: BotAuthentication,
        channel_id: str | int,
        message_id: str | int,
        *,
        reason: str | UndefinedType = Undefined,
    ) -> None:
        """Deletes a message.

        See the `documentation <https://discord.dev/resources/channel#delete-message>`__

        .. note::
            This requires the ``manage_messages`` permission.

        .. note::
            This will cause a ``MESSAGE_DELETE`` dispatch event.

        Parameters
        ----------
        authentication: :class:`BotAuthentication`
            Authentication info.
        channel_id: :class:`str` | :class:`int`
            The id of the channel where the message is located.
        message_id: :class:`str` | :class:`int`
            The id of the message to delete.
        reason: :class:`str` | :class:`UndefinedType`
            The reason for deleting the message.

            .. note::
                If this is set to ``Undefined``, there will be no reason.
        """
        route = Route(
            "DELETE", "/channels/{channel_id}/messages/{message_id}", channel_id=channel_id, message_id=message_id
        )
        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if not isinstance(reason, UndefinedType):
            headers["X-Audit-Log-Reason"] = reason

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers)

    async def bulk_delete_messages(
        self,
        authentication: BotAuthentication,
        channel_id: str | int,
        messages: list[str] | list[int] | list[str | int],
        *,
        reason: str | UndefinedType = Undefined,
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
        authentication: :class:`BotAuthentication`
            Authentication info.
        channel_id: :class:`str` | :class:`int`
            The id of the channel where the message is located.
        messages: :class:`list[:class:`str` | :class:`int`]`
            The ids of the messages to delete.

            .. note::
                This has to be between 2 and 100 messages.

                Invalid messages still count towards the limit.
        reason: :class:`str` | :class:`UndefinedType`
            The reason for deleting the message.

            .. note::
                If this is set to ``Undefined``, there will be no reason.
        """
        route = Route("POST", "/channels/{channel_id}/messages/bulk-delete", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if not isinstance(reason, UndefinedType):
            headers["X-Audit-Log-Reason"] = reason

        await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers=headers, json={"messages": messages}
        )

    async def edit_channel_permissions(
        self,
        authentication: BotAuthentication,
        channel_id: str | int,
        target_type: Literal[0, 1],
        target_id: str | int,
        *,
        allow: str | None | UndefinedType = Undefined,
        deny: str | None | UndefinedType = Undefined,
        reason: str | UndefinedType = Undefined,
    ) -> None:
        """Edits the permissions of a channel.

        See the `documentation <https://discord.dev/resources/channel#edit-channel-permissions>`__

        .. note::
            This requires the ``manage_roles`` permission.

            This also requires the permissions you want to grant/deny unless your bot has a ``manage_roles`` overwrite.

        Parameters
        ----------
        authentication: :class:`BotAuthentication`
            Authentication info.
        channel_id: :class:`str` | :class:`int`
            The id of the channel to edit.
        target_type: :class:`int`
            The type of the target.

            0: Role
            1: User
        target_id: :class:`str` | :class:`int`
            The id of the target to edit permissions for.
        allow: :class:`str` | :class:`None` | :class:`UndefinedType`
            A bitwise flag of permissions to allow.

            .. note::
                If this is set to :data:`None`, it will default to ``0``.
        deny: :class:`str` | :class:`None` | :class:`UndefinedType`
            A bitwise flag of permissions to allow.

            .. note::
                If this is set to :data:`None`, it will default to ``0``.
        reason: :class:`str` | :class:`UndefinedType`
            The reason to show in audit log

            .. note::
                If this is set to ``Undefined``, there will be no reason.
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
        if not isinstance(allow, UndefinedType):
            payload["allow"] = allow
        if not isinstance(deny, UndefinedType):
            payload["deny"] = deny

        payload["type"] = target_type

        if not isinstance(reason, UndefinedType):
            headers["X-Audit-Log-Reason"] = reason

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, json=payload)

    async def get_channel_invites(
        self, authentication: BotAuthentication, channel_id: str | int
    ) -> list[InviteMetadata]:
        """Gets the invites for a channel.

        See the `documentation <https://discord.dev/resources/channel#get-channel-invites>`__

        .. note::
            This requires the ``manage_channels`` permission.

        Parameters
        ----------
        authentication: :class:`BotAuthentication`
            Authentication info.
        channel_id: :class:`str` | :class:`int`
            The id of the channel to get invites for.

        Returns
        -------
        list[:class:`InviteMetadata`]
            The invites for the channel.
        """
        route = Route("GET", "/channels/{channel_id}/invites", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers)

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    @overload
    async def create_channel_invite(
        self,
        authentication: BotAuthentication,
        channel_id: str | int,
        *,
        max_age: int | UndefinedType = Undefined,
        max_uses: int | UndefinedType = Undefined,
        temporary: bool | UndefinedType = Undefined,
        unique: bool | UndefinedType = Undefined,
        target_type: Literal[0],
        target_user_id: str | int,
        target_application_id: UndefinedType = Undefined,
    ) -> InviteData:
        ...

    @overload
    async def create_channel_invite(
        self,
        authentication: BotAuthentication,
        channel_id: str | int,
        *,
        max_age: int | UndefinedType = Undefined,
        max_uses: int | UndefinedType = Undefined,
        temporary: bool | UndefinedType = Undefined,
        unique: bool | UndefinedType = Undefined,
        target_type: Literal[1],
        target_user_id: UndefinedType = Undefined,
        target_application_id: str | int,
    ) -> InviteData:
        ...

    @overload
    async def create_channel_invite(
        self,
        authentication: BotAuthentication,
        channel_id: str | int,
        *,
        max_age: int | UndefinedType = Undefined,
        max_uses: int | UndefinedType = Undefined,
        temporary: bool | UndefinedType = Undefined,
        unique: bool | UndefinedType = Undefined,
        target_type: UndefinedType = Undefined,
        target_user_id: UndefinedType = Undefined,
        target_application_id: UndefinedType = Undefined,
    ) -> InviteData:
        ...

    async def create_channel_invite(
        self,
        authentication: BotAuthentication,
        channel_id: str | int,
        *,
        max_age: int | UndefinedType = Undefined,
        max_uses: int | UndefinedType = Undefined,
        temporary: bool | UndefinedType = Undefined,
        unique: bool | UndefinedType = Undefined,
        target_type: Literal[0, 1] | UndefinedType = Undefined,
        target_user_id: str | int | UndefinedType = Undefined,
        target_application_id: str | int | UndefinedType = Undefined,
    ) -> InviteData:
        """Creates an invite for a channel.

        Read the `documentation <https://discord.com/developers/docs/resources/channel#create-channel-invite>`__

        Parameters
        -----------
        authentication: :class:`BotAuthentication`
            Authentication info.
        channel_id: :class:`str` | :class:`int`
            The id of the channel to create an invite for.
        max_age: :class:`int` | :class:`UndefinedType`
            How long the invite should last.

            .. note::
                This has to be between 0 and 604800 seconds. (7 days)

                Setting this to ``0`` will make it never expire.
        max_uses: :class:`int` | :class:`UndefinedType`
            How many times the invite can be used before getting deleted.
        temporary: :class:`bool` | :class:`UndefinedType`
            Whether the invite grants temporary membership.

            This will kick members if they havent got a role when logging off.
        unique: :class:`bool` | :class:`UndefinedType`
            Whether discord will make a new invite regardless of existing invites.
        target_type: :class:`int` | :class:`UndefinedType`
            The type of the target.

            0: A user's stream
            1: ``EMBEDDED`` Activity
        target_user_id: :class:`str` | :class:`int` | :class:`UndefinedType`
            The id of the user streaming to invite to.

            .. note::
                This can only be set if ``target_type`` is ``0``.
        target_application_id: :class:`str` | :class:`int` | :class:`UndefinedType`
            The id of the ``EMBEDDED`` activity to play.

            .. note::
                This can only be set if ``target_type`` is ``1``.

        Returns
        -------
        :class:`InviteData`
            The invite data.
        """
        route = Route("POST", "/channels/{channel_id}/invites", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}

        payload = {}

        if not isinstance(max_age, UndefinedType):
            payload["max_age"] = max_age
        if not isinstance(max_uses, UndefinedType):
            payload["max_uses"] = max_uses
        if not isinstance(temporary, UndefinedType):
            payload["temporary"] = temporary
        if not isinstance(unique, UndefinedType):
            payload["unique"] = unique
        if not isinstance(target_type, UndefinedType):
            payload["target_type"] = target_type
        if not isinstance(target_user_id, UndefinedType):
            payload["target_user_id"] = target_user_id
        if not isinstance(target_application_id, UndefinedType):
            payload["target_application_id"] = target_application_id

        r = await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers, json=payload)

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def delete_channel_permission(
        self,
        authentication: BotAuthentication,
        channel_id: str | int,
        target_id: str | int,
        *,
        reason: str | UndefinedType = Undefined,
    ) -> None:
        """Deletes a channel permission.

        Read the `documentation <https://discord.com/developers/docs/resources/channel#delete-channel-permission>`__

        Parameters
        -----------
        authentication: :class:`BotAuthentication`
            Authentication info.
        channel_id: :class:`str` | :class:`int`
            The id of the channel to delete the permission from.
        target_id: :class:`str` | :class:`int`
            The id of the user or role to delete the permission from.
        """
        route = Route(
            "DELETE", "/channels/{channel_id}/permissions/{target_id}", channel_id=channel_id, target_id=target_id
        )
        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if not isinstance(reason, UndefinedType):
            headers["X-Audit-Log-Reason"] = reason

        await self._request(route, ratelimit_key=authentication.rate_limit_key, headers=headers)

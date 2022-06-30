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
from typing import TYPE_CHECKING, overload
from urllib.parse import quote
from warnings import warn

from aiohttp import ClientSession, FormData

from .. import __version__ as nextcore_version
from ..common import UNDEFINED, Dispatcher, UndefinedType, json_dumps
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
        ApplicationCommandData,
        ApplicationCommandOptionData,
        ApplicationCommandPayload,
        ApplicationData,
        AttachmentData,
        AuditLogData,
        BanData,
        ChannelData,
        ChannelPositionData,
        DMChannelData,
        EmbedData,
        EmojiData,
        FollowedChannelData,
        GetGatewayBotData,
        GetGatewayData,
        GuildApplicationCommandPermissionData,
        GuildData,
        GuildMemberData,
        GuildPreviewData,
        GuildScheduledEventData,
        GuildScheduledEventEntityMetadata,
        GuildTemplateData,
        GuildWidgetData,
        GuildWidgetSettingsData,
        HasMoreListThreadsData,
        IntegrationData,
        InviteData,
        InviteMetadata,
        MessageData,
        MessageReferenceData,
        PartialChannelData,
        RoleData,
        RolePositionData,
        StageInstanceData,
        StickerData,
        StickerPackData,
        ThreadChannelData,
        ThreadMemberData,
        UserData,
        VoiceRegionData,
        WebhookData,
        WelcomeChannelData,
        WelcomeScreenData,
    )
    from discord_typings.interactions.commands import Locales
    from discord_typings.resources.audit_log import AuditLogEvents
    from discord_typings.shared import Snowflake

    from ..common.json import JsonCompatible
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
        self,
        route: Route,
        ratelimit_key: str | None,
        *,
        headers: dict[str, str] | None = None,
        global_priority: int = 0,
        **kwargs: Any,
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
        ClientResponse
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
        aiohttp.ClientWebSocketResponse
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
    # Application commands
    async def get_global_application_commands(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        *,
        with_localizations: bool | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> list[ApplicationCommandData]:  # TODO: Narrow typing to never include guild_id and localization overload
        """Gets all global commands

        See the `documentation <https://discord.dev/interactions/application-commands#get-global-application-commands>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[discord_typings.ApplicationCommandData]
            The global commmands registered to the application
        """
        route = Route("GET", "/applications/{application_id}/commands", application_id=application_id)

        query = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if with_localizations is not UNDEFINED:
            query["with_localizations"] = with_localizations

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            query=query,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def create_global_application_command(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        name: str,
        description: str,
        *,
        name_localizations: dict[Locales, str] | None | UndefinedType = UNDEFINED,
        description_localizations: dict[Locales, str] | None | UndefinedType = UNDEFINED,
        options: list[ApplicationCommandOptionData] | UndefinedType = UNDEFINED,
        default_member_permissions: str | None | UndefinedType = UNDEFINED,
        dm_permission: bool | None | UndefinedType = UNDEFINED,
        type: Literal[1, 2, 3] | UndefinedType = UNDEFINED,  # TODO: Replace this with a type alias in discord_typings
        global_priority: int = 0,
    ) -> ApplicationCommandData:  # TODO: Narrow typing to never include guild_id
        """Creates or updates a global application command

        See the `documentation <https://discord.dev/interactions/application-commands#create-global-application-command>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only update commands for your current application
        name:
            The name of the command

            .. note::
                If the name is already taken by a existing application command with the same name and type
                it will update the exisiting command.
            .. note::
                This has to be between 1-32 characters long and follow the `naming conventions <https://discord.dev/interactions/application-commands#application-command-object-application-command-naming>`__
        description:
            The description of the command

            .. note::
                This has to be between 1-100 characters long

            .. warning::
                Some special characters may be automatically removed from this!
        name_localizations:
            The localizations for the name

            .. note::
                This has to be between 1-32 characters long and follow the `naming conventions <https://discord.dev/interactions/application-commands#application-command-object-application-command-naming>`__
        description_localizations:
            The localizations for the description

            .. note::
                This has to be between 1-100 characters long

            .. warning::
                Some special characters may be automatically removed from this!
        options:
            The parameters or sub-commands of the command

            .. note::
                This should only be provide
        default_member_permissions:
            The default permissions to require to use the command
        dm_permission:
            Whether the command can be used in DMs.

            .. note::
                If this is :data:`UNDEFINED`, it defaults to :data:`True`.
        type:
            The type of the command

            .. note::
                This defaults to ``1`` if it is :data:`UNDEFINED`.

            **Possible values**
            - ``1``: Slash/text command
            - ``2``: User context menu
            - ``3``: Message context menu
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.ApplicationCommandData
            The command that was created
        """
        route = Route("POST", "/applications/{application_id}/commands", application_id=application_id)

        payload: JsonCompatible = {"name": name, "description": description}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name_localizations is not UNDEFINED:
            payload["name_localizations"] = name_localizations
        if description_localizations is not UNDEFINED:
            payload["description_localizations"] = description_localizations
        if options is not UNDEFINED:
            payload["options"] = options
        if default_member_permissions is not UNDEFINED:
            payload["default_member_permissions"] = default_member_permissions
        if dm_permission is not UNDEFINED:
            payload["dm_permission"] = dm_permission
        if type is not UNDEFINED:
            payload["type"] = type

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_global_application_command(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        command_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> ApplicationCommandData:  # TODO: Narrow typing to never include guild_id
        """Gets a global command

        See the `documentation <https://discord.dev/interactions/application-commands#get-global-application-command>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        application_id:
            The id of the command to fetch
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.ApplicationCommandData
            The global commmand fetched
        """
        route = Route(
            "GET",
            "/applications/{application_id}/commands/{command_id}",
            application_id=application_id,
            command_id=command_id,
        )

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def edit_global_application_command(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        command_id: Snowflake,
        *,
        name: str | UndefinedType = UNDEFINED,
        name_localizations: dict[Locales, str] | None | UndefinedType = UNDEFINED,
        description: str | UndefinedType = UNDEFINED,
        description_localizations: dict[Locales, str] | None | UndefinedType = UNDEFINED,
        options: list[ApplicationCommandOptionData] | UndefinedType = UNDEFINED,
        default_member_permissions: str | None | UndefinedType = UNDEFINED,
        dm_permission: bool | None | UndefinedType = UNDEFINED,
        type: Literal[1, 2, 3] | UndefinedType = UNDEFINED,  # TODO: Replace this with a type alias in discord_typings
        global_priority: int = 0,
    ) -> ApplicationCommandData:  # TODO: Narrow typing to never include guild_id
        """Updates a global application command

        See the `documentation <https://discord.dev/interactions/application-commands#edit-global-application-command>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only update commands for your current application
        name:
            The name of the command

            .. note::
                If the name is already taken by a existing application command with the same name and type
                it will update the exisiting command.
            .. note::
                This has to be between 1-32 characters long and follow the `naming conventions <https://discord.dev/interactions/application-commands#application-command-object-application-command-naming>`__
        name_localizations:
            The localizations for the name

            .. note::
                This has to be between 1-32 characters long and follow the `naming conventions <https://discord.dev/interactions/application-commands#application-command-object-application-command-naming>`__
        description:
            The description of the command

            .. note::
                This has to be between 1-100 characters long

            .. warning::
                Some special characters may be automatically removed from this!
        description_localizations:
            The localizations for the description

            .. note::
                This has to be between 1-100 characters long

            .. warning::
                Some special characters may be automatically removed from this!
        options:
            The parameters or sub-commands of the command

            .. note::
                This should only be provide
        default_member_permissions:
            The default permissions to require to use the command
        dm_permission:
            Whether the command can be used in DMs.

            .. note::
                If this is :data:`UNDEFINED`, it defaults to :data:`True`.
        type:
            The type of the command

            .. note::
                This defaults to ``1`` if it is :data:`UNDEFINED`.

            **Possible values**
            - ``1``: Slash/text command
            - ``2``: User context menu
            - ``3``: Message context menu
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.ApplicationCommandData
            The command that was edited
        """
        route = Route(
            "PATCH",
            "/applications/{application_id}/commands/{command_id}",
            application_id=application_id,
            command_id=command_id,
        )

        payload: JsonCompatible = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name
        if name_localizations is not UNDEFINED:
            payload["name_localizations"] = name_localizations
        if description is not UNDEFINED:
            payload["description"] = description
        if description_localizations is not UNDEFINED:
            payload["description_localizations"] = description_localizations
        if options is not UNDEFINED:
            payload["options"] = options
        if default_member_permissions is not UNDEFINED:
            payload["default_member_permissions"] = default_member_permissions
        if dm_permission is not UNDEFINED:
            payload["dm_permission"] = dm_permission
        if type is not UNDEFINED:
            payload["type"] = type

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_global_application_command(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        command_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> None:
        """Deletes a global command

        See the `documentation <https://discord.dev/interactions/application-commands#delete-global-application-command>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        application_id:
            The id of the command to fetch
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "GET",
            "/applications/{application_id}/commands/{command_id}",
            application_id=application_id,
            command_id=command_id,
        )

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def bulk_overwrite_global_application_commands(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        *commands: ApplicationCommandPayload,
        global_priority: int = 0,
    ) -> list[ApplicationCommandData]:  # TODO: Narrow typing to never include guild_id
        """Creates or updates a global application command

        See the `documentation <https://discord.dev/interactions/application-commands#bulk-overwrite-global-application-commands>`__

        .. warning::
            This will replace all your global commands. Include the old commands to keep them

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only update commands for your current application
        commands:
            The global commands to overwrite the current global commands with
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[discord_typings.ApplicationCommandData]
            The global commands
        """
        route = Route("PUT", "/applications/{application_id}/commands", application_id=application_id)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            json=commands,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_application_commands(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        guild_id: Snowflake,
        *,
        with_localizations: bool | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> list[
        ApplicationCommandData
    ]:  # TODO: Narrow typing to always include guild_id and localization overload and never dm_permission
        """Gets all commands in a guild

        See the `documentation <https://discord.dev/interactions/application-commands#get-guild-application-commands>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        guild_id:
            The guild to get commands from.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[discord_typings.ApplicationCommandData]
            The commmands registered to the guild
        """
        route = Route(
            "GET",
            "/applications/{application_id}/guilds/{guild_id}commands",
            application_id=application_id,
            guild_id=guild_id,
        )

        query = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if with_localizations is not UNDEFINED:
            query["with_localizations"] = with_localizations

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            query=query,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def create_guild_application_command(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        guild_id: Snowflake,
        name: str,
        description: str,
        *,
        name_localizations: dict[Locales, str] | None | UndefinedType = UNDEFINED,
        description_localizations: dict[Locales, str] | None | UndefinedType = UNDEFINED,
        options: list[ApplicationCommandOptionData] | UndefinedType = UNDEFINED,
        default_member_permissions: str | None | UndefinedType = UNDEFINED,
        type: Literal[1, 2, 3] | UndefinedType = UNDEFINED,  # TODO: Replace this with a type alias in discord_typings
        global_priority: int = 0,
    ) -> ApplicationCommandData:  # TODO: Narrow typing to never include guild_id
        """Creates or updates a guild command

        See the `documentation <https://discord.dev/interactions/application-commands#create-guild-application-command>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only update commands for your current application
        guild_id:
            The guild to add the command to
        name:
            The name of the command

            .. note::
                If the name is already taken by a existing application command with the same name and type
                it will update the exisiting command.
            .. note::
                This has to be between 1-32 characters long and follow the `naming conventions <https://discord.dev/interactions/application-commands#application-command-object-application-command-naming>`__
        description:
            The description of the command

            .. note::
                This has to be between 1-100 characters long

            .. warning::
                Some special characters may be automatically removed from this!
        name_localizations:
            The localizations for the name

            .. note::
                This has to be between 1-32 characters long and follow the `naming conventions <https://discord.dev/interactions/application-commands#application-command-object-application-command-naming>`__
        description_localizations:
            The localizations for the description

            .. note::
                This has to be between 1-100 characters long

            .. warning::
                Some special characters may be automatically removed from this!
        options:
            The parameters or sub-commands of the command

            .. note::
                This should only be provide
        default_member_permissions:
            The default permissions to require to use the command
        type:
            The type of the command

            .. note::
                This defaults to ``1`` if it is :data:`UNDEFINED`.

            **Possible values**
            - ``1``: Slash/text command
            - ``2``: User context menu
            - ``3``: Message context menu
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.ApplicationCommandData
            The command that was created
        """
        route = Route(
            "POST",
            "/applications/{application_id}/guilds/{guild_id}/commands",
            application_id=application_id,
            guild_id=guild_id,
        )

        payload: JsonCompatible = {"name": name, "description": description}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name_localizations is not UNDEFINED:
            payload["name_localizations"] = name_localizations
        if description_localizations is not UNDEFINED:
            payload["description_localizations"] = description_localizations
        if options is not UNDEFINED:
            payload["options"] = options
        if default_member_permissions is not UNDEFINED:
            payload["default_member_permissions"] = default_member_permissions
        if type is not UNDEFINED:
            payload["type"] = type

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_application_command(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        guild_id: Snowflake,
        command_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> ApplicationCommandData:  # TODO: Narrow typing to never include guild_id
        """Gets a guild command

        See the `documentation <https://discord.dev/interactions/application-commands#get-guild-application-command>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        guild_id:
            The guild to get the command from
        application_id:
            The id of the command to fetch
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.ApplicationCommandData
            The global commmand fetched
        """
        route = Route(
            "GET",
            "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
            application_id=application_id,
            guild_id=guild_id,
            command_id=command_id,
        )

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def edit_guild_application_command(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        guild_id: Snowflake,
        command_id: Snowflake,
        *,
        name: str | UndefinedType = UNDEFINED,
        name_localizations: dict[Locales, str] | None | UndefinedType = UNDEFINED,
        description: str | UndefinedType = UNDEFINED,
        description_localizations: dict[Locales, str] | None | UndefinedType = UNDEFINED,
        options: list[ApplicationCommandOptionData] | UndefinedType = UNDEFINED,
        default_member_permissions: str | None | UndefinedType = UNDEFINED,
        type: Literal[1, 2, 3] | UndefinedType = UNDEFINED,  # TODO: Replace this with a type alias in discord_typings
        global_priority: int = 0,
    ) -> ApplicationCommandData:  # TODO: Narrow typing
        """Updates a guild application command

        See the `documentation <https://discord.dev/interactions/application-commands#edit-guild-application-command>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only update commands for your current application
        guild_id:
            The id of the guild where the command is located in
        name:
            The name of the command

            .. note::
                If the name is already taken by a existing application command with the same name and type
                it will update the exisiting command.
            .. note::
                This has to be between 1-32 characters long and follow the `naming conventions <https://discord.dev/interactions/application-commands#application-command-object-application-command-naming>`__
        name_localizations:
            The localizations for the name

            .. note::
                This has to be between 1-32 characters long and follow the `naming conventions <https://discord.dev/interactions/application-commands#application-command-object-application-command-naming>`__
        description:
            The description of the command

            .. note::
                This has to be between 1-100 characters long

            .. warning::
                Some special characters may be automatically removed from this!
        description_localizations:
            The localizations for the description

            .. note::
                This has to be between 1-100 characters long

            .. warning::
                Some special characters may be automatically removed from this!
        options:
            The parameters or sub-commands of the command

            .. note::
                This should only be provide
        default_member_permissions:
            The default permissions to require to use the command
        type:
            The type of the command

            .. note::
                This defaults to ``1`` if it is :data:`UNDEFINED`.

            **Possible values**
            - ``1``: Slash/text command
            - ``2``: User context menu
            - ``3``: Message context menu
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.ApplicationCommandData
            The command that was edited
        """
        route = Route(
            "PATCH",
            "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
            application_id=application_id,
            guild_id=guild_id,
            command_id=command_id,
        )

        payload: JsonCompatible = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name
        if name_localizations is not UNDEFINED:
            payload["name_localizations"] = name_localizations
        if description is not UNDEFINED:
            payload["description"] = description
        if description_localizations is not UNDEFINED:
            payload["description_localizations"] = description_localizations
        if options is not UNDEFINED:
            payload["options"] = options
        if default_member_permissions is not UNDEFINED:
            payload["default_member_permissions"] = default_member_permissions
        if type is not UNDEFINED:
            payload["type"] = type

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_guild_application_command(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        guild_id: Snowflake,
        command_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> None:
        """Deletes a guild command

        See the `documentation <https://discord.dev/interactions/application-commands#delete-guild-application-command>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        application_id:
            The id of the command to fetch
        guild_id:
            The guild where the command is located in
        command_id:
            The command to delete
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "GET",
            "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
            application_id=application_id,
            guild_id=guild_id,
            command_id=command_id,
        )

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def bulk_overwrite_guild_application_commands(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        guild_id: Snowflake,
        *commands: ApplicationCommandPayload,
        global_priority: int = 0,
    ) -> list[ApplicationCommandData]:  # TODO: Narrow typing to always include guild_id
        """Bulk overwrite guild commands

        See the `documentation <https://discord.dev/interactions/application-commands#bulk-overwrite-global-application-commands>`__

        .. warning::
            This will replace all your global commands. Include the old commands to keep them

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only update commands for your current application
        guild_id:
            The guild to overwrite commands in
        commands:
            The commands to overwrite the current commands with
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[discord_typings.ApplicationCommandData]
            The new commands
        """
        route = Route(
            "PUT",
            "/applications/{application_id}/guilds/{guild_id}/commands",
            application_id=application_id,
            guild_id=guild_id,
        )

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            json=commands,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_application_command_permissions(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        guild_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> list[GuildApplicationCommandPermissionData]:
        """Gets all application command permissions in a guild

        See the `documentation <https://discord.dev/interactions/application-commands#get-guild-application-command-permissions>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        application_id:
            The id of the command to fetch
        guild_id:
            The guild to get permissions from
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[discord_typings.GuildApplicationCommandPermissionData]
            The application command permissions overwrites in the guild
        """
        route = Route(
            "GET",
            "/applications/{application_id}/guilds/{guild_id}/commands/permissions",
            application_id=application_id,
            guild_id=guild_id,
        )

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_application_command_permissions(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        guild_id: Snowflake,
        command_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> GuildApplicationCommandPermissionData:
        """Gets permissions for a command in a guild

        See the `documentation <https://discord.dev/interactions/application-commands#get-guild-application-command-permissions>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        command_id:
            The id of the command to fetch
        guild_id:
            The guild to get permissions from
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.GuildApplicationCommandPermissionData
            The application command permissions overwrites for the command
        """
        route = Route(
            "GET",
            "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions",
            application_id=application_id,
            guild_id=guild_id,
            command_id=command_id,
        )

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Add Edit Application Command Permissions

    # Responding to application commands (Receiving and responding)
    # TODO: Add Create Interaction Response
    async def get_original_interaction_response(
        self,
        application_id: Snowflake,
        interaction_token: str,
        *,
        global_priority: int = 0,
    ) -> MessageData:
        """Gets the first response sent to a interaction

        See the `documentation <https://discord.dev/interactions/receiving-and-responding#get-original-interaction-response>`__

        Parameters
        ----------
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        interaction_token:
            The token of the interaction
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.MessageData
            The message
        """
        route = Route(
            "GET",
            "/webhooks/{application_id}/{interaction_token}/messages/@original",
            application_id=application_id,
            interaction_token=interaction_token,
        )

        r = await self._request(
            route,
            ratelimit_key=None,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Add Edit Original Interaction Response

    async def delete_original_interaction_response(
        self,
        application_id: Snowflake,
        interaction_token: str,
        *,
        global_priority: int = 0,
    ) -> None:
        """Deletes the first response sent to a interaction

        See the `documentation <https://discord.dev/interactions/receiving-and-responding#delete-original-interaction-response>`__

        Parameters
        ----------
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        interaction_token:
            The token of the interaction
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "DELETE",
            "/webhooks/{application_id}/{interaction_token}/messages/@original",
            application_id=application_id,
            interaction_token=interaction_token,
        )

        await self._request(
            route,
            ratelimit_key=None,
            global_priority=global_priority,
        )

    # TODO: Add Create Followup Message

    async def get_followup_message(
        self,
        application_id: Snowflake,
        interaction_token: str,
        message_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> MessageData:
        """Gets a response sent to a interaction by message id

        See the `documentation <https://discord.dev/interactions/receiving-and-responding#get-followup-message>`__

        Parameters
        ----------
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        interaction_token:
            The token of the interaction
        message_id:
            The id of the message to fetch
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.MessageData
            The message that was fetched
        """
        route = Route(
            "GET",
            "/webhooks/{application_id}/{interaction_token}/messages/{message_id}",
            application_id=application_id,
            interaction_token=interaction_token,
            message_id=message_id,
        )

        r = await self._request(
            route,
            ratelimit_key=None,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Add Edit Followup Message
    async def delete_followup_message(
        self,
        application_id: Snowflake,
        interaction_token: str,
        message_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> MessageData:
        """Deletes a response sent to a interaction by message id

        See the `documentation <https://discord.dev/interactions/receiving-and-responding#delete-followup-message>`__

        Parameters
        ----------
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        interaction_token:
            The token of the interaction
        message_id:
            The id of the message to delete
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "DELETE",
            "/webhooks/{application_id}/{interaction_token}/messages/{message_id}",
            application_id=application_id,
            interaction_token=interaction_token,
            message_id=message_id,
        )

        r = await self._request(
            route,
            ratelimit_key=None,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # Audit log
    async def get_guild_audit_log(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        user_id: int | None = None,
        action_type: AuditLogEvents | None = None,
        before: int | None = None,
        limit: int = 50,
        global_priority: int = 0,
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
        AuditLogData
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
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # Channel
    async def get_channel(
        self, authentication: BotAuthentication, channel_id: Snowflake, *, global_priority: int = 0
    ) -> ChannelData:
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
        ChannelData
            The channel.

            .. hint::
                A list of fields are available in the documentation.
        """
        route = Route("GET", "/channels/{channel_id}", channel_id=channel_id)
        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # These 3 requests are 1 route but are split up for convinience
    async def modify_group_dm(
        self,
        authentication: BearerAuthentication,
        channel_id: Snowflake,
        *,
        name: str | UndefinedType = UNDEFINED,
        icon: str | None | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
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
        payload: JsonCompatible = {}  # TODO: Use a typehint for payload

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name

        if icon is not UNDEFINED:
            payload["icon"] = icon

        headers = {"Authorization": str(authentication)}

        if reason is not UNDEFINED:
            headers["reason"] = reason

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_guild_channel(
        self,
        authentication: BearerAuthentication,
        channel_id: Snowflake,
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
        parent_id: Snowflake | UndefinedType = UNDEFINED,
        rtc_region: str | None | UndefinedType = UNDEFINED,
        video_quality_mode: Literal[1, 2] | None | UndefinedType = UNDEFINED,  # TODO: Implement VideoQualityMode
        default_auto_archive_duration: Literal[60, 1440, 4320, 10080] | None | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
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
        payload: JsonCompatible = {}  # TODO: Use a typehint for payload

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

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_thread(
        self,
        authentication: BotAuthentication,
        thread_id: Snowflake,
        *,
        name: str | UndefinedType = UNDEFINED,
        archived: bool | UndefinedType = UNDEFINED,
        auto_archive_duration: Literal[60, 1440, 4320, 10080] | UndefinedType = UNDEFINED,
        locked: bool | UndefinedType = UNDEFINED,
        invitable: bool | UndefinedType = UNDEFINED,
        rate_limit_per_user: int | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
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
        payload: JsonCompatible = {}

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

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_channel(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        channel_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Deletes a channel.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to delete.
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route("DELETE", "/channels/{channel_id}", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        await self._request(
            route, headers=headers, ratelimit_key=authentication.rate_limit_key, global_priority=global_priority
        )

    @overload
    async def get_channel_messages(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        *,
        around: int,
        limit: int | UndefinedType,
        global_priority: int = 0,
    ) -> list[MessageData]:
        ...

    @overload
    async def get_channel_messages(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        *,
        before: int,
        limit: int | UndefinedType,
        global_priority: int = 0,
    ) -> list[MessageData]:
        ...

    @overload
    async def get_channel_messages(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        *,
        after: int,
        limit: int | UndefinedType,
        global_priority: int = 0,
    ) -> list[MessageData]:
        ...

    @overload
    async def get_channel_messages(
        self, authentication: BotAuthentication, channel_id: Snowflake, *, global_priority: int = 0
    ) -> list[MessageData]:
        ...

    async def get_channel_messages(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        *,
        around: int | UndefinedType = UNDEFINED,
        before: int | UndefinedType = UNDEFINED,
        after: int | UndefinedType = UNDEFINED,
        limit: int | UndefinedType = UNDEFINED,
        global_priority: int = 0,
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

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            params=params,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def create_message(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
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
        global_priority: int = 0,
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
        discord_typings.MessageData
            The message that was sent.
        """
        route = Route("POST", "/channels/{channel_id}/messages", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}

        # We use payload_json here as the format is more strictly defined than form data.
        # This means we don't have to manually format the data.
        payload: JsonCompatible = {}

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
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def crosspost_message(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        message_id: Snowflake,
        *,
        global_priority: int = 0,
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
        discord_typings.MessageData
            The message that was crossposted.
        """
        route = Route(
            "POST",
            "/channels/{channel_id}/messages/{message_id}/crosspost",
            channel_id=channel_id,
            message_id=message_id,
        )
        headers = {"Authorization": str(authentication)}

        r = await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def create_reaction(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        message_id: Snowflake,
        emoji: str,
        *,
        global_priority: int = 0,
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

        await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
        )

    async def delete_own_reaction(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        message_id: Snowflake,
        emoji: str,
        *,
        global_priority: int = 0,
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

        await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
        )

    async def delete_user_reaction(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        message_id: Snowflake,
        emoji: str,
        user_id: Snowflake,
        *,
        global_priority: int = 0,
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

        await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
        )

    async def get_reactions(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        message_id: Snowflake,
        emoji: str,
        *,
        after: Snowflake | UndefinedType = UNDEFINED,
        limit: int | UndefinedType = UNDEFINED,
        global_priority: int = 0,
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

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            params=params,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_all_reactions(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        message_id: Snowflake,
        *,
        global_priority: int = 0,
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

        await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
        )

    async def delete_all_reactions_for_emoji(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        message_id: Snowflake,
        emoji: str,
        *,
        global_priority: int = 0,
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

        await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
        )

    async def edit_message(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        message_id: Snowflake,
        *,
        content: str | None | UndefinedType = UNDEFINED,
        embeds: list[EmbedData] | None | UndefinedType = UNDEFINED,
        flags: int | None | UndefinedType = UNDEFINED,
        allowed_mentions: AllowedMentionsData | None | UndefinedType = UNDEFINED,
        components: list[ActionRowData] | None | UndefinedType = UNDEFINED,
        files: list[File] | None | UndefinedType = UNDEFINED,
        attachments: list[AttachmentData] | None | UndefinedType = UNDEFINED,  # TODO: Partial
        global_priority: int = 0,
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
        MessageData
            The edited message.
        """
        route = Route(
            "PATCH", "/channels/{channel_id}/messages/{message_id}", channel_id=channel_id, message_id=message_id
        )

        headers = {"Authorization": str(authentication)}
        payload: JsonCompatible = {}

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

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            data=form,
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def delete_message(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        message_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
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

        await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
        )

    async def bulk_delete_messages(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        messages: list[str] | list[int] | list[Snowflake],
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
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
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            json={"messages": messages},
            global_priority=global_priority,
        )

    async def edit_channel_permissions(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        target_type: Literal[0, 1],
        target_id: Snowflake,
        *,
        allow: str | None | UndefinedType = UNDEFINED,
        deny: str | None | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
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

        payload: JsonCompatible = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if allow is not UNDEFINED:
            payload["allow"] = allow
        if deny is not UNDEFINED:
            payload["deny"] = deny

        payload["type"] = target_type

        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            json=payload,
            global_priority=global_priority,
        )

    async def get_channel_invites(
        self, authentication: BotAuthentication, channel_id: Snowflake, *, global_priority: int = 0
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

        r = await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    @overload
    async def create_channel_invite(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        *,
        max_age: int | UndefinedType = UNDEFINED,
        max_uses: int | UndefinedType = UNDEFINED,
        temporary: bool | UndefinedType = UNDEFINED,
        unique: bool | UndefinedType = UNDEFINED,
        target_type: Literal[0],
        target_user_id: Snowflake,
        target_application_id: UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> InviteData:
        ...

    @overload
    async def create_channel_invite(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        *,
        max_age: int | UndefinedType = UNDEFINED,
        max_uses: int | UndefinedType = UNDEFINED,
        temporary: bool | UndefinedType = UNDEFINED,
        unique: bool | UndefinedType = UNDEFINED,
        target_type: Literal[1],
        target_user_id: UndefinedType = UNDEFINED,
        target_application_id: Snowflake,
        global_priority: int = 0,
    ) -> InviteData:
        ...

    @overload
    async def create_channel_invite(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        *,
        max_age: int | UndefinedType = UNDEFINED,
        max_uses: int | UndefinedType = UNDEFINED,
        temporary: bool | UndefinedType = UNDEFINED,
        unique: bool | UndefinedType = UNDEFINED,
        target_type: UndefinedType = UNDEFINED,
        target_user_id: UndefinedType = UNDEFINED,
        target_application_id: UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> InviteData:
        ...

    async def create_channel_invite(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        *,
        max_age: int | UndefinedType = UNDEFINED,
        max_uses: int | UndefinedType = UNDEFINED,
        temporary: bool | UndefinedType = UNDEFINED,
        unique: bool | UndefinedType = UNDEFINED,
        target_type: Literal[0, 1] | UndefinedType = UNDEFINED,
        target_user_id: Snowflake | UndefinedType = UNDEFINED,
        target_application_id: Snowflake | UndefinedType = UNDEFINED,
        global_priority: int = 0,
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
        InviteData
            The invite data.
        """
        route = Route("POST", "/channels/{channel_id}/invites", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}

        payload: JsonCompatible = {}

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

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def delete_channel_permission(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        target_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
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

        await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
        )

    async def follow_news_channel(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        webhook_channel_id: Snowflake,
        *,
        global_priority: int = 0,
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
        FollowedChannelData
            The followed channel data.
        """
        route = Route("POST", "/channels/{channel_id}/followers", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}
        payload: JsonCompatible = {"webhook_channel_id": webhook_channel_id}

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def trigger_typing_indicator(
        self, authentication: BotAuthentication, channel_id: Snowflake, *, global_priority: int = 0
    ) -> None:
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

        await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
        )

    async def get_pinned_messages(
        self, authentication: BotAuthentication, channel_id: Snowflake, *, global_priority: int = 0
    ) -> list[MessageData]:
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

        r = await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def pin_message(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        message_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
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
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        message_id: Snowflake,
        *,
        global_priority: int = 0,
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

        await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
        )

    async def group_dm_add_recipient(
        self,
        authentication: BearerAuthentication,
        channel_id: Snowflake,
        user_id: Snowflake,
        *,
        global_priority: int = 0,
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

        await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
        )

    async def group_dm_remove_recipient(
        self,
        authentication: BearerAuthentication,
        channel_id: Snowflake,
        user_id: Snowflake,
        *,
        global_priority: int = 0,
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

        await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
        )

    async def start_thread_from_message(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        message_id: Snowflake,
        name: str,
        *,
        auto_archive_duration: Literal[60, 1440, 4320, 10080] | UndefinedType = UNDEFINED,
        rate_limit_per_user: int | None | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
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
        rate_limit_per_user: int` | :data:`None` | :class:`UndefinedType
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

        payload: JsonCompatible = {
            "name": name,
        }

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if auto_archive_duration is not UNDEFINED:
            payload["auto_archive_duration"] = auto_archive_duration
        if rate_limit_per_user is not UNDEFINED:
            payload["rate_limit_per_user"] = rate_limit_per_user

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def start_thread_without_message(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        name: str,
        *,
        auto_archive_duration: Literal[60, 1440, 4320, 10080] | UndefinedType = UNDEFINED,
        thread_type: Literal[11, 12] | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        invitable: bool | UndefinedType = UNDEFINED,
        rate_limit_per_user: int | None | UndefinedType = UNDEFINED,
        global_priority: int = 0,
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
        ChannelData
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

        payload: JsonCompatible = {
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

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Add start thread in forum channel here!

    async def join_thread(
        self, authentication: BotAuthentication, channel_id: Snowflake, *, global_priority: int = 0
    ) -> None:
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

        await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
        )

    async def add_thread_member(
        self, authentication: BotAuthentication, channel_id: Snowflake, user_id: str | int, *, global_priority: int = 0
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
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

    async def leave_thread(
        self, authentication: BotAuthentication, channel_id: Snowflake, *, global_priority: int = 0
    ) -> None:
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
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

    async def remove_thread_member(
        self, authentication: BotAuthentication, channel_id: Snowflake, user_id: str | int, *, global_priority: int = 0
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
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

    async def get_thread_member(
        self, authentication: BotAuthentication, channel_id: Snowflake, user_id: str | int, *, global_priority: int = 0
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
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def list_thread_members(
        self, authentication: BotAuthentication, channel_id: Snowflake, *, global_priority: int = 0
    ) -> list[ThreadMemberData]:
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

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def list_public_archived_threads(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        *,
        before: str | UndefinedType = UNDEFINED,
        limit: int | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> HasMoreListThreadsData:
        """List public archived threads

        Read the `documentation <https://discord.dev/resources/channel#list-public-archived-threads>`__

        .. note::
            This requires the ``READ_MESSAGE_HISTORY`` permission

        Parameters
        ----------
        authentication:
            Auth info.
        channel_id:
            The channel to get threads from
        before:
            A ISO8601 timestamp of public threads to get after
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        params = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if before is not UNDEFINED:
            params["before"] = before
        if limit is not UNDEFINED:
            params["limit"] = limit

        route = Route("GET", "/channels/{channel_id}/threads/archived/public", channel_id=channel_id)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            params=params,
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def list_private_archived_threads(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        *,
        before: str | UndefinedType = UNDEFINED,
        limit: int | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> HasMoreListThreadsData:
        """List private archived threads

        Read the `documentation <https://discord.dev/resources/channel#list-private-archived-threads>`__

        .. note::
            This requires the ``READ_MESSAGE_HISTORY`` and ``MANAGE_THREADS`` permissions.

        Parameters
        ----------
        authentication:
            Auth info.
        channel_id:
            The channel to get threads from
        before:
            A ISO8601 timestamp of public threads to get after
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        params = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if before is not UNDEFINED:
            params["before"] = before
        if limit is not UNDEFINED:
            params["limit"] = limit

        route = Route("GET", "/channels/{channel_id}/threads/archived/private", channel_id=channel_id)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            params=params,
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def list_private_joined_archived_threads(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        *,
        before: str | UndefinedType = UNDEFINED,
        limit: int | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> HasMoreListThreadsData:
        """List private archived threads the bot has joined.

        Read the `documentation <https://discord.dev/resources/channel#list-joined-private-archived-threads>`__

        .. note::
            This requires the ``READ_MESSAGE_HISTORY`` permission.

        Parameters
        ----------
        authentication:
            Auth info.
        channel_id:
            The channel to get threads from
        before:
            A ISO8601 timestamp of public threads to get after
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        params = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if before is not UNDEFINED:
            params["before"] = before
        if limit is not UNDEFINED:
            params["limit"] = limit

        route = Route("GET", "/channels/{channel_id}/users/@me/threads/archived/private", channel_id=channel_id)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            params=params,
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    # Emoji
    async def list_guild_emojis(
        self, authentication: BotAuthentication, guild_id: Snowflake, *, global_priority: int = 0
    ) -> list[EmojiData]:
        """List all emojis in a guild.

        Read the `documentation <https://discord.dev/resources/emoji#list-guild-emojis>`__

        Parameters
        ----------
        authentication:
            Auth info
        guild_id:
            The guild to list emojis from
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("GET", "/guilds/{guild_id}/emojis", guild_id=guild_id)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_emoji(
        self, authentication: BotAuthentication, guild_id: Snowflake, emoji_id: int | str, *, global_priority: int = 0
    ) -> list[EmojiData]:
        """Get emoji info

        Read the `documentation <https://discord.dev/resources/emoji#get-guild-emoji>`__

        Parameters
        ----------
        authentication:
            Auth info
        guild_id:
            The guild to get the emoji from
        emoji_id:
            The emoji to get
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("GET", "/guilds/{guild_id}/emojis/{emoji_id}", guild_id=guild_id, emoji_id=emoji_id)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Add create guild emoji here

    async def modify_guild_emoji(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        emoji_id: Snowflake,
        *,
        name: str | UndefinedType = UNDEFINED,
        roles: list[Snowflake] | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> EmojiData:
        """Modify a emoji

        Read the `documentation <https://discord.dev/resources/emoji#modify-guild-emoji>`__

        .. note::
            This requires the ``MANAGE_EMOJIS_AND_STICKERS`` permission.
        .. note::
            This dispatches a ``GUILD_EMOJIS_UPDATE`` event.

        Parameters
        ----------
        authentication:
            The auth info
        guild_id:
            The guild where the emoji is in
        emoji_id:
            The emoji to modify
        name:
            The emoji name.
        roles:
            IDs of roles that can use this emoji.
        reason:
            Reason to show in audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route("PATCH", "/guilds/{guild_id}/emojis/{emoji_id}", guild_id=guild_id, emoji_id=emoji_id)

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        params = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            params["name"] = name
        if roles is not UNDEFINED:
            params["roles"] = roles

        r = self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            params=params,
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def delete_guild_emoji(
        self, authentication: BotAuthentication, guild_id: Snowflake, emoji_id: int | str, *, global_priority: int = 0
    ) -> list[EmojiData]:
        """Delete a emoji

        Read the `documentation <https://discord.dev/resources/emoji#delete-guild-emoji>`__

        .. note::
            This requires the ``MANAGE_EMOJIS_AND_STICKERS`` permission.

        .. note::
            This dispatches a ``GUILD_EMOJIS_UPDATE`` event.

        Parameters
        ----------
        authentication:
            Auth info
        guild_id:
            The guild to get the emoji from
        emoji_id:
            The emoji to get
        reason:
            The reason to put in the audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("DELETE", "/guilds/{guild_id}/emojis/{emoji_id}", guild_id=guild_id, emoji_id=emoji_id)

        headers = {"Authorization": str(authentication)}

        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    # Guild
    async def create_guild(
        self,
        authentication: BotAuthentication,
        name: str,
        *,
        region: str | None | UndefinedType = UNDEFINED,
        icon: str | UndefinedType = UNDEFINED,
        verification_level: Literal[0, 1, 2, 3, 4] | UndefinedType = UNDEFINED,
        default_message_notifications: Literal[0, 1] | UndefinedType = UNDEFINED,
        explicit_content_filter: Literal[0, 1, 2] | UndefinedType = UNDEFINED,
        roles: list[RoleData] | UndefinedType = UNDEFINED,
        channels: list[PartialChannelData] | UndefinedType = UNDEFINED,
        afk_channel_id: Snowflake | UndefinedType = UNDEFINED,
        afk_timeout: int | UndefinedType = UNDEFINED,
        system_channel_id: Snowflake | UndefinedType = UNDEFINED,
        system_channel_flags: int | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> GuildData:
        """Create a guild

        See the `documentation <https://discord.dev/resources/guild#create-guild>`__.

        .. note::
            This can only be used by bots in less than 10 guilds.

        .. note::
            This dispatches a ``GUILD_CREATE`` event

        Parameters
        ----------
        authentication:
            The auth info
        name:
            The guild name
        region:
            The region of voice channels

            .. warning::
                This is deprecated by discord and may be removed in a future version of the Discord API.
        icon:
            A base64 encoded 128x128px icon of the guild.
        verification_level:
            The guild verification level
        default_message_notifications:
            The default message notification level

            - ``0``: All messages
            - ``1``: Only mentions
        explicit_content_filter_level:
            The explicit content filter level.

            - ``0`` Disabled
            - ``1`` Members without roles
            - ``2`` All members
        roles:
            A list of roles to initially create.

            .. hint::
                The id here is just a placeholder and can be used other places in this payload to reference it.

                It will be replaced by a snowflake by Discord once it has been created
        channels:
            Channels to initially create

            .. note::
                Not providing this will create a default setup

            .. hint::
                The id here is just a placeholder and can be used other places in this payload to reference it.

                It will be replaced by a snowflake by Discord once it has been created

            .. hint::
                Overwrites can be created by using a placeholder in the target and using the same placeholder as a role id.
        afk_channel_id:
            The voice channel afk members will be moved to when idle in voice chat.
        afk_timeout:
            The time in seconds a member has to be idle in a voice channel to be moved to the ``afk_channel_id``
        system_channel_id:
            The id of the channel where guild notices such as welcome messages and boost events are posted
        system_channel_flags:
            A bitwise flag deciding what messages to post in the system channel.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("POST", "/guilds")
        payload: JsonCompatible = {"name": name}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if region is not UNDEFINED:
            warn(FutureWarning("Guild wide voice regions and may be removed in a future Discord API version."))
            payload["region"] = region
        if icon is not UNDEFINED:
            payload["icon"] = icon
        if verification_level is not UNDEFINED:
            payload["verification_level"] = verification_level
        if default_message_notifications is not UNDEFINED:
            payload["default_messsage_notifications"] = default_message_notifications
        if explicit_content_filter is not UNDEFINED:
            payload["explicit_content_filter"] = explicit_content_filter
        if roles is not UNDEFINED:
            payload["roles"] = roles
        if channels is not UNDEFINED:
            payload["channels"] = channels
        if afk_channel_id is not UNDEFINED:
            payload["afk_channel_id"] = afk_channel_id
        if afk_timeout is not UNDEFINED:
            payload["afk_timeout"] = afk_timeout
        if system_channel_id is not UNDEFINED:
            payload["system_channel_id"] = system_channel_id
        if system_channel_flags is not UNDEFINED:
            payload["system_channel_flags"] = system_channel_flags

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
            json=payload,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        with_counts: bool | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> GuildData:  # TODO: More spesific typehints due to with_counts
        """Get a guild by ID

        Read the `documentation <https://discord.dev/resources/guild#get-guild>`__

        Parameters
        ----------
        authentication:
            The authenticaton info.
        guild_id:
            The guild to get
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("GET", "/guilds/{guild_id}", guild_id=guild_id)

        params = {}

        # Save a bit of bandwith by not including it by default
        # TODO: Not sure if this is worth it
        if with_counts is not UNDEFINED:
            params["with_counts"] = with_counts

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            params=params,
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def guild_guild_preview(
        self, authentication: BotAuthentication, guild_id: Snowflake, *, global_priority: int = 0
    ) -> GuildPreviewData:
        """Gets a guild preview by ID

        Read the `documentation <https://discord.dev/resources/guild#get-guild-preview>`__

        .. note::
            If the bot is not in the guild, it needs the ``LURKABLE`` feature.

        Parameters
        ----------
        authentication:
            The authentication info
        guild_id:
            The id of the guild to get
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("GET", "/guilds/{guild_id}/preview", guild_id=guild_id)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Implement modify guild here

    async def delete_guild(
        self, authentication: BotAuthentication, guild_id: Snowflake, *, global_priority: int = 0
    ) -> None:
        """Deletes a guild

        Read the `documentation <https://discord.dev/resources/guild#delete-guild>`__

        .. note::
            You have to be the guild owner to delete it.

        .. note::
            This dispatches a ``GUILD_DELETE`` event

        Parameters
        ----------
        authentication:
            The auth info.
        guild_id:
            The id of the guild to delete
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("DELETE", "/guilds/{guild_id}", guild_id=guild_id)

        await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

    async def get_guild_channels(
        self, authentication: BotAuthentication, guild_id: Snowflake, *, global_priority: int = 0
    ) -> list[ChannelData]:
        """Gets all channels in a guild

        Read the `documentation <https://discord.dev/resources/guild#get-guild-channels>`__

        Parameters
        ----------
        authentication:
            The auth info.
        guild_id:
            The guild to get channels from
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("GET", "/guilds/{guild_id}/channels", guild_id=guild_id)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Implement create guild channel

    async def modify_guild_channel_positions(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *position_updates: ChannelPositionData,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Modifies channel positions

        Read the `documentation <https://discord.dev/resources/guild#modify-guild-channel-positions>`__

        Parameters
        ----------
        authentication:
            The auth info.
        guild_id:
            The guild to modify channel positions in.
        position_updates:
            The position updates to do.
        reason:
            The reason to put in the audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("PATCH", "/guilds/{guild_id}/channels", guild_id=guild_id)

        headers = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        await self._request(
            route,
            json=position_updates,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

    async def list_active_guild_threads(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> HasMoreListThreadsData:  # TODO: This is not the correct type
        """List active guild threads

        Read the `documentation <https://discord.dev/resources/guild#list-active-guild-threads>`__

        Parameters
        ----------
        authentication:
            Auth info.
        guild_id:
            The guild to get threads from
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("GET", "/guilds/{guild_id}/threads/active", guild_id=guild_id)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_member(
        self, authentication: BotAuthentication, guild_id: Snowflake, user_id: str | int, *, global_priority: int = 0
    ) -> GuildMemberData:
        """Gets a member

        Read the `documentation <https://discord.dev/resources/guild#get-guild-member>`__

        Parameters
        ----------
        authentication:
            Auth info.
        guild_id:
            The guild to get the member from
        user_id:
            The user to get the member from
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("GET", "/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def list_guild_members(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        after: int | UndefinedType = UNDEFINED,
        limit: int | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> list[GuildMemberData]:
        """Lists members in a guild

        Read the `documentation <https://discord.dev/resources/guild#list-guild-members>`__

        .. note::
            This requires the ``GUILD_MEMBERS`` intent enabled in the `developer portal <https://discord.com/developers/applications>`__

        Parameters
        ----------
        authentication:
            Auth info.
        guild_id:
            The guild to get the members from
        after:
            What a members id has to be above for them to be returned.

            .. hint::
                This is usually the highest user id in the previous page.
            .. note::
                This defaults to ``0``
        limit:
            How many members to return per page

            .. note::
                This defaults to ``1``
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("GET", "/guilds/{guild_id}/members", guild_id=guild_id)

        query = {}
        # These can technically be provided by default however its wasted bandwidth
        # TODO: Reconsider this?
        # This only adds them if they are provided (not Undefined)
        if after is not UNDEFINED:
            query["after"] = after
        if limit is not UNDEFINED:
            query["limit"] = limit

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            query=query,
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def search_guild_members(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        query: str,
        *,
        limit: int | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> list[GuildMemberData]:
        """Searches for members in the guild with a username or nickname that starts with ``query``

        Read the `documentation <https://discord.dev/resources/guild#search-guild-members>`__

        Parameters
        ----------
        authentication:
            Auth info.
        guild_id:
            The guild to get the members from
        query:
            What a members username or nickname has to start with to be included
        limit:
            The amount of results to return

            .. note::
                This has to be between ``1`` and `10,000`
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("GET", "/guilds/{guild_id}/members/search", guild_id=guild_id)

        params = {"query": query}

        # These can technically be provided by default however its wasted bandwidth
        # TODO: Reconsider this?
        # This only adds them if they are provided (not Undefined)
        if limit is not UNDEFINED:
            params["limit"] = limit

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def add_guild_member(
        self,
        bot_authentication: BotAuthentication,
        user_authentication: BearerAuthentication,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        nick: str | UndefinedType = UNDEFINED,
        roles: list[Snowflake] | UndefinedType = UNDEFINED,
        mute: bool | UndefinedType = UNDEFINED,
        deaf: bool | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> GuildMemberData | None:
        """Adds a member to a guild

        .. note::
            The bot requires the ``CREATE_INSTANT_INVITE`` permission.

        Parameters
        ----------
        bot_authentication:
            The bot to use to invite the user
        user_authentication:
            The user to add to the guild.

            .. note::
                This requires the ``guilds.join`` scope.
        guild_id:
            The guild to add the user to
        user_id:
            The user to add to the guild.
        nick:
            What to set the users nickname to.

            .. note::
                Setting this requires the ``MANAGE_NICKNAMES`` permission
        roles:
            Roles to assign to the user.

            .. note::
                Setting this requires the ``MANAGE_ROLES`` permission
        mute:
            Whether to server mute the user

            .. note::
                Setting this requires the ``MUTE_MEMBERS`` permission
        deaf:
            Whether to server deafen the user

            .. note::
                Setting this requires the ``DEAFEN_MEMBERS`` permission
        global_priority:
            The priority of the request for the global rate-limiter.


        Returns
        -------
        discord_typings.GuildMemberData
            The member was added to the guild
        :data:`None`
            The member was already in the guild
        """
        route = Route("PUT", "/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id)

        params = {"access_token": user_authentication.token}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if nick is not UNDEFINED:
            params["nick"] = nick
        if roles is not UNDEFINED:
            params["roles"] = roles
        if mute is not UNDEFINED:
            params["mute"] = mute
        if deaf is not UNDEFINED:
            params["deaf"] = deaf

        r = await self._request(
            route,
            ratelimit_key=bot_authentication.rate_limit_key,
            headers={"Authorization": str(bot_authentication)},
            params=params,
            global_priority=global_priority,
        )

        if r.status == 201:
            # Member was added to the guild
            # TODO: Make this verify the data from Discord
            return await r.json()  # type: ignore [no-any-return]

    async def modify_guild_member(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        nick: str | None | UndefinedType = UNDEFINED,
        roles: list[Snowflake] | None | UndefinedType = UNDEFINED,
        mute: bool | None | UndefinedType = UNDEFINED,
        deaf: bool | None | UndefinedType = UNDEFINED,
        channel_id: Snowflake | None | UndefinedType = UNDEFINED,
        communication_disabled_until: str | None | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> GuildMemberData:
        """Modifies a member

        Parameters
        ----------
        authentication:
            The auth info
        guild_id:
            The guild where the member to update is in.
        nick:
            What to change the users nickname to.

            .. note::
                Setting it to :data:`None` will remove the nickname.
            .. note::
                Setting this requires the ``MANAGE_NICKNAMES`` permission
        roles:
            The roles the member has.

            .. note::
                Setting this requires the ``MANAGE_ROLES`` permission
        mute:
            Whether to server mute the user

            .. note::
                Setting this requires the ``MUTE_MEMBERS`` permission
        deaf:
            Whether to server deafen the user

            .. note::
                Setting this requires the ``DEAFEN_MEMBERS`` permission
        channel_id:
            The channel to move the member to.

            .. warning::
                This will fail if the member is not in a voice channel
            .. note::
                Setting this requires having the ``VIEW_CHANNEL`` and ``CONNECT`` permissions in the ``channel_id`` channel, and the ``MOVE_MEMBERS`` permission
        communication_disabled_until:
            A ISO8601 timestamp of When the member's timeout will expire.

            .. note::
                This has to be under 28 days in the future.
            .. note::
                This requires the ``MODERATE_MEMBERS`` permission
        reason:
            The reason to put in the audit log
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.GuildMemberData
            The member after the update
        """
        route = Route("PATCH", "/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id)

        payload: JsonCompatible = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if nick is not UNDEFINED:
            payload["nick"] = nick
        if roles is not UNDEFINED:
            payload["roles"] = roles
        if mute is not UNDEFINED:
            payload["mute"] = mute
        if deaf is not UNDEFINED:
            payload["deaf"] = deaf
        if channel_id is not UNDEFINED:
            payload["channel_id"] = channel_id
        if communication_disabled_until is not UNDEFINED:
            payload["communication_disabled_until"] = communication_disabled_until

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["reason"] = reason

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def modify_current_member(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        nick: str | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> GuildMemberData:
        """Modifies a member

        Parameters
        ----------
        authentication:
            The auth info
        guild_id:
            The guild where the member to update is in.
        nick:
            What to change the users nickname to.

            .. note::
                Setting it to :data:`None` will remove the nickname.
        reason:
            The reason to put in the audit log
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.GuildMemberData
            The member after the update
        """
        route = Route("PATCH", "/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id)

        payload: JsonCompatible = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if nick is not UNDEFINED:
            payload["nick"] = nick

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["reason"] = reason

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Maybe add modify current user role here?`It is deprecated so not going to be implemented as of now
    async def add_guild_member_role(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        user_id: Snowflake,
        role_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Add a role to a member

        .. note::
            This requires the ``MANAGE_ROLES`` permission

        Parameters
        ----------
        authentication:
            The auth info.
        guild_id:
            The guild where the member is located
        user_id:
            The id of the member to add the role to
        role_id:
            The id of the role to add.
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "PUT",
            "/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
            guild_id=guild_id,
            user_id=user_id,
            role_id=role_id,
        )

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
        )

    async def remove_guild_member_role(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        user_id: Snowflake,
        role_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Removes a role from a member

        .. note::
            This requires the ``MANAGE_ROLES`` permission

        Parameters
        ----------
        authentication:
            The auth info.
        guild_id:
            The guild where the member is located
        user_id:
            The id of the member to remove the role from
        role_id:
            The id of the role to remove
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "DELETE",
            "/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
            guild_id=guild_id,
            user_id=user_id,
            role_id=role_id,
        )

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
        )

    async def remove_guild_member(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Removes a member from a guild

        .. note::
            This requires the ``KICK_MEMBERS`` permission and that the bot is higher in the role hierarchy than the member you are trying to kick

        Parameters
        ----------
        authentication:
            The auth info
        guild_id:
            The id of theguild to kick the member from
        user_id:
            The id of the user to kick
        reason:
            The reason to put in the audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("DELETE", "/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id)

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        await self._request(
            route, ratelimit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
        )

    @overload
    async def get_guild_bans(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        before: int,
        limit: int | UndefinedType,
        global_priority: int = 0,
    ) -> list[BanData]:
        ...

    @overload
    async def get_guild_bans(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        after: int,
        limit: int | UndefinedType,
        global_priority: int = 0,
    ) -> list[BanData]:
        ...

    @overload
    async def get_guild_bans(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> list[BanData]:
        ...

    async def get_guild_bans(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        before: int | UndefinedType = UNDEFINED,
        after: int | UndefinedType = UNDEFINED,
        limit: int | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> list[BanData]:
        """Gets a list of bans in a guild.

        See the `documentation <https://discord.dev/resources/guild#get-guild-bans>`__

        .. note::
            This requires the ``BAN_MEMBERS`` permission..

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of the guild to get bans from
        before:
            Do not return bans from users with a id more than this.

            .. note::
                This does not have to be a id of a existing user.
        after:
            Do not return bans from users with a id less than this.

            .. note::
                This does not have to be a id of a existing user.
        limit:
            The number of bans to get.

            .. note::
                This has to be between 1-100.
            .. note::
                If this is not provided it will default to ``50``.
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route("GET", "/guilds/{guild_id}/bans", guild_id=guild_id)
        headers = {"Authorization": str(authentication)}

        params = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if before is not UNDEFINED:
            params["before"] = before
        if after is not UNDEFINED:
            params["after"] = after
        if limit is not UNDEFINED:
            params["limit"] = limit

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            params=params,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_ban(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> BanData:
        """Gets a ban

        See the `documentation <https://discord.dev/resources/guild#get-guild-ban>`__

        .. note::
            This requires the ``BAN_MEMBERS`` permission..

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of the guild to get the ban from
        user_id:
            The user to get ban info for
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route("GET", "/guilds/{guild_id}/bans/{user_id}", guild_id=guild_id, user_id=user_id)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def create_guild_ban(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        delete_message_days: int | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Bans a user from a guild

        Read the `documentation <https://discord.dev/resources/guild#create-guild-ban>`__

        .. note::
            This requires the ``BAN_MEMBERS`` permission and that the bot is higher in the role hierarchy than the member you are trying to kick

        Parameters
        ----------
        authentication:
            The auth info
        guild_id:
            The id of the guild to ban the member from
        user_id:
            The id of the user to ban
        delete_message_days:
            Delete all messages younger than delete_message_days days sent by the user.
        reason:
            The reason to put in the audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("PUT", "/guilds/{guild_id}/bans/{user_id}", guild_id=guild_id, user_id=user_id)

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        payload: JsonCompatible = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if delete_message_days is not UNDEFINED:
            payload["delete_message_days"] = delete_message_days

        await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            global_priority=global_priority,
            json=payload,
        )

    async def remove_guild_ban(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Unbans a user from a guild

        Read the `documentation <https://discord.dev/resources/guild#remove-guild-ban>`__

        .. note::
            This requires the ``BAN_MEMBERS`` permission and that the bot is higher in the role hierarchy than the member you are trying to kick

        Parameters
        ----------
        authentication:
            The auth info
        guild_id:
            The id of the guild to unban the member from
        user_id:
            The id of the user to unban
        reason:
            The reason to put in the audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("DELETE", "/guilds/{guild_id}/bans/{user_id}", guild_id=guild_id, user_id=user_id)

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            global_priority=global_priority,
        )

    async def get_guild_roles(
        self, authentication: BotAuthentication, guild_id: Snowflake, *, global_priority: int = 0
    ) -> list[RoleData]:
        """Gets all roles in a guild

        Read the `documentation <https://discord.dev/resources/guild#get-guild-roles>`__

        Parameters
        ----------
        authentication:
            The auth info
        guild_id:
            The guild to get the roles from
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[discord_typings.RoleData]
            The roles in the guild
        """
        route = Route("GET", "/guilds/{guild_id}/roles", guild_id=guild_id)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    @overload
    async def create_guild_role(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        name: str | UndefinedType = UNDEFINED,
        permissions: str | UndefinedType = UNDEFINED,
        color: int | UndefinedType = UNDEFINED,
        hoist: bool | UndefinedType = UNDEFINED,
        mentionable: bool | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> RoleData:
        ...

    @overload
    async def create_guild_role(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        name: str | UndefinedType = UNDEFINED,
        permissions: str | UndefinedType = UNDEFINED,
        color: int | UndefinedType = UNDEFINED,
        hoist: bool | UndefinedType = UNDEFINED,
        icon: str | None,
        mentionable: bool | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> RoleData:
        ...

    @overload
    async def create_guild_role(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        name: str | UndefinedType = UNDEFINED,
        permissions: str | UndefinedType = UNDEFINED,
        color: int | UndefinedType = UNDEFINED,
        hoist: bool | UndefinedType = UNDEFINED,
        unicode_emoji: str | None,
        mentionable: bool | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> RoleData:
        ...

    async def create_guild_role(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        name: str | UndefinedType = UNDEFINED,
        permissions: str | UndefinedType = UNDEFINED,
        color: int | UndefinedType = UNDEFINED,
        hoist: bool | UndefinedType = UNDEFINED,
        icon: str | None | UndefinedType = UNDEFINED,
        unicode_emoji: str | None | UndefinedType = UNDEFINED,
        mentionable: bool | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> RoleData:
        """Creates a role

        .. note::
            This requires the ``MANAGE_ROLES`` permission

        Parameters
        ----------
        authentication:
            The auth info
        guild_id:
            The guild to create the role in
        name:
            The name of the role
        permissions:
            The permissions the role has
        color:
            The color of the role
        hoist:
            If the role will be split into a seperate section in the member list.
        icon:
            Base64 encoded image data of the role icon

            .. note::
                This requires the ``ROLE_ICONS`` guild feature.
        unicode_emoji:
            A unicode emoji to use for the role icon.

            .. note::
                This requires the ``ROLE_ICONS`` guild feature.
        mentionable:
            Whether the role can be mentioned by members without the ``MENTION_EVERYONE`` permission.
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.RoleData
            The role that was created
        """
        route = Route("POST", "/guilds/{guild_id}/roles", guild_id=guild_id)

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        payload: JsonCompatible = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name
        if permissions is not UNDEFINED:
            payload["permissions"] = permissions
        if color is not UNDEFINED:
            payload["color"] = color
        if hoist is not UNDEFINED:
            payload["hoist"] = hoist
        if icon is not UNDEFINED:
            payload["icon"] = icon
        if unicode_emoji is not UNDEFINED:
            payload["unicode_emoji"] = unicode_emoji
        if mentionable is not UNDEFINED:
            payload["mentionable"] = mentionable

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_guild_role_positions(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *position_updates: RolePositionData,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> list[RoleData]:
        """Modifies role positions

        .. note::
            This requires the ``MANAGE_ROLES`` permission

        Parameters
        ----------
        authentication:
            The auth info
        guild_id:
            The guild to modify role positions in
        position_updates:
            The positions to update
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("GET", "/guilds/{guild_id}/roles", guild_id=guild_id)

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route, ratelimit_key=authentication.rate_limit_key, json=position_updates, global_priority=global_priority
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    @overload
    async def modify_guild_role(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        role_id: Snowflake,
        *,
        name: str | UndefinedType = UNDEFINED,
        permissions: str | UndefinedType = UNDEFINED,
        color: int | UndefinedType = UNDEFINED,
        hoist: bool | UndefinedType = UNDEFINED,
        icon: str | None,
        mentionable: bool | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> RoleData:
        ...

    @overload
    async def modify_guild_role(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        role_id: Snowflake,
        *,
        name: str | UndefinedType = UNDEFINED,
        permissions: str | UndefinedType = UNDEFINED,
        color: int | UndefinedType = UNDEFINED,
        hoist: bool | UndefinedType = UNDEFINED,
        unicode_emoji: str | None,
        mentionable: bool | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> RoleData:
        ...

    async def modify_guild_role(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        role_id: Snowflake,
        *,
        name: str | UndefinedType = UNDEFINED,
        permissions: str | UndefinedType = UNDEFINED,
        color: int | UndefinedType = UNDEFINED,
        hoist: bool | UndefinedType = UNDEFINED,
        icon: str | None | UndefinedType = UNDEFINED,
        unicode_emoji: str | None | UndefinedType = UNDEFINED,
        mentionable: bool | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> RoleData:
        """Modifies a role

        .. note::
            This requires the ``MANAGE_ROLES`` permission

        Parameters
        ----------
        authentication:
            The auth info
        guild_id:
            The guild where the role is located in
        role_id:
            The role to modify
        name:
            The name of the role
        permissions:
            The permissions the role has
        color:
            The color of the role
        hoist:
            If the role will be split into a seperate section in the member list.
        icon:
            Base64 encoded image data of the role icon

            .. note::
                This requires the ``ROLE_ICONS`` guild feature.
        unicode_emoji:
            A unicode emoji to use for the role icon.

            .. note::
                This requires the ``ROLE_ICONS`` guild feature.
        mentionable:
            Whether the role can be mentioned by members without the ``MENTION_EVERYONE`` permission.
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.RoleData
            The updated role
        """
        route = Route("PATCH", "/guilds/{guild_id}/roles/{role_id}", guild_id=guild_id, role_id=role_id)

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        payload: JsonCompatible = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name
        if permissions is not UNDEFINED:
            payload["permissions"] = permissions
        if color is not UNDEFINED:
            payload["color"] = color
        if hoist is not UNDEFINED:
            payload["hoist"] = hoist
        if icon is not UNDEFINED:
            payload["icon"] = icon
        if unicode_emoji is not UNDEFINED:
            payload["unicode_emoji"] = unicode_emoji
        if mentionable is not UNDEFINED:
            payload["mentionable"] = mentionable

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_guild_role(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        role_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Deletes a channel.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the role to delete.
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route("DELETE", "/guilds/{guild_id}/roles/{role_id}", guild_id=guild_id, role_id=role_id)
        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        await self._request(
            route, headers=headers, ratelimit_key=authentication.rate_limit_key, global_priority=global_priority
        )

    async def get_guild_prune_count(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        days: int | UndefinedType = UNDEFINED,
        include_roles: list[str] | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> dict[str, Any]:  # TODO: Replace return type
        """Gets the amount of members that would be pruned

        .. note::
            This requires the ``KICK_MEMBERS`` permission

        Parameters
        ----------
        authentication:
            The auth info
        guild_id:
            The guild to get the prune count for
        days:
            How many days a user has to be inactive for to get included in the prune count

            .. note::
                If this is :data:`UNDEFINED`, this will default to 7.
        include_roles:
            IDs of roles to be pruned aswell as the default role.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("GET", "/guilds/{guild_id}/prune", guild_id=guild_id)

        query = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)

        if days is not UNDEFINED:
            query["days"] = days
        if include_roles is not UNDEFINED:
            query["include_roles"] = ",".join(include_roles)

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            query=query,
            ratelimit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def begin_guild_prune(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        days: int | UndefinedType = UNDEFINED,
        compute_prune_count: bool | UndefinedType = UNDEFINED,
        include_roles: list[str] | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> dict[str, Any]:  # TODO: Replace return type
        """Gets the amount of members that would be pruned

        .. note::
            This requires the ``KICK_MEMBERS`` permission

        Parameters
        ----------
        authentication:
            The auth info
        guild_id:
            The guild to get the prune count for
        days:
            How many days a user has to be inactive for to get included in the prune count

            .. note::
                If this is :data:`UNDEFINED`, this will default to 7.
        include_roles:
            IDs of roles to be pruned aswell as the default role.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("GET", "/guilds/{guild_id}/prune", guild_id=guild_id)

        query = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)

        if days is not UNDEFINED:
            query["days"] = days
        if compute_prune_count is not UNDEFINED:
            query["compute_prune_count"] = compute_prune_count
        if include_roles is not UNDEFINED:
            query["include_roles"] = ",".join(include_roles)

        headers = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)

        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            query=query,
            ratelimit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_voice_regions(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> list[VoiceRegionData]:
        """Gets voice regions for a guild.

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of guild to get voice regions from
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route("GET", "/guilds/{guild_id}/regions", guild_id=guild_id)

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            ratelimit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_invites(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> list[InviteMetadata]:
        """Gets all guild invites

        .. note::
            This requires the ``MANAGE_GUILD`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of guild to get invites for
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route("GET", "/guilds/{guild_id}/invites", guild_id=guild_id)

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            ratelimit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_integrations(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> list[IntegrationData]:
        """Gets guild integrations

        .. note::
            This requires the ``MANAGE_GUILD`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of guild to get integrations for
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route("GET", "/guilds/{guild_id}/invites", guild_id=guild_id)

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            ratelimit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_guild_integration(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        guild_id: Snowflake,
        integration_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Deletes a integration

        .. note::
            This will delete any associated webhooks and kick any associated bots.

        .. note::
            This requires the ``MANAGE_GUILD`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of the guild where the integration is located in
        integration_id:
            The id of the integration to delete
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route(
            "DELETE",
            "/guilds/{guild_id}/integrations/{integration_id}",
            guild_id=guild_id,
            integration_id=integration_id,
        )
        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        await self._request(
            route, headers=headers, ratelimit_key=authentication.rate_limit_key, global_priority=global_priority
        )

    async def get_guild_widget_settings(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> GuildWidgetSettingsData:
        """Gets widget settings for a guild

        .. note::
            This requires the ``MANAGE_GUILD`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of guild to get the widget settings for
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route("GET", "/guilds/{guild_id}/widget", guild_id=guild_id)

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            ratelimit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_guild_widget_settings(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        enabled: bool | UndefinedType = UNDEFINED,
        channel_id: Snowflake | None | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> GuildWidgetSettingsData:
        """Modifies a guilds widget settings

        .. note::
            This requires the ``MANAGE_GUILD`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of guild to modify the widget for
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route("PATCH", "/guilds/{guild_id}/widget", guild_id=guild_id)

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        payload: JsonCompatible = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if enabled is not UNDEFINED:
            payload["enabled"] = enabled
        if channel_id is not UNDEFINED:
            payload["channel_id"] = channel_id

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            ratelimit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_widget(
        self,
        guild_id: Snowflake,
    ) -> GuildWidgetData:
        """Gets a widget from a guild id

        Parameters
        ----------
        guild_id:
            The id of guild to get the widget for.
        """

        route = Route("GET", "/guilds/{guild_id}/widget.json", guild_id=guild_id, ignore_global=True)

        r = await self._request(
            route,
            ratelimit_key=None,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_vanity_url(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> GuildWidgetSettingsData:
        """Gets the vanity invite from a guild

        .. note::
            This requires the ``MANAGE_GUILD`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of guild to get the vanity invite from
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route("GET", "/guilds/{guild_id}/vanity-url", guild_id=guild_id)

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            ratelimit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Implement get guild widget image

    async def get_guild_welcome_screen(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> WelcomeScreenData:
        """Gets the welcome screen for a guild

        .. note::
            This requires the ``MANAGE_GUILD`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of guild to get the welcome screen for
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route("GET", "/guilds/{guild_id}/welcome-screen", guild_id=guild_id)

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            ratelimit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_guild_welcome_screen(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        enabled: bool | None | UndefinedType = UNDEFINED,
        welcome_channels: list[WelcomeChannelData] | None | UndefinedType = UNDEFINED,
        description: str | None | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> WelcomeScreenData:
        """Modifies a guilds welcome screen

        .. note::
            This requires the ``MANAGE_GUILD`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of guild to modify the welcome screen for
        enabled:
            Whether the welcome screen is enabled
        welcome_channels:
            The channels to show on the welcome screen
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("PATCH", "/guilds/{guild_id}/welcome-screen", guild_id=guild_id)

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        payload: JsonCompatible = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if enabled is not UNDEFINED:
            payload["enabled"] = enabled
        if welcome_channels is not UNDEFINED:
            payload["welcome_channels"] = welcome_channels
        if description is not UNDEFINED:
            payload["description"] = description

        r = await self._request(
            route,
            headers=headers,
            ratelimit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_current_user_voice_state(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        channel_id: Snowflake,
        *,
        suppress: bool | UndefinedType = UNDEFINED,
        request_to_speak_timestamp: str | None | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Modifies the voice state of the bot

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of guild to get the vanity invite from
        channel_id:
            The id of a stage channel the bot is in
        suppress:
            Whether to be in the audience.

            .. note::
                You need the ``MUTE_MEMBERS`` if you want to set this to :data:`False`, however no permission is required to set it to :data:`False`.
        request_to_speak_timestamp:
            A timestamp of when a user requested to speak.

            .. note::
                There is no validation if this is in the future or the past.

            .. note::
                You need the ``REQUEST_TO_SPEAK`` to set this to a non-:data:`None` value, however setting it to :data:`None` requires no permission.
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route("PATCH", "/guilds/{guild_id}/voice-states/@me", guild_id=guild_id)

        payload: JsonCompatible = {"channel_id": channel_id}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if suppress is not UNDEFINED:
            payload["suppress"] = suppress
        if request_to_speak_timestamp is not UNDEFINED:
            payload["request_to_speak_timestamp"] = request_to_speak_timestamp

        await self._request(
            route,
            headers={"Authorization": str(authentication)},
            json=payload,
            ratelimit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

    async def modify_user_voice_state(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        channel_id: Snowflake,
        user_id: Snowflake,
        *,
        suppress: bool | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Modifies the voice state of the bot

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of guild to get the vanity invite from
        channel_id:
            The id of a stage channel the user is in
        user_id:
            The user to modify the voice state for
        suppress:
            Whether to be in the audience.

            .. note::
                You need the ``MUTE_MEMBERS`` if you want to set this to :data:`False`, however no permission is required to set it to :data:`False`.
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route("PATCH", "/guilds/{guild_id}/voice-states/{user_id}", guild_id=guild_id, user_id=user_id)

        payload: JsonCompatible = {"channel_id": channel_id}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if suppress is not UNDEFINED:
            payload["suppress"] = suppress

        await self._request(
            route,
            headers={"Authorization": str(authentication)},
            json=payload,
            ratelimit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

    # Scheduled events

    async def list_scheduled_events_for_guild(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        with_user_count: bool | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> list[GuildScheduledEventData]:  # TODO: Narrow type more with a overload with_user_count
        """Gets all scheduled events for a guild

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of guild scheduled events from
        with_user_count:
            Include :attr:`discord_typings.GuildScheduledEventData.user_count`
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("GET", "/guilds/{guild_id}/scheduled-events", guild_id=guild_id)

        query = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if with_user_count is not UNDEFINED:
            query["with_user_count"] = with_user_count

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            ratelimit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    @overload
    async def create_guild_scheduled_event(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        name: str,
        privacy_level: Literal[2],
        scheduled_start_time: str,
        entity_type: Literal[3],
        *,
        entity_metadata: GuildScheduledEventEntityMetadata,
        scheduled_end_time: str,
        description: str | UndefinedType = UNDEFINED,
        image: str | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> GuildScheduledEventData:
        ...

    @overload
    async def create_guild_scheduled_event(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        name: str,
        privacy_level: Literal[2],
        scheduled_start_time: str,
        entity_type: Literal[1, 2],
        *,
        channel_id: Snowflake,
        scheduled_end_time: str | UndefinedType = UNDEFINED,
        description: str | UndefinedType = UNDEFINED,
        image: str | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> GuildScheduledEventData:
        ...

    async def create_guild_scheduled_event(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        name: str,
        privacy_level: Literal[2],
        scheduled_start_time: str,
        entity_type: Literal[1, 2, 3],
        *,
        channel_id: Snowflake | None | UndefinedType = UNDEFINED,
        entity_metadata: GuildScheduledEventEntityMetadata | UndefinedType = UNDEFINED,
        scheduled_end_time: str | UndefinedType = UNDEFINED,
        description: str | UndefinedType = UNDEFINED,
        image: str | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> GuildScheduledEventData:
        """Create a scheduled event

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of guild to create the scheduled event in
        name:
            The name of the event
        privacy_level:
            Who can join the event

            .. note::
                This can currently only be ``2``
        scheduled_start_time:
            A ISO8601 timestamp of when the event should start
        entity_type:
            What the event points to.

            **Types:**
            - ``1``: A stage channel
            - ``2`` A voice channnel
            - ``3`` A external link
        channel_id:
            The channel the event is for
        entity_metadata:
            Metadata about the event spesific to what ``entity_type`` you chose.
        scheduled_end_time:
            A ISO8601 timestamp of when the event ends.
        description:
            The description of the event.
        image:
            A base64 encoded image to use as a cover.
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.GuildScheduledEventData
            The scheduled event that was created
        """
        route = Route("POST", "/guilds/{guild_id}/scheduled-events", guild_id=guild_id)

        payload: JsonCompatible = {
            "name": name,
            "privacy_level": privacy_level,
            "scheduled_start_time": scheduled_start_time,
            "entity_type": entity_type,
        }

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if channel_id is not UNDEFINED:
            payload["channel_id"] = channel_id
        if entity_metadata is not UNDEFINED:
            payload["entity_metadata"] = entity_metadata
        if scheduled_end_time is not UNDEFINED:
            payload["scheduled_end_time"] = scheduled_end_time
        if description is not UNDEFINED:
            payload["description"] = description
        if image is not UNDEFINED:
            payload["image"] = image

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            headers=headers,
            json=payload,
            ratelimit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_scheduled_event(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        guild_scheduled_event_id: Snowflake,
        *,
        with_user_count: bool | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> GuildScheduledEventData:  # TODO: Narrow type more with a overload with_user_count
        """Gets a scheduled event by id

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of guild scheduled events from
        guild_scheduled_event_id:
            The id of the event to get.
        with_user_count:
            Include :attr:`discord_typings.GuildScheduledEventData.user_count`
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "GET",
            "/guilds/{guild_id}/scheduled-events/{guild_scheduled_event_id}",
            guild_id=guild_id,
            guild_scheduled_event_id=guild_scheduled_event_id,
        )

        query = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if with_user_count is not UNDEFINED:
            query["with_user_count"] = with_user_count

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            ratelimit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Add Modify Guild Scheduled Event

    async def delete_guild_scheduled_event(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        guild_id: Snowflake,
        guild_scheduled_event_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Deletes scheduled event.

        .. note::
            This requires the ``MANAGE_EVENTS`` guild permission.

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of the guild where the scheduled event is in
        guild_scheduled_event_id:
            The id of the event to delete.
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route(
            "DELETE",
            "/guilds/{guild_id}/scheduled-events/{guild_scheduled_event_id}",
            guild_id=guild_id,
            guild_scheduled_event_id=guild_scheduled_event_id,
        )
        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        await self._request(
            route, headers=headers, ratelimit_key=authentication.rate_limit_key, global_priority=global_priority
        )

    # TODO: Add Get Guild Scheduled Event Users
    async def get_guild_template(
        self, authentication: BotAuthentication, template_code: str, *, global_priority: int = 0
    ) -> GuildTemplateData:
        """Gets a template by code

        See the `documentation <https://discord.dev/resources/guild-template#get-guild-templates>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        template_code:
            The template code to get the template from
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.GuildTemplateData
            The template you requested
        """
        route = Route("GET", "/guilds/templates/{template_code}", template_code=template_code)
        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def create_guild_from_guild_template(
        self,
        authentication: BotAuthentication,
        template_code: str,
        name: str,
        *,
        icon: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> GuildData:
        """Creates a guild from a template

        See the `documentation <https://discord.dev/resources/guild-template#create-guild-from-guild-template>`__

        .. warning::
            This will fail if the bot is in more than 10 guilds.

        Parameters
        ----------
        authentication:
            Authentication info.
        template_code:
            The template code to create the guild from
        name:
            The name of the guild
        icon:
            Base64 encoded 128x128px image to set the guild icon to.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.GuildData
            The guild created
        """
        route = Route("POST", "/guilds/templates/{template_code}", template_code=template_code)

        payload: JsonCompatible = {"name": name}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if icon is not UNDEFINED:
            payload["icon"] = icon

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_templates(
        self, authentication: BotAuthentication, guild_id: Snowflake, *, global_priority: int = 0
    ) -> list[GuildTemplateData]:
        """Gets all templates in a guild

        See the `documentation <https://discord.dev/resources/guild-template#get-guild-templates>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The guild id to get templates from
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[:class:`discord_typings.GuildTemplateData`]
            The templates in the guild
        """
        route = Route("GET", "/guilds/{guild_id}/templates", guild_id=guild_id)
        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def create_guild_template(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        name: str,
        *,
        description: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> GuildTemplateData:  # TODO: Narrow typing to overload description.
        """Creates a template from a guild

        See the `documentation <https://discord.dev/resources/guild-template#create-guild-template>`__

        .. note::
            This requires the ``MANAGE_GUILD`` permission


        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The guild to create a template from
        name:
            The name of the template

            .. note::
                This has to be between ``2`` and ``100`` characters long.
        description:
            The description of the template

            .. note::
                This has to be between ``0`` and ``120`` characters long.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.GuildData
            The guild created
        """
        route = Route("POST", "/guilds/{guild_id}/templates", guild_id=guild_id)

        payload: JsonCompatible = {"name": name}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if description is not UNDEFINED:
            payload["description"] = description

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def sync_guild_template(
        self, authentication: BotAuthentication, guild_id: Snowflake, template_code: str, *, global_priority: int = 0
    ) -> None:
        """Updates a template with the updated-guild.

        See the `documentation <https://discord.dev/resources/guild-template#sync-guild-templates>`__

        .. note::
            This requires the ``MANAGE_GUILD`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The guild id of the template
        template_code:
            The template to sync
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "PUT", "/guilds/{guild_id}/templates/{template_code}", guild_id=guild_id, template_code=template_code
        )

        await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_guild_template(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        template_code: str,
        *,
        name: str | UndefinedType = UNDEFINED,
        description: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Updates a template.

        See the `documentation <https://discord.dev/resources/guild-template#modify-guild-templates>`__

        .. note::
            This requires the ``MANAGE_GUILD`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The guild id of the template
        template_code:
            The code of the template to modify
        name:
            What to change the template name to

            .. note::
                This has to be between ``2`` and ``100`` characters long.
        description:
            What to change the template description to.

            .. note::
                This has to be between ``0`` and ``120`` characters long.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "PATCH", "/guilds/{guild_id}/templates/{template_code}", guild_id=guild_id, template_code=template_code
        )

        payload: JsonCompatible = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name
        if description is not UNDEFINED:
            payload["description"] = description

        await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_guild_template(
        self, authentication: BotAuthentication, guild_id: Snowflake, template_code: str, *, global_priority: int = 0
    ) -> GuildTemplateData:
        """Deletes a template

        See the `documentation <https://discord.dev/resources/guild-template#delete-guild-template>`__

        .. note::
            This requires the ``MANAGE_GUILD`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The guild id where the template is located
        template_code:
            The code of the template to delete
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.GuildTemplateData
            The deleted template
        """
        route = Route(
            "DELETE", "/guilds/{guild_id}/templates/{template_code}", guild_id=guild_id, template_code=template_code
        )

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # Invite
    async def get_invite(
        self, authentication: BotAuthentication, invite_code: str, *, global_priority: int = 0
    ) -> InviteData:
        """Gets a invite from a invite code

        See the `documentation <https://discord.dev/resources/invite#get-invite>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        invite_code:
            The code of the invite to get
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.InviteData
            The invite that was fetched
        """
        route = Route("GET", "/invites/{invite_code}", invite_code=invite_code)
        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_invite(
        self, authentication: BotAuthentication, invite_code: str, *, global_priority: int = 0
    ) -> InviteData:
        """Gets a invite from a invite code

        See the `documentation <https://discord.dev/resources/invite#get-invite>`__

        .. note::
            This requires the ``MANAGE_CHANNELS`` permission in the channel the invite is from or the ``MANAGE_GUILD`` permission.

        .. note::
            This will dispatch a ``INVITE_DELETE`` event.

        Parameters
        ----------
        authentication:
            Authentication info.
        invite_code:
            The code of the invite to delete
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.InviteData
            The invite that was deleted
        """
        route = Route("DELETE", "/invites/{invite_code}", invite_code=invite_code)
        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # Stage instance
    async def create_stage_instance(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        topic: str,
        *,
        privacy_level: Literal[1, 2] | UndefinedType = UNDEFINED,
        send_start_notification: bool | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> StageInstanceData:
        """Creates a stage instance

        See the `documentation <https://discord.dev/resources/stage-instance#create-stage-instance>`__

        .. note::
            This requires the ``MANAGE_CHANNELS``, ``MUTE_MEMBERS`` and ``MOVE_MEMBERS`` permission.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the stage channel to create a stage instance in
        topic:
            The topic of the stage instance

            .. note::
                This has to be between ``1`` and ``120`` characters.
        privacy_level:
            The privacy level of the stage instance.

            .. note::
                This will default to ``2``/Guild only if not provided.

            **Possible values**
            - ``1``: Public (deprecated)
            - ``2`` Guild only
        send_start_notification:
            If you should send a notification to all members in the guild

            .. note::
                Setting this to :data:`True` requires the ``MENTION_EVERYONE`` permission.
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.StageInstanceData
            The stage instance that was created.
        """
        route = Route("POST", "/stage-instances")

        payload: JsonCompatible = {"channel_id": channel_id, "topic": topic}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if privacy_level is not UNDEFINED:
            payload["privacy_level"] = privacy_level
        if send_start_notification is not UNDEFINED:
            payload["send_start_notification"] = send_start_notification

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_stage_instance(
        self, authentication: BotAuthentication, channel_id: Snowflake, *, global_priority: int = 0
    ) -> StageInstanceData:
        """Gets a stage instance from a stage channel id

        See the `documentation <https://discord.dev/resources/stage-instance#get-stage-instance>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The code of the invite to get
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.StageInstanceData
            The stage instance that was fetched.
        """
        route = Route("GET", "/stage-instances/{channel_id}", channel_id=channel_id)
        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_stage_instance(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        *,
        topic: str | UndefinedType = UNDEFINED,
        privacy_level: Literal[1, 2] | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> StageInstanceData:
        """Modifies a stage instance

        See the `documentation <https://discord.dev/resources/stage-instance#modify-stage-instance>`__

        .. note::
            This requires the ``MANAGE_CHANNELS``, ``MUTE_MEMBERS`` and ``MOVE_MEMBERS`` permission.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the stage channel to modify a stage instance in
        topic:
            The topic of the stage instance

            .. note::
                This has to be between ``1`` and ``120`` characters.
        privacy_level:
            The privacy level of the stage instance.

            **Possible values**
            - ``1``: Public (deprecated)
            - ``2`` Guild only
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.StageInstanceData
            The updated stage instance
        """
        route = Route("PATCH", "/stage-instances/{channel_id}", channel_id=channel_id)

        payload: JsonCompatible = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if topic is not UNDEFINED:
            payload["topic"] = topic
        if privacy_level is not UNDEFINED:
            payload["privacy_level"] = privacy_level

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_stage_instance(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Modifies a stage instance

        See the `documentation <https://discord.dev/resources/stage-instance#delete-stage-instance>`__

        .. note::
            This requires the ``MANAGE_CHANNELS``, ``MUTE_MEMBERS`` and ``MOVE_MEMBERS`` permission.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the stage channel to delete the stage instance for.
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("DELETE", "/stage-instances/{channel_id}", channel_id=channel_id)

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # Sticker
    async def get_sticker(
        self, authentication: BotAuthentication, sticker_id: Snowflake, *, global_priority: int = 0
    ) -> StickerData:
        """Gets a sticker from a sticker id.

        See the `documentation <https://discord.dev/resources/sticker#get-sticker>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        sticker_id:
            The id of the sticker to get.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.StickerData
            The sticker that was fetched
        """
        route = Route("GET", "/stickers/{sticker_id}", sticker_id=sticker_id)
        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_nitro_sticker_packs(
        self, *, global_priority: int = 0
    ) -> dict[Literal["sticker_packs"], list[StickerPackData]]:
        """Gets all nitro sticker packs

        See the `documentation <https://discord.dev/resources/sticker#list-nitro-sticker-packs>`__

        Parameters
        ----------
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("GET", "/sticker-packs")
        r = await self._request(
            route,
            ratelimit_key=None,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def list_guild_stickers(
        self, authentication: BotAuthentication, guild_id: Snowflake, *, global_priority: int = 0
    ) -> list[StickerData]:
        """Gets all custom stickers added by a guild

        See the `documentation <https://discord.dev/resources/sticker#list-guild-stickers>`__

        .. note::
            The ``user`` field will be provided if you have the ``MANAGE_EMOJIS_AND_STICKERS`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of guild to get stickers from
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[discord_typings.StickerData]
            The stickers in the guild
        """
        route = Route("GET", "/guilds/{guild_id}/stickers", guild_id=guild_id)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_sticker(
        self, authentication: BotAuthentication, guild_id: Snowflake, sticker_id: str | int, *, global_priority: int = 0
    ) -> StickerData:
        """Get a custom sticker

        See the `documentation <https://discord.dev/resources/sticker#get-guild-sticker>`__

        .. note::
            The ``user`` field will be provided if you have the ``MANAGE_EMOJIS_AND_STICKERS`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of guild to get the sticker from
        sticker_id:
            The sticker to get
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[discord_typings.StickerData]
            The stickers in the guild
        """
        route = Route("GET", "/guilds/{guild_id}/stickers/{sticker_id}", guild_id=guild_id, sticker_id=sticker_id)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Add create guild sticker

    async def modify_guild_sticker(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        sticker_id: Snowflake,
        *,
        name: str | UndefinedType = UNDEFINED,
        description: str | UndefinedType = UNDEFINED,
        tags: list[str] | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> StickerData:  # TODO: Make StickerData always include user
        """Modifies a sticker

        See the `documentation <https://discord.dev/resources/sticker#modify-guild-sticker>`__

        .. note::
            This requires the ``MANAGE_EMOJIS_AND_STICKERS`` permission.

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of the guild where the sticker is in.
        sticker_id:
            The id of the sticker to update
        name:
            The name of the sticker.

            .. note::
                This has to be between ``2`` and ``30`` characters
        description:
            The description of the sticker

            .. note::
                This has to be between ``2`` and ``100`` characters
        tags:
            Autocomplete/suggestion tags for the sticker (max 200 characters)
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.StageInstanceData
            The updated stage instance
        """
        route = Route("PATCH", "/guilds/{guild_id}/stickers/{sticker_id}", guild_id=guild_id, sticker_id=sticker_id)

        payload: JsonCompatible = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name
        if description is not UNDEFINED:
            payload["description"] = description
        if tags is not UNDEFINED:
            payload["tags"] = tags

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_guild_sticker(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        sticker_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Modifies a stage instance

        See the `documentation <https://discord.dev/resources/stage-instance#delete-stage-instance>`__

        .. note::
            This requires the ``MANAGE_CHANNELS``, ``MUTE_MEMBERS`` and ``MOVE_MEMBERS`` permission.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the stage channel to delete the stage instance for.
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("DELETE", "/guilds/{guild_id}/stickers/{sticker_id}", guild_id=guild_id, sticker_id=sticker_id)

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # User
    async def get_current_user(
        self, authentication: BotAuthentication | BearerAuthentication, *, global_priority: int = 0
    ) -> UserData:
        """Gets the current user

        See the `documentation <https://discord.dev/resources/user#get-current-user>`__

        .. note::
            If you are using :class:`BearerAuthentication` you need the ``IDENTIFY`` scope.

            :attr:`UserData.email` will only be provided if you have the ``EMAIL`` scope.

        Parameters
        ----------
        authentication:
            Authentication info.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.UserData
            The current user
        """
        route = Route("GET", "/users/@me")

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_user(
        self, authentication: BotAuthentication | BearerAuthentication, user_id: Snowflake, *, global_priority: int = 0
    ) -> UserData:
        """Gets a user by id

        See the `documentation <https://discord.dev/resources/user#get-user>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        user_id:
            The id of the user to fetch
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.UserData
            The user you fetched
        """
        route = Route("GET", "/users/{user_id}", user_id=user_id)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_current_user(
        self,
        authentication: BotAuthentication,
        *,
        username: str | UndefinedType = UNDEFINED,
        avatar: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> UserData:
        """Modifies the current user

        See the `documentation <https://discord.dev/resources/user#modify-current-user>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        username:
            The username to update to
        avatar:
            Base64 encoded image to change the current users avatar to
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.UserData
            The updated user
        """
        route = Route("PATCH", "/users/@me")

        payload: JsonCompatible = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if username is not UNDEFINED:
            payload["username"] = username
        if avatar is not UNDEFINED:
            payload["avatar"] = avatar

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_current_user_guilds(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        *,
        before: Snowflake,
        after: Snowflake,
        limit: int,
        global_priority: int = 0,
    ) -> list[GuildData]:  # TODO: Replace with partial guild data
        """Gets the guilds the current user is in

        See the `documentation <https://discord.dev/resources/user#get-current-user-guilds>`__

        .. note::
            If you are using :class:`BearerAuthentication` you need the ``guilds`` scope.

        Parameters
        ----------
        authentication:
            Authentication info.
        before:
            Get guilds before this id

            .. note::
                This does not have to be a valid id.
        after:
            Get guilds after this id

            .. note::
                This does not have to be a valid id.
        limit:
            The max amount of guilds to return

            .. note::
                This has to be between ``1`` and ``200``
            .. note::
                This defaults to ``200``
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[discord_typings.PartialGuildData]
            The guilds fetched
        """
        route = Route("GET", "/users/@me/guilds")

        query = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if before is not UNDEFINED:
            query["before"] = before
        if after is not UNDEFINED:
            query["after"] = after
        if limit is not UNDEFINED:
            query["limit"] = limit

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            query=query,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_current_user_guild_member(
        self, authentication: BotAuthentication | BearerAuthentication, guild_id: Snowflake, *, global_priority: int = 0
    ) -> GuildMemberData:
        """Gets the current users member in a guild

        See the `documentation <https://discord.dev/resources/user#get-current-user-guild-member>`__

        .. note::
            This requires the ``guilds.members.read`` scope

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of the guild to get the member in
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.GuildMemberData
            The current member
        """
        route = Route("GET", "/users/@me/guilds/{guild_id}/member", guild_id=guild_id)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def leave_guild(
        self, authentication: BotAuthentication, guild_id: Snowflake, *, global_priority: int = 0
    ) -> None:
        """Leave a guild

        See the `documentation <https://discord.dev/resources/user#leave-guild>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of the guild to leave
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.UserData
            The current user
        """
        route = Route("DELETE", "/users/@me/guilds/{guild_id}", guild_id=guild_id)

        await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

    async def create_dm(
        self, authentication: BotAuthentication, recipient_id: Snowflake, *, global_priority: int = 0
    ) -> DMChannelData:
        """Creates a DM channel

        See the `documentation <https://discord.dev/resources/user#create-dm>`__

        .. warning::
            You should not use this endpoint to DM everyone in a server about something. DMs should generally be initiated by a user action.

            If you open a significant amount of DMs too quickly, your bot may be blocked from opening new ones.

        Parameters
        ----------
        authentication:
            Authentication info.
        recipient_id:
            The id of user to DM.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.DMChannelData
            The DM channel created/fetched.
        """
        route = Route("POST", "/users/@me/channels")

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            json={"recipient_id": recipient_id},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Add Create Group DM

    async def get_user_connections(
        self, authentication: BearerAuthentication, *, global_priority: int = 0
    ) -> list[dict[str, Any]]:  # TODO: This should be more strict
        """Gets the users connections

        See the `documentation <https://discord.dev/resources/user#get-user-connections>`__

        .. note::
            This requires the ``connections`` scope

        Parameters
        ----------
        authentication:
            Authentication info.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.GuildMemberData
            The current member
        """
        route = Route("GET", "/users/@me/connections")

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # Voice
    async def list_voice_regions(
        self, authentication: BotAuthentication, *, global_priority: int = 0
    ) -> list[VoiceRegionData]:  # TODO: This should be more strict
        """Gets the users connections

        See the `documentation <https://discord.dev/resources/voice#list-voice-regions>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[discord_typings.VoiceRegionData]
            Voice regions
        """
        route = Route("GET", "/voice/regions")

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # Webhook
    async def create_webhook(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        name: str,
        *,
        avatar: str | None | UndefinedType = UNDEFINED,
        reason: str,
        global_priority: int = 0,
    ) -> WebhookData:
        """Creates a webhook

        See the `documentation <https://discord.dev/resources/webhook#create-webhook>`__

        .. note::
            This requires the ``MANAGE_WEBHOOKS`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to create a webhook in
        name:
            The name of the webhook

            .. note::
                This has to be between ``1`` and ``80`` characters.

                It has to follow the `Discord nickname restrictions <https://discord.dev/resources/user#usernames-and-nicknames>`__ (with the exception of the length limit.)
        avatar:
            Base64 encoded image avatar to use as the default avatar
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.WebhookData
            The webhook that was created
        """
        route = Route("POST", "/channels/{channel_id}/webhooks", channel_id=channel_id)

        payload: JsonCompatible = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name
        if avatar is not UNDEFINED:
            payload["avatar"] = avatar

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_channel_webhooks(
        self, authentication: BotAuthentication, channel_id: Snowflake, *, global_priority: int = 0
    ) -> list[WebhookData]:
        """Gets all webhooks in a channel

        See the `documentation <https://discord.dev/resources/webhook#get-channel-webhooks>`__

        .. note::
            This requires the ``MANAGE_WEBHOOKS`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to get webhooks from
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[discord_typings.WebhookData]
            The webhooks in the channel
        """
        route = Route("GET", "/channels/{channel_id}/webhooks", channel_id=channel_id)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_webhooks(
        self, authentication: BotAuthentication, guild_id: Snowflake, *, global_priority: int = 0
    ) -> list[WebhookData]:
        """Gets all webhooks in a guild

        See the `documentation <https://discord.dev/resources/webhook#get-guild-webhooks>`__

        .. note::
            This requires the ``MANAGE_WEBHOOKS`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of the guild to get webhooks from
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[discord_typings.WebhookData]
            The webhooks in the channel
        """
        route = Route("GET", "/guilds/{guild_id}/webhooks", guild_id=guild_id)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_webhook(
        self, authentication: BotAuthentication, webhook_id: Snowflake, *, global_priority: int = 0
    ) -> WebhookData:
        """Gets a webhook by webhook id

        See the `documentation <https://discord.dev/resources/webhook#get-webhook>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        webhook_id:
            The id of the webhook to fetch
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.WebhookData
            The webhook that was fetched
        """
        route = Route("GET", "/webhooks/{webhook_id}", webhook_id=webhook_id)

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_webhook_with_token(
        self, webhook_id: Snowflake, webhook_token: str, *, global_priority: int = 0
    ) -> WebhookData:
        """Gets a webhook by webhook id and token

        See the `documentation <https://discord.dev/resources/webhook#get-webhook-with-token>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        webhook_id:
            The id of the webhook to fetch
        webhook_token:
            The token of the webhook
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.WebhookData
            The webhook that was fetched
        """
        route = Route(
            "GET", "/webhooks/{webhook_id}/{webhook_token}", webhook_id=webhook_id, webhook_token=webhook_token
        )

        r = await self._request(
            route,
            ratelimit_key=None,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_webhook(
        self,
        authentication: BotAuthentication,
        webhook_id: Snowflake,
        *,
        name: str | UndefinedType = UNDEFINED,
        avatar: str | None | UndefinedType = UNDEFINED,
        channel_id: Snowflake | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> WebhookData:
        """Modifies a webhook

        See the `documentation <https://discord.dev/resources/webhook#modify-webhook>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        webhook_id:
            The id of the webhook to modify
        name:
            The new name of the webhook
        avatar:
            Base64 encoded avatar of the webhook
        channel_id:
            The id of a channel to move the webhook to.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.WebhookData
            The updated webhook
        """
        route = Route("PATCH", "/webhooks/{webhook_id}", webhook_id=webhook_id)

        payload: JsonCompatible = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name
        if avatar is not UNDEFINED:
            payload["avatar"] = avatar
        if channel_id is not UNDEFINED:
            payload["channel_id"] = channel_id

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            headers=headers,
            ratelimit_key=authentication.rate_limit_key,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_webhook_with_token(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        *,
        name: str | UndefinedType = UNDEFINED,
        avatar: str | None | UndefinedType = UNDEFINED,
        channel_id: Snowflake | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> WebhookData:
        """Modifies a webhook

        See the `documentation <https://discord.dev/resources/webhook#modify-webhook-with-token>`__

        Parameters
        ----------
        webhook_id:
            The id of the webhook to modify
        webhook_token:
            The token of the webhook to use for authentication
        name:
            The new name of the webhook
        avatar:
            Base64 encoded avatar of the webhook
        channel_id:
            The id of a channel to move the webhook to.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.WebhookData
            The updated webhook
        """
        route = Route(
            "PATCH", "/webhooks/{webhook_id}/{webhook_token}", webhook_id=webhook_id, webhook_token=webhook_token
        )

        payload: JsonCompatible = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name
        if avatar is not UNDEFINED:
            payload["avatar"] = avatar
        if channel_id is not UNDEFINED:
            payload["channel_id"] = channel_id

        headers = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            headers=headers,
            ratelimit_key=None,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_webhook(
        self, authentication: BotAuthentication, webhook_id: Snowflake, *, reason: str, global_priority: int = 0
    ) -> None:
        """Deletes a webhook

        See the `documentation <https://discord.dev/resources/webhook#delete-webhook>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        webhook_id:
            The id of the webhook to delete
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.WebhookData
            The webhook that was deleted
        """
        route = Route("DELETE", "/webhooks/{webhook_id}", webhook_id=webhook_id)

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers=headers,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_webhook_with_token(
        self, webhook_id: Snowflake, webhook_token: str, *, reason: str, global_priority: int = 0
    ) -> None:
        """Deletes a webhook

        See the `documentation <https://discord.dev/resources/webhook#delete-webhook-with-token>`__

        Parameters
        ----------
        webhook_id:
            The id of the webhook to delete
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.WebhookData
            The webhook that was fetched
        """
        route = Route(
            "DELETE", "/webhooks/{webhook_id}/{webhook_token}", webhook_id=webhook_id, webhook_token=webhook_token
        )

        headers = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            ratelimit_key=None,
            headers=headers,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # TODO: @ooliver1 should implement execute webhook
    # TODO: @ooliver1 should implement execute slack-compatible webhook
    # TODO: @ooliver1 should implement execute github-compatible webhook

    async def get_webhook_message(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        message_id: Snowflake,
        *,
        thread_id: Snowflake,
        global_priority: int = 0,
    ) -> MessageData:
        """Gets a message sent by the webhook

        See the `documentation <https://discord.dev/resources/webhook#get-webhook>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        webhook_id:
            The id of the webhook to fetch a message from
        webhook_token:
            The token of the webhook
        message_id:
            The id of the message to fetch
        thread_id:
            The id of the thread to fetch the message from

            .. note::
                This has to be a thread in the channel the webhook is in
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.MessageData
            The message that was fetched
        """
        route = Route(
            "GET",
            "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}",
            webhook_id=webhook_id,
            webhook_token=webhook_token,
            message_id=message_id,
        )

        query = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if thread_id is not UNDEFINED:
            query["thread_id"] = thread_id

        r = await self._request(route, ratelimit_key=None, global_priority=global_priority, query=query)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # TODO: @ooliver1 should implement edit webhook message

    async def delete_webhook_message(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        message_id: Snowflake,
        *,
        thread_id: Snowflake,
        global_priority: int = 0,
    ) -> None:
        """Deletes a message sent by the webhook

        See the `documentation <https://discord.dev/resources/webhook#get-webhook>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        webhook_id:
            The id of the webhook to fetch a message from
        webhook_token:
            The token of the webhook
        message_id:
            The id of the message to fetch
        thread_id:
            The id of the thread to fetch the message from

            .. note::
                This has to be a thread in the channel the webhook is in
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "DELETE",
            "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}",
            webhook_id=webhook_id,
            webhook_token=webhook_token,
            message_id=message_id,
        )

        query = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if thread_id is not UNDEFINED:
            query["thread_id"] = thread_id

        r = await self._request(route, ratelimit_key=None, global_priority=global_priority, query=query)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # Gateway
    async def get_gateway(self) -> GetGatewayData:
        """Gets gateway connection info.

        See the `documentation <https://discord.dev/topics/gateway#get-gateway>`__ for more info.

        **Example usage:**

        .. code-block:: python

            gateway_info = await http_client.get_gateway()

        Returns
        -------
        discord_typings.GetGatewayData
            The gateway info.
        """
        route = Route("GET", "/gateway", ignore_global=True)
        r = await self._request(route, ratelimit_key=None)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_gateway_bot(
        self, authentication: BotAuthentication, *, global_priority: int = 0
    ) -> GetGatewayBotData:
        """Gets gateway connection information.

        See the `documentation <https://discord.dev/topics/gateway#gateway-get-gateway-bot>`__

        **Example usage:**

        .. code-block:: python

            bot_info = await http_client.get_gateway_bot(token)

        Parameters
        ----------
        authentication:
            Authentication info.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.GetGatewayBotData
            Gateway connection info.
        """
        route = Route("GET", "/gateway/bot")
        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # OAuth2
    async def get_current_bot_application_information(
        self, authentication: BotAuthentication, *, global_priority: int = 0
    ) -> ApplicationData:
        """Gets the bots application

        See the `documentation <https://discord.dev/topics/oauth2#get-current-bot-application-information>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.ApplicationData
            The application the bot is connected to
        """
        route = Route("GET", "/oauth2/applications/@me")

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_current_authorization_information(
        self, authentication: BotAuthentication | BearerAuthentication, *, global_priority: int = 0
    ) -> JsonCompatible:  # TODO: Narrow typing
        """Gets the bots application

        See the `documentation <https://discord.dev/topics/oauth2#get-current-bot-application-information>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.???
            Info about the current logged in user/bot
        """
        route = Route("GET", "/oauth2/@me")

        r = await self._request(
            route,
            ratelimit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

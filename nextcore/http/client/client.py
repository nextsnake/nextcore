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
from typing import TYPE_CHECKING, overload

from ...common import UNDEFINED, UndefinedType
from ..route import Route
from .base_client import BaseHTTPClient
from .wrappers import ApplicationCommandsHTTPWrappers, AuditLogHTTPWrappers, ChannelHTTPWrappers, EmojiHTTPWrappers

if TYPE_CHECKING:
    from typing import Any, Final, Literal

    from discord_typings import (
        ApplicationData,
        BanData,
        ChannelData,
        ChannelPositionData,
        DMChannelData,
        GetGatewayBotData,
        GetGatewayData,
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
        PartialChannelData,
        RoleData,
        RolePositionData,
        Snowflake,
        StageInstanceData,
        StickerData,
        StickerPackData,
        UserData,
        VoiceRegionData,
        WebhookData,
        WelcomeChannelData,
        WelcomeScreenData,
    )

    from ..authentication import BearerAuthentication, BotAuthentication

logger = getLogger(__name__)

__all__: Final[tuple[str, ...]] = ("HTTPClient",)


class HTTPClient(
    ApplicationCommandsHTTPWrappers,
    AuditLogHTTPWrappers,
    ChannelHTTPWrappers,
    EmojiHTTPWrappers,
    BaseHTTPClient,
):
    """The HTTP client to interface with the Discord API.

    **Example usage**

    .. code-block:: python3

        http_client = HTTPClient()
        await http_client.setup()

        gateway = await http_client.get_gateway()

        print(gateway["url"])

        await http_client.close()

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

    # Wrapper functions for requests
    # Application commands
    # Audit log
    # Channel
    # Emoji
    # Guild
    async def create_guild(
        self,
        authentication: BotAuthentication,
        name: str,
        *,
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

        Read the `documentation <https://discord.dev/resources/guild#create-guild>`__.

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
        payload: dict[str, Any] = {"name": name}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
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
            rate_limit_key=authentication.rate_limit_key,
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

        query: dict[str, str] = {}

        # Save a bit of bandwith by not including it by default
        # TODO: Not sure if this is worth it
        if with_counts is not UNDEFINED:
            query["with_counts"] = str(with_counts).lower()  # Use true instead of True

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            query=query,
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_preview(
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
            rate_limit_key=authentication.rate_limit_key,
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
            rate_limit_key=authentication.rate_limit_key,
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
            rate_limit_key=authentication.rate_limit_key,
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
            rate_limit_key=authentication.rate_limit_key,
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
            rate_limit_key=authentication.rate_limit_key,
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
            rate_limit_key=authentication.rate_limit_key,
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
            rate_limit_key=authentication.rate_limit_key,
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

        url_query: dict[str, str] = {"query": query}  # Different name to not overwrite the query argument

        # These can technically be provided by default however its wasted bandwidth
        # TODO: Reconsider this?
        # This only adds them if they are provided (not Undefined)
        if limit is not UNDEFINED:
            url_query["limit"] = str(limit)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            query=url_query,
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

        Read the `documentation <https://discord.dev/resources/guild#add-guild-member>`__

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

        payload: dict[str, Any] = {"access_token": user_authentication.token}

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

        r = await self._request(
            route,
            rate_limit_key=bot_authentication.rate_limit_key,
            headers={"Authorization": str(bot_authentication)},
            json=payload,
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

        Read the `documentation <https://discord.dev/resources/guild#modify-guild-member>`__

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

        payload: dict[str, Any] = {}

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild#modify-current-member>`__

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

        payload: dict[str, Any] = {}

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild#add-guild-member-role>`__

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
            route, rate_limit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
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

        Read the `documentation <https://discord.dev/resources/guild#remove-guild-member-role>`__

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
            route, rate_limit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
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

        Read the `documentation <https://discord.dev/resources/guild#remove-guild-member>`__

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
            route, rate_limit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
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
        before: Snowflake | UndefinedType = UNDEFINED,
        after: Snowflake | UndefinedType = UNDEFINED,
        limit: int | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> list[BanData]:
        """Gets a list of bans in a guild.

        Read the `documentation <https://discord.dev/resources/guild#get-guild-bans>`__

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

        query: dict[str, str] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if before is not UNDEFINED:
            query["before"] = str(before)
        if after is not UNDEFINED:
            query["after"] = str(after)
        if limit is not UNDEFINED:
            query["limit"] = str(limit)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers=headers,
            query=query,
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

        Read the `documentation <https://discord.dev/resources/guild#get-guild-ban>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        payload: dict[str, Any] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if delete_message_days is not UNDEFINED:
            payload["delete_message_days"] = delete_message_days

        await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
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
            rate_limit_key=authentication.rate_limit_key,
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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild#create-guild-role>`__

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

        payload: dict[str, Any] = {}

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild#modify-guild-role-positions>`__

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
            route, rate_limit_key=authentication.rate_limit_key, json=position_updates, global_priority=global_priority
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

        Read the `documentation <https://discord.dev/resources/guild#modify-guild-role>`__

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

        payload: dict[str, Any] = {}

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild#delete-guild-role>`__

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
            route, headers=headers, rate_limit_key=authentication.rate_limit_key, global_priority=global_priority
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

        Read the `documentation <https://discord.dev/resources/guild#get-guild-prune-count>`

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild#begin-guild-prune>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild#get-guild-voice-regions>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild#get-guild-invites>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild#get-guild-integrations>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild#delete-guild-integration>`__

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
            route, headers=headers, rate_limit_key=authentication.rate_limit_key, global_priority=global_priority
        )

    async def get_guild_widget_settings(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> GuildWidgetSettingsData:
        """Gets widget settings for a guild

        Read the `documentation <https://discord.dev/resources/guild#get-guild-widget-settings>`__

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
            rate_limit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_guild_widget(
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

        Read the `documentation <https://discord.dev/resources/guild#modify-guild-widget>`__

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

        payload: dict[str, Any] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if enabled is not UNDEFINED:
            payload["enabled"] = enabled
        if channel_id is not UNDEFINED:
            payload["channel_id"] = channel_id

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            rate_limit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_widget(
        self,
        guild_id: Snowflake,
    ) -> GuildWidgetData:
        """Gets a widget from a guild id

        Read the `documentation <https://discord.dev/resources/guild#get-guild-widget>`__

        Parameters
        ----------
        guild_id:
            The id of guild to get the widget for.
        """

        route = Route("GET", "/guilds/{guild_id}/widget.json", guild_id=guild_id, ignore_global=True)

        r = await self._request(
            route,
            rate_limit_key=None,
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

        Read the `documentation <https://discord.dev/resources/guild#get-guild-vanity-url>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild#get-guild-welcome-screen>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild#modify-guild-welcome-screen>`__

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

        payload: dict[str, Any] = {}

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild#modify-current-user-voice-state>`__

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

        payload: dict[str, Any] = {"channel_id": channel_id}

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild#modify-user-voice-state>`__

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

        payload: dict[str, Any] = {"channel_id": channel_id}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if suppress is not UNDEFINED:
            payload["suppress"] = suppress

        await self._request(
            route,
            headers={"Authorization": str(authentication)},
            json=payload,
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild-scheduled-event#list-scheduled-events-for-guild>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild-scheduled-event#create-guild-scheduled-event>`__

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

        payload: dict[str, Any] = {
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
            rate_limit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_scheduled_event(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        guild_scheduled_event_id: Snowflake,
        *,
        with_user_count: bool | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> GuildScheduledEventData:  # TODO: Narrow type more with a overload with_user_count
        """Gets a scheduled event by id

        Read the `documentation <https://discord.dev/resources/guild-scheduled-event#get-guild-scheduled-event>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild-scheduled-event#delete-guild-scheduled-event>`__

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
            route, headers=headers, rate_limit_key=authentication.rate_limit_key, global_priority=global_priority
        )

    # TODO: Add Get Guild Scheduled Event Users
    async def get_guild_template(
        self, authentication: BotAuthentication, template_code: str, *, global_priority: int = 0
    ) -> GuildTemplateData:
        """Gets a template by code

        Read the `documentation <https://discord.dev/resources/guild-template#get-guild-templates>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild-template#create-guild-from-guild-template>`__

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

        payload: dict[str, Any] = {"name": name}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if icon is not UNDEFINED:
            payload["icon"] = icon

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild-template#get-guild-templates>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild-template#create-guild-template>`__

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

        payload: dict[str, Any] = {"name": name}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if description is not UNDEFINED:
            payload["description"] = description

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild-template#sync-guild-templates>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/guild-template#modify-guild-templates>`__

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

        payload: dict[str, Any] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name
        if description is not UNDEFINED:
            payload["description"] = description

        await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_guild_template(
        self, authentication: BotAuthentication, guild_id: Snowflake, template_code: str, *, global_priority: int = 0
    ) -> GuildTemplateData:
        """Deletes a template

        Read the `documentation <https://discord.dev/resources/guild-template#delete-guild-template>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/invite#get-invite>`__

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
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_invite(
        self, authentication: BotAuthentication, invite_code: str, *, global_priority: int = 0
    ) -> InviteData:
        """Gets a invite from a invite code

        Read the `documentation <https://discord.dev/resources/invite#delete-invite>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/stage-instance#create-stage-instance>`__

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

        payload: dict[str, Any] = {"channel_id": channel_id, "topic": topic}

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/stage-instance#get-stage-instance>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/stage-instance#modify-stage-instance>`__

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

        payload: dict[str, Any] = {}

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/stage-instance#delete-stage-instance>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/sticker#get-sticker>`__

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
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def list_nitro_sticker_packs(
        self, *, global_priority: int = 0
    ) -> dict[Literal["sticker_packs"], list[StickerPackData]]:
        """Gets all nitro sticker packs

        Read the `documentation <https://discord.dev/resources/sticker#list-nitro-sticker-packs>`__

        Parameters
        ----------
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("GET", "/sticker-packs")
        r = await self._request(
            route,
            rate_limit_key=None,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def list_guild_stickers(
        self, authentication: BotAuthentication, guild_id: Snowflake, *, global_priority: int = 0
    ) -> list[StickerData]:
        """Gets all custom stickers added by a guild

        Read the `documentation <https://discord.dev/resources/sticker#list-guild-stickers>`__

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
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_sticker(
        self, authentication: BotAuthentication, guild_id: Snowflake, sticker_id: str | int, *, global_priority: int = 0
    ) -> StickerData:
        """Get a custom sticker

        Read the `documentation <https://discord.dev/resources/sticker#get-guild-sticker>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/sticker#modify-guild-sticker>`__

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

        payload: dict[str, Any] = {}

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/sticker#delete-guild-sticker>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/user#get-current-user>`__

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
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_user(
        self, authentication: BotAuthentication | BearerAuthentication, user_id: Snowflake, *, global_priority: int = 0
    ) -> UserData:
        """Gets a user by id

        Read the `documentation <https://discord.dev/resources/user#get-user>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/user#modify-current-user>`__

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

        payload: dict[str, Any] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if username is not UNDEFINED:
            payload["username"] = username
        if avatar is not UNDEFINED:
            payload["avatar"] = avatar

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_current_user_guilds(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        *,
        before: Snowflake | UndefinedType = UNDEFINED,
        after: Snowflake | UndefinedType = UNDEFINED,
        limit: int | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> list[GuildData]:  # TODO: Replace with partial guild data
        """Gets the guilds the current user is in

        Read the `documentation <https://discord.dev/resources/user#get-current-user-guilds>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/user#get-current-user-guild-member>`__

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
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def leave_guild(
        self, authentication: BotAuthentication, guild_id: Snowflake, *, global_priority: int = 0
    ) -> None:
        """Leave a guild

        Read the `documentation <https://discord.dev/resources/user#leave-guild>`__

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
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

    async def create_dm(
        self, authentication: BotAuthentication, recipient_id: Snowflake, *, global_priority: int = 0
    ) -> DMChannelData:
        """Creates a DM channel

        Read the `documentation <https://discord.dev/resources/user#create-dm>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/user#get-user-connections>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/voice#list-voice-regions>`__

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
            rate_limit_key=authentication.rate_limit_key,
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
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> WebhookData:
        """Creates a webhook

        Read the `documentation <https://discord.dev/resources/webhook#create-webhook>`__

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

        payload: dict[str, Any] = {"name": name}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if avatar is not UNDEFINED:
            payload["avatar"] = avatar

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/webhook#get-channel-webhooks>`__

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
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_webhooks(
        self, authentication: BotAuthentication, guild_id: Snowflake, *, global_priority: int = 0
    ) -> list[WebhookData]:
        """Gets all webhooks in a guild

        Read the `documentation <https://discord.dev/resources/webhook#get-guild-webhooks>`__

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
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_webhook(
        self, authentication: BotAuthentication, webhook_id: Snowflake, *, global_priority: int = 0
    ) -> WebhookData:
        """Gets a webhook by webhook id

        Read the `documentation <https://discord.dev/resources/webhook#get-webhook>`__

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
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_webhook_with_token(
        self, webhook_id: Snowflake, webhook_token: str, *, global_priority: int = 0
    ) -> WebhookData:
        """Gets a webhook by webhook id and token

        Read the `documentation <https://discord.dev/resources/webhook#get-webhook-with-token>`__

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
            rate_limit_key=None,
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

        Read the `documentation <https://discord.dev/resources/webhook#modify-webhook>`__

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

        payload: dict[str, Any] = {}

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/webhook#modify-webhook-with-token>`__

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

        payload: dict[str, Any] = {}

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
            rate_limit_key=None,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_webhook(
        self,
        authentication: BotAuthentication,
        webhook_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Deletes a webhook

        Read the `documentation <https://discord.dev/resources/webhook#delete-webhook>`__

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
            rate_limit_key=authentication.rate_limit_key,
            headers=headers,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_webhook_with_token(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Deletes a webhook

        Read the `documentation <https://discord.dev/resources/webhook#delete-webhook-with-token>`__

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
            rate_limit_key=None,
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
        thread_id: Snowflake | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> MessageData:
        """Gets a message sent by the webhook

        Read the `documentation <https://discord.dev/resources/webhook#get-webhook-message>`__

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

        r = await self._request(route, rate_limit_key=None, global_priority=global_priority, query=query)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # TODO: @ooliver1 should implement edit webhook message

    async def delete_webhook_message(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        message_id: Snowflake,
        *,
        thread_id: Snowflake | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Deletes a message sent by the webhook

        Read the `documentation <https://discord.dev/resources/webhook#delete-webhook-message>`__

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

        r = await self._request(route, rate_limit_key=None, global_priority=global_priority, query=query)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # Gateway
    async def get_gateway(self) -> GetGatewayData:
        """Gets gateway connection info.

        Read the `documentation <https://discord.dev/topics/gateway#get-gateway>`__ for more info.

        **Example usage:**

        .. code-block:: python

            gateway_info = await http_client.get_gateway()

        Returns
        -------
        discord_typings.GetGatewayData
            The gateway info.
        """
        route = Route("GET", "/gateway", ignore_global=True)
        r = await self._request(route, rate_limit_key=None)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_gateway_bot(
        self, authentication: BotAuthentication, *, global_priority: int = 0
    ) -> GetGatewayBotData:
        """Gets gateway connection information.

        Read the `documentation <https://discord.dev/topics/gateway#gateway-get-gateway-bot>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/topics/oauth2#get-current-bot-application-information>`__

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
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_current_authorization_information(
        self, authentication: BotAuthentication | BearerAuthentication, *, global_priority: int = 0
    ) -> dict[str, Any]:  # TODO: Narrow typing
        """Gets the bots application

        Read the `documentation <https://discord.dev/topics/oauth2#get-current-authorization-information>`__

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
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

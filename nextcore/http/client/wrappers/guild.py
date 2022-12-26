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

from abc import ABC
from logging import getLogger
from typing import TYPE_CHECKING, overload

from ....common import UNDEFINED, UndefinedType
from ...route import Route
from ..abstract_client import AbstractHTTPClient

if TYPE_CHECKING:
    from typing import Any, Final, Literal

    from discord_typings import (
        BanData,
        ChannelData,
        ChannelPositionData,
        GuildData,
        GuildMemberData,
        GuildPreviewData,
        GuildWidgetData,
        GuildWidgetSettingsData,
        HasMoreListThreadsData,
        IntegrationData,
        InviteMetadata,
        PartialChannelData,
        RoleData,
        RolePositionData,
        Snowflake,
        VoiceRegionData,
        WelcomeChannelData,
        WelcomeScreenData,
    )

    from ...authentication import BearerAuthentication, BotAuthentication

logger = getLogger(__name__)

__all__: Final[tuple[str, ...]] = ("GuildHTTPWrappers",)


class GuildHTTPWrappers(AbstractHTTPClient, ABC):
    """HTTP wrappers for guild API endpoints.

    This is an abstract base class that should not be used directly.
    """

    __slots__ = ()

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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
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
            json=payload,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        with_counts: bool | UndefinedType = UNDEFINED,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """
        route = Route("GET", "/guilds/{guild_id}", guild_id=guild_id)

        params: dict[str, str] = {}

        # Save a bit of bandwith by not including it by default
        # TODO: Not sure if this is worth it
        if with_counts is not UNDEFINED:
            params["with_counts"] = str(with_counts).lower()  # Use true instead of True

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            params=params,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_preview(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """
        route = Route("GET", "/guilds/{guild_id}/preview", guild_id=guild_id)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Implement modify guild here

    async def delete_guild(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """
        route = Route("DELETE", "/guilds/{guild_id}", guild_id=guild_id)

        await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

    async def get_guild_channels(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """
        route = Route("GET", "/guilds/{guild_id}/channels", guild_id=guild_id)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
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
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

    async def list_active_guild_threads(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """
        route = Route("GET", "/guilds/{guild_id}/threads/active", guild_id=guild_id)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_member(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        user_id: str | int,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """
        route = Route("GET", "/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """
        route = Route("GET", "/guilds/{guild_id}/members", guild_id=guild_id)

        params = {}
        # These can technically be provided by default however its wasted bandwidth
        # TODO: Reconsider this?
        # This only adds them if they are provided (not Undefined)
        if after is not UNDEFINED:
            params["after"] = after
        if limit is not UNDEFINED:
            params["limit"] = limit

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            params=params,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """
        route = Route("GET", "/guilds/{guild_id}/members/search", guild_id=guild_id)

        params: dict[str, str] = {"query": query}

        # These can technically be provided by default however its wasted bandwidth
        # TODO: Reconsider this?
        # This only adds them if they are provided (not Undefined)
        if limit is not UNDEFINED:
            params["limit"] = str(limit)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            params=params,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`


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
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`

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
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def modify_current_member(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        nick: str | None | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`

        Returns
        -------
        discord_typings.GuildMemberData
            The member after the update
        """
        route = Route("PATCH", "/guilds/{guild_id}/members/@me", guild_id=guild_id)

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
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
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
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers=headers,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

    async def remove_guild_member_role(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        user_id: Snowflake,
        role_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
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
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers=headers,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

    async def remove_guild_member(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """
        route = Route("DELETE", "/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id)

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers=headers,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

    @overload
    async def get_guild_bans(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        before: int,
        limit: int | UndefinedType,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
    ) -> list[BanData]:
        ...

    @overload
    async def get_guild_bans(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """

        route = Route("GET", "/guilds/{guild_id}/bans", guild_id=guild_id)
        headers = {"Authorization": str(authentication)}

        params: dict[str, str] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if before is not UNDEFINED:
            params["before"] = str(before)
        if after is not UNDEFINED:
            params["after"] = str(after)
        if limit is not UNDEFINED:
            params["limit"] = str(limit)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers=headers,
            params=params,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_ban(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """

        route = Route("GET", "/guilds/{guild_id}/bans/{user_id}", guild_id=guild_id, user_id=user_id)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
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
            json=payload,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

    async def remove_guild_ban(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
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
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

    async def get_guild_roles(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`

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
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`

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
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_guild_role_positions(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *position_updates: RolePositionData,
        reason: str | UndefinedType = UNDEFINED,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """
        route = Route("GET", "/guilds/{guild_id}/roles", guild_id=guild_id)

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            json=position_updates,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`

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
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """

        route = Route("DELETE", "/guilds/{guild_id}/roles/{role_id}", guild_id=guild_id, role_id=role_id)
        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        await self._request(
            route,
            headers=headers,
            rate_limit_key=authentication.rate_limit_key,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

    async def get_guild_prune_count(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        days: int | UndefinedType = UNDEFINED,
        include_roles: list[str] | UndefinedType = UNDEFINED,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """
        route = Route("GET", "/guilds/{guild_id}/prune", guild_id=guild_id)

        params = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)

        if days is not UNDEFINED:
            params["days"] = days
        if include_roles is not UNDEFINED:
            params["include_roles"] = ",".join(include_roles)

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            params=params,
            rate_limit_key=authentication.rate_limit_key,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """
        route = Route("GET", "/guilds/{guild_id}/prune", guild_id=guild_id)

        params = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)

        if days is not UNDEFINED:
            params["days"] = days
        if compute_prune_count is not UNDEFINED:
            params["compute_prune_count"] = compute_prune_count
        if include_roles is not UNDEFINED:
            params["include_roles"] = ",".join(include_roles)

        headers = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)

        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            params=params,
            rate_limit_key=authentication.rate_limit_key,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_voice_regions(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """

        route = Route("GET", "/guilds/{guild_id}/regions", guild_id=guild_id)

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            rate_limit_key=authentication.rate_limit_key,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_invites(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """

        route = Route("GET", "/guilds/{guild_id}/invites", guild_id=guild_id)

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            rate_limit_key=authentication.rate_limit_key,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_integrations(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """

        route = Route("GET", "/guilds/{guild_id}/invites", guild_id=guild_id)

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            rate_limit_key=authentication.rate_limit_key,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
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
            route,
            headers=headers,
            rate_limit_key=authentication.rate_limit_key,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

    async def get_guild_widget_settings(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """

        route = Route("GET", "/guilds/{guild_id}/widget", guild_id=guild_id)

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            rate_limit_key=authentication.rate_limit_key,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
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
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """

        route = Route("GET", "/guilds/{guild_id}/vanity-url", guild_id=guild_id)

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            rate_limit_key=authentication.rate_limit_key,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Implement get guild widget image

    async def get_guild_welcome_screen(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """

        route = Route("GET", "/guilds/{guild_id}/welcome-screen", guild_id=guild_id)

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            rate_limit_key=authentication.rate_limit_key,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
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
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
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
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

    async def modify_user_voice_state(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        channel_id: Snowflake,
        user_id: Snowflake,
        *,
        suppress: bool | UndefinedType = UNDEFINED,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
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
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

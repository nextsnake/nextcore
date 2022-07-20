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
from typing import TYPE_CHECKING

from ...common import UNDEFINED, UndefinedType
from ..route import Route
from .base_client import BaseHTTPClient
from .wrappers import (
    ApplicationCommandsHTTPWrappers,
    AuditLogHTTPWrappers,
    ChannelHTTPWrappers,
    EmojiHTTPWrappers,
    GuildHTTPWrappers,
    GuildScheduledEventHTTPWrappers,
    GuildTemplateHTTPWrappers,
)

if TYPE_CHECKING:
    from typing import Any, Final, Literal

    from discord_typings import (
        ApplicationData,
        DMChannelData,
        GetGatewayBotData,
        GetGatewayData,
        GuildData,
        GuildMemberData,
        InviteData,
        MessageData,
        Snowflake,
        StageInstanceData,
        StickerData,
        StickerPackData,
        UserData,
        VoiceRegionData,
        WebhookData,
    )

    from ..authentication import BearerAuthentication, BotAuthentication

logger = getLogger(__name__)

__all__: Final[tuple[str, ...]] = ("HTTPClient",)


class HTTPClient(
    ApplicationCommandsHTTPWrappers,
    AuditLogHTTPWrappers,
    ChannelHTTPWrappers,
    EmojiHTTPWrappers,
    GuildHTTPWrappers,
    GuildScheduledEventHTTPWrappers,
    GuildTemplateHTTPWrappers,
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
    # Guild Scheduled events
    # Guild Template
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

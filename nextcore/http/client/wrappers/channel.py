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
from typing import TYPE_CHECKING, overload
from urllib.parse import quote

from aiohttp import FormData

from ....common import UNDEFINED, UndefinedType, json_dumps
from ...route import Route
from ..abstract_client import AbstractHTTPClient

if TYPE_CHECKING:
    from typing import Any, Final, Iterable, Literal

    from discord_typings import (
        ActionRowData,
        AllowedMentionsData,
        AttachmentData,
        ChannelData,
        EmbedData,
        FollowedChannelData,
        HasMoreListThreadsData,
        InviteData,
        InviteMetadata,
        MessageData,
        MessageReferenceData,
        Snowflake,
        ThreadChannelData,
        ThreadMemberData,
        UserData,
    )

    from ...authentication import BearerAuthentication, BotAuthentication
    from ...file import File

__all__: Final[tuple[str, ...]] = ("ChannelHTTPWrappers",)


class ChannelHTTPWrappers(AbstractHTTPClient, ABC):
    """HTTP wrappers for channel API endpoints.

    This is an abstract base class that should not be used directly.
    """

    __slots__ = ()

    async def get_channel(
        self, authentication: BotAuthentication, channel_id: Snowflake, *, global_priority: int = 0
    ) -> ChannelData:
        """Gets a channel by ID.

        Read the `documentation <https://discord.dev/resources/channels#get-channel>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The channel ID to get.
        global_priority:
            The priority of the request for the global rate-limiter.

        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFound
            The channel could not be found


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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `docoumentation <https://discord.dev/resources/channel#modify-group-dm>`__

        .. warning::
            This shares rate limits with :attr:`HTTPClient.modify_guild_channel` and :attr:`HTTPClient.modify_thread`.

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


        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            Could not find the group dm
        BadRequestError
            You did not follow the requirements for the parameters
        """
        route = Route("PATCH", "/channels/{channel_id}", channel_id=channel_id)
        payload: dict[str, Any] = {}  # TODO: Use a typehint for payload

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `docoumentation <https://discord.dev/resources/channel#modify-channel>`__


        .. warning::
            This shares rate limits with :attr:`HTTPClient.modify_group_dm` and :attr:`HTTPClient.modify_thread`.

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


        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            The channel was not found
        BadRequestError
            You did not follow the requirements for some of the parameters
        """

        route = Route("PATCH", "/channels/{channel_id}", channel_id=channel_id)
        payload: dict[str, Any] = {}  # TODO: Use a typehint for payload

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `docoumentation <https://discord.dev/resources/channel#modify-channel>`__

        .. warning::
            This shares rate limits with :attr:`HTTPClient.modify_group_dm` and :attr:`HTTPClient.modify_guild_channel`.

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

        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            The thread wasnt found
        BadRequestError
            You did not follow the requirements for some of the parameters
        """

        route = Route("PATCH", "/channels/{channel_id}", channel_id=thread_id)
        payload: dict[str, Any] = {}

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/channel#deleteclose-channel>`__

        .. note::
            This requires the ``MANAGE_CHANNELS`` for channels and ``MANAGE_THREADS`` for threads

            DMs does not require any permissions to close

        .. warning::
            Deleting a category will not delete the channels under it.

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


        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        ForbiddenError
            You did not have the correct permissions
        NotFoundError
            Can't find the channel
        """

        route = Route("DELETE", "/channels/{channel_id}", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        await self._request(
            route, headers=headers, rate_limit_key=authentication.rate_limit_key, global_priority=global_priority
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

        Read the `documentation <https://discord.dev/resources/channel#get-channel-messages>`__

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


        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            The channel was not found
        ForbiddenError
            You did not have the neccesary permissions
        BadRequestError
            You did not give the correct types or did not follow the requirements for some of the parameters
        """

        route = Route("GET", "/channels/{channel_id}/messages", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}

        query: dict[str, str] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if around is not UNDEFINED:
            query["around"] = str(around)
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

        Read the `documentation <https://discord.dev/resources/channel#create-message>`__

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

                Read the `embed limits documentation <https://discord.dev/resources/channel#embed-object-embed-limits>`__ for more info.
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


        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            The channel was not found
        ForbiddenError
            Missing permissions
        BadRequestError
            You did not follow the requirements for some parameters

        Returns
        -------
        discord_typings.MessageData
            The message that was sent.
        """
        route = Route("POST", "/channels/{channel_id}/messages", channel_id=channel_id)
        headers = {"Authorization": str(authentication)}

        # We use payload_json here as the format is more strictly defined than form data.
        # This means we don't have to manually format the data.
        payload: dict[str, Any] = {}

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
            rate_limit_key=authentication.rate_limit_key,
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
        """Publishes a message in a news channel

        Read the `documentation <https://discord.dev/resources/channel#crosspost-message>`__

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

        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        ForbiddenError
            Missing permissions or you tried to publish a message in a non-news channel
        NotFoundError
            Could not find the message to publish

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
            route, rate_limit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
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

        Read the `documentation <https://discord.dev/resources/channel#create-reaction>`__

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


        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            Could not find the message
        BadRequestError
            Could not find the emoji to react with
        BadRequestError
            You are not in the server that owns this emoji
        BadRequestError
            You did not URL-encode the unicode emoji
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
            route, rate_limit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
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

        Read the `documentation <https://discord.dev/resources/channel#delete-own-reaction>`__

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

        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            You had not reacted with that emoji
        NotFoundError
            You did not follow the format for the emoji
        NotFoundError
            The message was not found
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
            route, rate_limit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
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

        Read the `documentation <https://discord.dev/resources/channel#delete-user-reaction>`__

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


        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            The user had not reacted with that emoji
        NotFoundError
            You did not follow the format for the emoji
        NotFoundError
            The message was not found
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
            route, rate_limit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
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

        Read the `documentation <https://discord.dev/resources/channel#get-reactions>`__

        .. note::
            This requires the ``READ_MESSAGE_HISTORY`` permission.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel where the message is located.
        message_id:
            The id of the message to get the reactions from.
        emoji:
            The emoji to get reactions for
        after:
            A snowflake of that the reaction id has to be higher than to be included

            .. note::
                This does not have to be a valid snowflake
        limit:
            The max amount of reactions to return

            .. note::
                This has to be between ``1`` and ``100``
            .. note::
                This defaults to ``25``
        global_priority:
            The priority of the request for the global rate-limiter.

        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            The channel was not found
        NotFoundError
            The message was not found
        NotFoundError
            There was no reactions for that emoji
        NotFoundError
            The emoji format was not followed
        ForbiddenError
            You did not have the ``READ_MESSAGE_HISTORY`` permission


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

        query: dict[str, str] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
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

    async def delete_all_reactions(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        message_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> None:
        """Deletes all reactions from a message.

        Read the `documentation <https://discord.dev/resources/channel#delete-all-reactions>`__

        .. note::
            This requires the ``MANAGE_MESSAGES`` permission.

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


        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            Could not find the channel
        NotFoundError
            Could not find the message
        ForbiddenError
            You did not have the ``MANAGE_MESSAGES`` permission

        """
        route = Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions",
            channel_id=channel_id,
            message_id=message_id,
        )
        headers = {"Authorization": str(authentication)}

        await self._request(
            route, rate_limit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
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

        Read the `documentation <https://discord.dev/resources/channel#delete-all-reactions-for-emoji>`__

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
            route, rate_limit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
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

        Read the `documentation <https://discord.dev/resources/channel#edit-message>`__

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
        payload: dict[str, Any] = {}

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/channel#delete-message>`__

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
            route, rate_limit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
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

        Read the `documentation <https://discord.dev/resources/channel#bulk-delete-messages>`__

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
            rate_limit_key=authentication.rate_limit_key,
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

        Read the `documentation <https://discord.dev/resources/channel#edit-channel-permissions>`__

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

            - ``0``: Role
            - ``1``: User
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

        payload: dict[str, Any] = {}

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
            rate_limit_key=authentication.rate_limit_key,
            headers=headers,
            json=payload,
            global_priority=global_priority,
        )

    async def get_channel_invites(
        self, authentication: BotAuthentication, channel_id: Snowflake, *, global_priority: int = 0
    ) -> list[InviteMetadata]:
        """Gets the invites for a channel.

        Read the `documentation <https://discord.dev/resources/channel#get-channel-invites>`__

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
            route, rate_limit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
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

            - ``0``: A user's stream
            - ``1``: ``EMBEDDED`` Activity
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

        payload: dict[str, Any] = {}

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
            rate_limit_key=authentication.rate_limit_key,
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
            route, rate_limit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
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
        payload: dict[str, Any] = {"webhook_channel_id": webhook_channel_id}

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
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
            route, rate_limit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
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
            route, rate_limit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
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

        await self._request(route, rate_limit_key=authentication.rate_limit_key, headers=headers)

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
            route, rate_limit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
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
            route, rate_limit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
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
            route, rate_limit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
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
        rate_limit_per_user:
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

        payload: dict[str, Any] = {
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
            rate_limit_key=authentication.rate_limit_key,
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

        payload: dict[str, Any] = {
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
            rate_limit_key=authentication.rate_limit_key,
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
            route, rate_limit_key=authentication.rate_limit_key, headers=headers, global_priority=global_priority
        )

    async def add_thread_member(
        self, authentication: BotAuthentication, channel_id: Snowflake, user_id: str | int, *, global_priority: int = 0
    ) -> None:
        """Adds a member to a thread

        Read the `documentation <https://discord.dev/resources/channel#add-thread-member>`__

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
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

    async def leave_thread(
        self, authentication: BotAuthentication, channel_id: Snowflake, *, global_priority: int = 0
    ) -> None:
        """Leaves a thread

        Read the `documentation <https://discord.dev/resources/channel#leave-thread>`__

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
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

    async def remove_thread_member(
        self, authentication: BotAuthentication, channel_id: Snowflake, user_id: str | int, *, global_priority: int = 0
    ) -> None:
        """Removes a member from a thread

        Read the `documentation <https://discord.dev/resources/channel#remove-thread-member>`__

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
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

    async def get_thread_member(
        self, authentication: BotAuthentication, channel_id: Snowflake, user_id: str | int, *, global_priority: int = 0
    ) -> ThreadMemberData:
        """Gets a thread member.

        Read the `documentation <https://discord.dev/resources/channel#get-thread-member>`__

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
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def list_thread_members(
        self, authentication: BotAuthentication, channel_id: Snowflake, *, global_priority: int = 0
    ) -> list[ThreadMemberData]:
        """Gets all thread members

        Read the `documentation <https://discord.dev/resources/channel#list-thread-members>`__

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
            rate_limit_key=authentication.rate_limit_key,
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
        query: dict[str, str] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if before is not UNDEFINED:
            query["before"] = before
        if limit is not UNDEFINED:
            query["limit"] = str(limit)

        route = Route("GET", "/channels/{channel_id}/threads/archived/public", channel_id=channel_id)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            query=query,
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
        query: dict[str, str] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if before is not UNDEFINED:
            query["before"] = before
        if limit is not UNDEFINED:
            query["limit"] = str(limit)

        route = Route("GET", "/channels/{channel_id}/threads/archived/private", channel_id=channel_id)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            query=query,
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def list_joined_private_archived_threads(
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
        query: dict[str, str] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if before is not UNDEFINED:
            query["before"] = before
        if limit is not UNDEFINED:
            query["limit"] = str(limit)

        route = Route("GET", "/channels/{channel_id}/users/@me/threads/archived/private", channel_id=channel_id)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            query=query,
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

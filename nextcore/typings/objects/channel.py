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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypedDict

    from typing_extensions import NotRequired

    from .auto_archive_duration import AutoArchiveDuration
    from .channel_type import ChannelType
    from .permission_overwrite import PermissionOverwrite
    from .thread_member import ThreadMember
    from .thread_metadata import ThreadMetadata
    from .user import User
    from .video_quality_mode import VideoQualityMode

    # TODO: Document what the discord client does with duplicate channel positions
    class Channel(TypedDict):
        """Typings for a discord channel object

        See the `documentation <https://discord.dev/resources/channel>`__ for more information.

        Attributes
        ----------
        id: :class:`str`
            A unique identifier for the channel.
        type: :class:`ChannelType`
            The type of channel.
        guild_id: NotRequired[:class:`str`]
            The :attr:`Guild.id` the channel belongs to.
        position: NotRequired[:class:`int`]
            The position of the channel in the channel list.
            This is scoped to the category it is in.

            .. note::
                This can be the same as another :attr`Channel.position`.
        permission_overwrites: NotRequired[list[:class:`PermissionOverwrite`]]
            Channel spesific permissions.
        name: NotRequired[:class:`str` | :data:`None`]
            The name of the channel.
        topic: NotRequired[:class:`str` | :data:`None`]
            The channel topic.
        nsfw: NotRequired[:class:`bool`]
            Whether the channel is marked as age-restricted.
        last_message_id: NotRequired[:class:`str` | :data:`None`]
            The id of the last message sent in the channel.

            .. note::
                This is only applicable to text, group DM and forum channels.
            .. note::
                In the case of forum channels, this will be the most recent thread's ID.
            .. note::
                This may not point to a existing message or thread.
        bitrate: NotRequired[:class:`int`]
            The bitrate in bits the voice channel uses.

            .. note::
                This is only applicable to voice and stage channels.
        user_limit: NotRequired[:class:`int`]
            The maximum number of users that can be connected to the voice channel.

            .. note::
                This is only applicable to voice channels.
        rate_limit_per_user: NotRequired[:class:`int`]
            The time in seconds a user has to wait between sending a message or creating a thread.

            .. note::
                This is only applicable to text, forums and news channels.
        recipients: NotRequired[list[:class:`User`]]
            The users that are in the group channel.

            .. note::
                This is only applicable to group DMs.
        icon: NotRequired[:class:`str` | :data:`None`]
            The icon hash of the group DM.

            .. note::
                This is only applicable to group DMs.
        owner_id: NotRequired[:class:`str`]
            The :attr:`User.id` that owns the group DM or the thread creator.

            .. note::
                This is only applicable to group DMs and threads.
        application_id: NotRequired[:class:`str`]
            The :attr:`Application.id` of the application that created the group DM.

            .. note::
                This is only applicable to group DMs.
        parent_id: NotRequired[:class:`str` | :data:`None`]
            The :attr:`Channel.id` of the parent category of the channel.

            .. note::
                If the channel is a thread, this will be the channel the thread was created in.
        last_pin_timestamp: NotRequired[:class:`str` | :data:`None`]
            A ISO8601 timestamp of when the last pinned message was pinned.

            .. note::
                This is only applicable to text, group DM and news channels.
        rtc_region: NotRequired[:class:`str` | :data:`None`]
            The region of the voice channel.

            .. note::
                If this is :data:`None`, the voice region will be automatically determined by the first user to connect to the voice channel.
        video_quality_mode: NotRequired[:class:`VideoQualityMode`]
            The video quality mode of the voice channel.

            .. note::
                If this is not set, assume it is auto.
            .. note::
                This is only applicable to voice channels.
        message_count: NotRequired[:class:`int`]
            Approximate number of messages in the thread.

            .. note::
                This is only applicable to threads.
            .. note::
                This stops counting at 50 messages.
        member_count: NotRequired[:class:`int`]
            Approximate number of members in the thread.

            .. note::
                This is only applicable to threads.
            .. note::
                This stops counting at 50 members.
        thread_metadata: NotRequired[:class:`ThreadMetadata`]
            Metadata about the thread.
        member: NotRequired[:class:`ThreadMember`]
            The :class:`ThreadMember` of the currently logged in user.

            .. note::
                This is only included in certain endpoints.
        default_auto_archive_duration: NotRequired[:class:`AutoArchiveDuration`]
            The default time it takes for the API to archive a thread after the last message was sent.

            .. note::
                This is only applicable to text, forum and news channels.
            .. warn::
                This is only used by the client! The API does not use this as a default
        permissions: NotRequired[:class:`str`]
            The permission the user who called the :class:`Interaction` has.

            .. note::
                This is only present in :attr:`InteractionData.resolved`
        flags: NotRequired[:class:`int`]
            The bitwise channel flags for this channel.

        """

        id: str
        type: ChannelType
        guild_id: NotRequired[str]
        position: NotRequired[int]
        permission_overwrites: NotRequired[PermissionOverwrite]
        name: NotRequired[str]
        topic: NotRequired[str | None]
        nsfw: NotRequired[bool]
        last_message_id: NotRequired[str]
        bitrate: NotRequired[int]
        user_limit: NotRequired[int]
        rate_limit_per_user: NotRequired[int]
        recipients: NotRequired[list[User]]
        icon: NotRequired[str | None]
        owner_id: NotRequired[str]
        application_id: NotRequired[str]
        parent_id: NotRequired[str | None]
        last_pin_timestamp: NotRequired[str | None]
        rtc_region: NotRequired[str | None]
        video_quality_mode: NotRequired[VideoQualityMode]
        message_count: NotRequired[int]
        member_count: NotRequired[int]
        thread_metadata: NotRequired[ThreadMetadata]
        member: NotRequired[ThreadMember]
        default_auto_archive_duration: NotRequired[AutoArchiveDuration]
        permissions: NotRequired[str]
        flags: NotRequired[int]

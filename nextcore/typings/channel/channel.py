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

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from typing_extensions import NotRequired

    from ..common import Snowflake
    from .channel_type import ChannelType
    from .overwrite import Overwrite
    from .thread import AutoArchiveDuration, ThreadMetadata, ThreadMember
    from .video_quality_mode import VideoQualityMode

__all__ = ("Channel",)


class Channel(TypedDict):
    """A `Channel <https://discord.dev/resources/channel>`__ object.

    Attributes
    ----------
    id: :class:`Snowflake`
        The channel's ID.
    type: :class:`ChannelType`
        The channel's type.
    guild_id: NotRequired[:class:`Snowflake`]
        The guild this channel belongs to.
    position: :class:`int`
        The position of the channel. TODO: Document this. Good luck!
    permission_overwrites: NotRequired[list[:class:`Overwrite`]]
        Permission overwrites to apply to the channel. These overwrite the :class:`Member's <Member>` guild level permissions for actions on this channel.
    name: NotRequired[:class:`str` | :data:`None`]
        The name of the channel.

        .. note::
            This is :data:`None` if this channel is a ``DM``.
    topic: NotRequired[:class:`str` | :data:`None`]
        The topic of the channel.

        .. note::
            For ``GUILD_FORUM``, in the Discord client this is displayed as the forum guidelines instead.
    nsfw: NotRequired[:class:`bool`]
        Whether the channel is age-restricted.
    last_message_id: NotRequired[:class:`Snowflake` | :data:`None`]
        The ID of the last message sent in this channel.

        .. note::
            For ``GUILD_FORUM``'s, this will be the ID of the last created thread.

        .. warning::
            This may point to a deleted or invalid message.
    bitrate: NotRequired[:class:`int`]
        The bitrate of the channel in bits per second.
    user_limit: NotRequired[:class:`int`]
        The maximum number of members that can be in this voice channel.

        .. note::
            This is not used for stage channels.
    rate_limit_per_user: NotRequired[:class:`int`]
        The time in seconds that a user has to wait before sending another message or create a new thread.

        This has to be a number between ``0`` and ``21600``.

        .. note::
            This is ``0`` if no rate limit is set.

        .. note::
            Bots and members with the ``MANAGE_MESSAGES`` or ``MANAGE_CHANNELS`` permission are unaffected by this rate limit.
    recipients: NotRequired[list[:class:`User`]]
        The :class:`Users <User>` who are in this Group DM.
    icon: NotRequired[:class:`str` | :data:`None`]
        The icon hash of the Group DM.
    owner_id: NotRequired[:class:`Snowflake`]
        The ID of the owner of the :class:`Guild` or ``GROUP_DM`` this channel belongs to.
    application_id: NotRequired[:class:`Snowflake`]
        The ID of the application that created the Group DM.
    parent_id: NotRequired[:class:`Snowflake` | :data:`None`]
        The ID of the parent channel.

        For threads, this will be the channel the thread was started in.

        For other channels, this will be the ID of the category the channel belongs to.
    last_pin_timestamp: NotRequired[:class:`str` | :data:`None`]
        The ISO 8601 timestamp of the last time a message was pinned in the channel.
    rtc_region: NotRequired[:class:`str` | :data:`None`]
        The :attr:`VoiceRegion.id` for the voice channel, automatically selected by discord when set to :data:`None`.

        .. note::
            The automatic voice region is detected from the first person who joins the voice channel.
    video_quality_mode: NotRequired[:class:`VideoQualityMode`]
        The video quality mode of the channel.

        .. note::
            This should default to ``1`` when not present.
    message_count: NotRequired[:class:`int`]
        A estimate of how many messages are in the channel.

        .. note::
            This stops counting at 50 messages.
    member_count: NotRequired[:class:`int`]
        A estimate of how many members who joined/followed the thread.

        .. note::
            This stops counting at 50 members.
    thread_metadata: NotRequired[:class:`ThreadMetadata`]
        Metadata about a thread.
    member: NotRequired[:class:`ThreadMember`]
        The :class:`ThreadMember` of the current user if they are in the thread.

        .. note::
            This is only included in certain REST endpoints.
    default_auto_archive_duration: :class:`AutoArchiveDuration`
        The default auto archive duration for threads created in this channel.

        .. note::
            This is only used in the client. There is no default for the API.
    permissions: NotRequired[:class:`int`]
        The calculated permissions including guild permissions.

        .. note::
            This is only sent in ``INTERACTION`` events inside the ``RESOLVED`` field.
    flags: NotRequired[:class:`int`]
        The flags for the channel.
    """

    id: Snowflake
    type: ChannelType
    guild_id: NotRequired[Snowflake]
    position: NotRequired[int]
    permission_overwrites: NotRequired[Overwrite]
    name: NotRequired[str | None]
    topic: NotRequired[str | None]
    nsfw: NotRequired[bool]
    last_message_id: NotRequired[Snowflake | None]
    bitrate: NotRequired[int]
    user_limit: NotRequired[int]
    rate_limit_per_user: NotRequired[int]
    recipients: NotRequired[list[User]]  # TODO: Implement User
    icon: NotRequired[str | None]
    owner_id: NotRequired[Snowflake]
    application_id: NotRequired[Snowflake]
    parent_id: NotRequired[Snowflake | None]
    last_pin_timestamp: NotRequired[str | None]
    rtc_region: NotRequired[str | None]
    video_quality_mode: NotRequired[VideoQualityMode]
    message_count: NotRequired[int]
    member_count: NotRequired[int]
    thread_metadata: NotRequired[ThreadMetadata]
    member: NotRequired[ThreadMember]
    default_archive_duration: AutoArchiveDuration
    permissions: NotRequired[int]
    flags: NotRequired[int]

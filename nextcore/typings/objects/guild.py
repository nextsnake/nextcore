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
    from typing_extensions import NotRequired

    from .emoji import Emoji
    from .explicit_content_filter_level import ExplicitContentFilterLevel
    from .guild_feature import GuildFeature
    from .member import Member
    from .message_notifications_level import MessageNotificationsLevel
    from .mfa_level import MFALevel
    from .role import Role
    from .unavailable_guild import UnavailableGuild
    from .verification_level import VerificationLevel
    from .voice_state import VoiceState

    class Guild(UnavailableGuild):
        name: str
        """The guild's name."""
        icon: str | None
        """The guild's icon hash."""
        icon_hash: NotRequired[str]
        """The guild's icon hash, but only present when in the template object"""
        splash: str | None
        """The guild's splash hash."""
        discovery_splash: str | None
        """The guild's discovery splash hash."""
        owner: NotRequired[bool]
        """Whether the current user is the guild owner."""
        owner_id: str
        """The guild owner's ID."""
        permissions: NotRequired[int]
        """The guild's permissions for the current user."""
        afk_channel_id: str | None
        """The ID of the channel where members AFK in voice is moved."""
        afk_timeout: int
        """The amount of time in seconds a user must be idle to be considered AFK."""
        verification_level: VerificationLevel
        """The guild's verification level."""
        default_message_notifications: MessageNotificationsLevel
        """The guild's default message notification level."""
        explicit_content_filter: ExplicitContentFilterLevel
        """The guild's explicit content filter level."""
        roles: NotRequired[list[Role]]
        """A list of guild roles."""
        emojis: NotRequired[list[Emoji]]
        """A list of guild emojis."""
        features: NotRequired[list[GuildFeature]]
        """A list of guild features."""
        mfa_level: MFALevel
        """The guild's MFA level."""
        application_id: str | None
        """The ID of the application that created the guild, if created by a bot."""
        system_channel_id: str | None
        """The ID of the channel where guild notices such as welcome messages and boost events are sent."""
        system_channel_flags: int
        """The bitwise value of the guild's system channel flags. Used for setting which messages are sent to the system channel."""
        rules_channel_id: str | None
        """The ID of the channel where the guild's rules are posted."""
        joined_at: NotRequired[str]
        """The time which the current user joined the guild. Only sent in GUILD_CREATE events."""
        large: NotRequired[bool]
        """Whether the guild is larger than large_threshold provided in IDENTIFY. Only sent in GUILD_CREATE events."""
        member_count: NotRequired[int]
        """The number of members in the guild. Only sent in GUILD_CREATE events."""
        voice_states: NotRequired[list[VoiceState]]
        """A list of voice states in the guild. Only sent in GUILD_CREATE events."""
        members: NotRequired[list[Member]]
        """A list of members in the guild. Only sent in GUILD_CREATE events."""

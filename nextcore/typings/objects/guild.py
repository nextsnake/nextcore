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
    from typing import Literal

    from typing_extensions import NotRequired

    from .channel import Channel
    from .emoji import Emoji
    from .explicit_content_filter_level import ExplicitContentFilterLevel
    from .guild_feature import GuildFeature
    from .guild_scheduled_event import GuildScheduledEvent
    from .locale import Locale
    from .member import Member
    from .message_notifications_level import MessageNotificationsLevel
    from .mfa_level import MFALevel
    from .nsfw_level import NSFWLevel
    from .premium_tier import PremiumTier
    from .presence_update import PresenceUpdate
    from .role import Role
    from .stage_instance import StageInstance
    from .sticker import Sticker
    from .unavailable_guild import UnavailableGuild
    from .verification_level import VerificationLevel
    from .voice_state import VoiceState
    from .welcome_screen import WelcomeScreen

    class Guild(UnavailableGuild):
        """A typing for a `guild <https://discord.dev/resources/guild>`__ object.

        Attributes
        ----------
        id: :class:`str`
            The guild's ID.
        name: :class:`str`
            The name of the guild.
        icon: :class:`str` | :data:`None`
            The hash of the guild's icon.
        icon_hash: NotRequired[:class:`str` | :data:`None`]
            The hash of the guild's icon.

            .. note::
                This is only present in the partial guild in the :class:`Template` object.
        splash: :class:`str` | :data:`None`
            The hash of the guild's splash.
        discovery_splash: :class:`str` | :data:`None`
            The hash of the guild's discovery splash. This is only shown in the Discord client under the discovery tab.
        owner: NotRequired[:class:`bool`]
            If the current logged in user is the owner of the guild.

            .. note::
                This is only present when using OAuth2 to get the current user's guilds.
        owner_id: :class:`str`
            The ID of the guild owner.
        permissions: NotRequired[:class:`int`]
            The permissions of the current logged in user in the guild.

            .. note::
                This is only present when using OAuth2 to get the current user's guilds.
        region: NotRequired[:class:`str` | :data:`None`]
            The ID of the :class:`VoiceRegion` this guild uses.

            .. deprecated::
                Voice regions are per-channel now. See :attr:`Channel.rtc_region`
        afk_channel_id: :class:`str` | :data:`None`
            ID of a voice channel Where human members will be moved to when they are AFK in a voice channel.
        afk_timeout: :class:`int`
            The AFK timeout in seconds.

            After a member being AFK in a voice channel for this amount of time, they will be moved to the AFK channel.

            .. note::
                If :attr:`Guild.afk_channel_id` is :data:`None`, this will disconnect the member from voice instead of moving them.
        widget_enabled: NotRequired[:class:`bool`]
            If the server widget is enabled.
        widget_channel_id: NotRequired[:class:`str` | :data:`None`]
            The ID of the channel the server widget will create a invite for. This is :data:`None` if it is set to no channel.

            .. warning::
                This might not be :data:`None` even though the widget is not enabled.
        verification_level: :class:`VerificationLevel`
            Verification level required to communicate in a guild.

            If a user does not pass these requirements, :attr:`Member.pending` will be :data:`False` until they pass.
        default_message_notifications: :class:`MessageNotificationsLevel`
            The default message notifications level for the guild.
        explicit_content_filter: :class:`ExplicitContentFilterLevel`
            The explicit content filter level for the guild.

            Attachments sent by human members that do not pass the filter will not be sent.
        roles: list[:class:`Role`]
            Roles in the guild.
        emojis: list[:class:`Emoji`]
            Custom emojis added to the guild.
        features: list[:class:`GuildFeature`]
            Enabled guild features.
        mfa_level: :class:`MFALevel`
            The MFA/2fa level for the guild.
        application_id: :class:`str` | :data:`None`
            The ID of the application that created the guild if it was created by a bot.
        system_channel_id: :class:`str` | :data:`None`
            The ID of the channel that is used for system messages.
        system_channel_flags: :class:`int`
            The bitwise flags for what should be sent to the system channel.
        rules_channel_id: :class:`str` | :data:`None`
            The ID of the text channel that is used for rules. In the Discord client, this channel will receive a special "rules" icon.

            .. note::
                This is only set for guilds with the :class:`COMMUNITY <GuildFeature>` feature.
        joined_at: NotRequired[:class:`str`]
            A ISO8601 timestamp of when the current user joined the guild.

            .. note::
                This is only sent in the ``GUILD_CREATE`` event.

        large: NotRequired[:class:`bool`]
            If the guild is considered large by discord

            .. note::
                This is only sent in the ``GUILD_CREATE`` event.
        member_count: NotRequired[:class:`int`]
            How many members are in the guild.

            .. note::
                This is only sent in the ``GUILD_CREATE`` event.
        voice_states: list[:class:`VoiceState`]
            Voice states of members in the guild.

            .. note::
                This is only sent in the ``GUILD_CREATE`` event.
        members: list[:class:`Member`]
            Members in the guild.

            .. note::
                This is only sent in the ``GUILD_CREATE`` event.
        channels: list[:class:`Channel`]
            Channels in the guild.

            .. note::
                This is only sent in the ``GUILD_CREATE`` event.
            .. note::
                Threads are not included in this list. See :attr:`Guild.threads` for threads.
        threads: list[:class:`Channel`]
            Active threads in the guild that the bot can view.

            .. note::
                This is only sent in the ``GUILD_CREATE`` event.
        presences: list[:class:`PresenceUpdate`]
            The members' presences in the guild.

            .. note::
                This is only sent in the ``GUILD_CREATE`` event.
            .. note::
                :attr:`PresenceUpdate.guild_id` will not be set. This should be inferred from :attr:`Guild.id`.
            .. note::
                If the server is :attr:`Guild.large`, offline members' presences are not sent.
        max_presences: NotRequired[:class:`int` | :data:`None`]
            How many members can have a presence at once.

            .. note::
                This always :data:`None` unless in the largest of guilds.
        max_members: NotRequired[:class:`int`]
            How many members can be in the guild before people get errors when trying to join.
        vanity_url_code: :class:`str` | :data:`None`
            A custom invite code for the guild. This code can be used as a normal invite.
        description: :class:`str` | :data:`None`
            The guild's description.

            .. note::
                This is locked behind the ``COMMUNITY`` feature.
        banner: :class:`str` | :data:`None`
            The guild's banner hash.
        premium_tier: :class:`PremiumTier`
            Which server boost level the guild is at.
        premium_subscription_count: NotRequired[:class:`int`]
            How many boosts the guild has.
        preferred_locale: :class:`Locale`
            The guild's preferred locale. This is used in server discovery and notices from discord. This will also be sent in :class:`Interaction` payloads.

            The default is ``en-US``.
        public_updates_channel_id: :class:`str` | :data:`None`
            The ID of the channel that is used for community updates.

            .. note::
                This is locked behind the ``COMMUNITY`` feature.
        max_video_channel_users: NotRequired[:class:`int`]
            The maximum number of users allowed in a voice channel when someone is sending video (video / streaming).
        approximate_member_count: NotRequired[:class:`int`]
            The approximate number of members in the guild.

            .. note::
                This is only returned from the ``GET /guilds/{guild_id}`` endpoint when ``with_counts`` is set to :data:`True`.
        approximate_presence_count: NotRequired[:class:`int`]
            The approximate number of non-offline members in the guild.

            .. note::
                This is only returned from the ``GET /guilds/{guild_id}`` endpoint when ``with_counts`` is set to :data:`True`.
        welcome_screen: NotRequired[:class:`WelcomeScreen`]
            The welcome screen settings for the guild.
        nsfw_level: :class:`NSFWLevel`
            The guild's nsfw level.
        stage_instances: NotRequired[list[:class:`StageInstance`]]
            The guild's currently running stages.

            .. note::
                This is only sent in the ``GUILD_CREATE`` event.
        stickers: NotRequired[list[:class:`Sticker`]]
            Custom stickers uploaded to the guild
        guild_scheduled_events: NotRequired[list[:class:`GuildScheduledEvent`]]
            The guild's scheduled events.

            .. note::
                This is only sent in the ``GUILD_CREATE`` event.
        premium_progress_bar_enabled: :class:`bool`
            Whether the guild has the boost progress bar enabled. This is used by the Discord client.
        """

        name: str
        icon: str | None
        icon_hash: NotRequired[str | None]
        splash: str | None
        discovery_splash: str | None
        owner: NotRequired[bool]
        owner_id: str
        permissions: NotRequired[str]
        region: NotRequired[str | None]
        afk_channel_id: str | None
        afk_timeout: int
        widget_enabled: NotRequired[bool]
        widget_channel_id: NotRequired[str | None]
        verification_level: VerificationLevel
        default_message_notifications: MessageNotificationsLevel
        explicit_content_filter: ExplicitContentFilterLevel
        roles: list[Role]
        emojis: list[Emoji]
        features: list[GuildFeature]
        mfa_level: MFALevel
        application_id: str | None
        system_channel_id: str | None
        system_channel_flags: int
        rules_channel_id: str | None
        joined_at: NotRequired[str]
        large: NotRequired[bool]
        # TODO This is violating PEP-8, however it provides better typings. Worth it?
        unavailable: NotRequired[Literal[False]]  # type: ignore [misc]
        member_count: NotRequired[int]
        voice_states: NotRequired[list[VoiceState]]
        members: NotRequired[list[Member]]
        channels: NotRequired[list[Channel]]
        threads: NotRequired[list[Channel]]
        presences: NotRequired[list[PresenceUpdate]]
        max_presences: NotRequired[int | None]
        max_members: NotRequired[int]
        vanity_url_code: str | None
        description: str | None
        banner: str | None
        premium_tier: PremiumTier
        premium_subscription_count: NotRequired[int]
        preferred_locale: Locale
        public_updates_channel_id: str | None
        max_video_channel_users: NotRequired[int]
        approximate_member_count: NotRequired[int]
        approximate_presence_count: NotRequired[int]
        welcome_screen: NotRequired[WelcomeScreen]
        nsfw_level: NSFWLevel
        stage_instances: NotRequired[list[StageInstance]]
        stickers: NotRequired[list[Sticker]]
        guild_scheduled_events: NotRequired[list[GuildScheduledEvent]]
        premium_progress_bar_enabled: bool

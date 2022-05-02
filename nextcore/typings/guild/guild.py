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

    from ..channel import Channel
    from ..common import Snowflake, Locale
    from ..emoji import Emoji
    from .default_message_notification_level import DefaultMessageNotificationLevel
    from .guild_feature import GuildFeature
    from .guild_nsfw_level import GuildNSFWLevel
    from .mfa_level import MFALevel
    from .premium_tier import PremiumTier
    from .verification_level import VerificationLevel


class Guild(TypedDict):
    """A `Guild <https://discord.dev/resources/guild#guild-object-guild-structure>`__ object.

    Attributes
    ----------
    id: :class:`Snowflake`
        The guild's ID.
    name: :class:`str`
        The guild's name.
    icon: :class:`str` | :data:`None`
        The guild's icon hash.
    icon_hash: NotRequired[:class:`str` | :data:`None`]
        The guild's icon hash.

        This is only sent in :class:`Template` objects. When it is not present, you should ignore :attr:`Guild.icon` as it will be :data:`None`.
    splash: :class:`str` | :data:`None`
        The guild's invite splash hash.
    discovery_splash: :class:`str` | :data:`None`
        The guild's splash in the guild discovery.
    owner: NotRequired[:class:`bool`]
        Whether the current user is the guild owner.

        .. note::
            This is only sent when using OAuth2 using the ``Get current user guilds`` endpoint.
    owner_id: :class:`Snowflake`
        The owner of the guild's ID.
    permissions: :class:`int`
        A bitwise integer representation of the current users permissions in the guild.

        .. note::
            This is only sent when using OAuth2 using the ``Get current user guilds`` endpoint.
    region: NotRequired[:class:`str` | :data:`None`]
        The region the guild is located in.

        .. deprecated:: 1.0.0
            Use :attr:`Channel.rtc_region` instead.
    afk_channel_id: :class:`Snowflake` | :data:`None`
        The ID of the voice channel that is used for members idle in voice channels.
    afk_timeout: :class:`int`
        The amount of time in seconds that a user must be idle in a voice channel before they will be moved to :attr:`Guild.afk_channel_id`.
    widget_enabled: NotRequired[:class:`bool`]
        Whether the guild has widget enabled.
    widget_channel_id: NotRequired[:class:`Snowflake` | :data:`None`]
        The ID of the channel that you get invited to via the widget. If this is :data:`None`, you cannot join the guild via the widget.
    verification_level: :class:`VerificationLevel`
        The guild's verification level for members to talk.
    default_message_notifications: :class:`DefaultMessageNotificationLevel`
        The default notification level for new :class:`Members <GuildMember>`
    explicit_content_filter: :class:`ExplicitContentFilterLevel`
        The level of filter that the guild has for message attachments.
    roles: list[:class:`Role`]
        The roles in the guild.
    emojis: list[:class:`Emoji`]
        The custom emojis in the guild.
    features: list[:class:`GuildFeature`]
        The features that the guild has. These are used to toggle functionality on and off.
    application_id: :class:`Snowflake` | :data:`None`
        The ID of the application that created the guild if it was created by a bot.
    system_channel_id: :class:`Snowflake` | :data:`None`
        The ID of the channel where events such as boosts and join messages are posted.
    system_channel_flags: :class:`int`
        The bitwise flags for the system channel.

        This selects which system messages will be sent.
    rules_channel_id: :class:`Snowflake` | :data:`None`
        A channel to highlight as the rules channel.

        .. note::
            This is restricted to guilds with the ``COMMUNITY`` feature.
    joined_at: NotRequired[:class:`str`]
        When the current user joined the guild.

        .. note::
            This is only sent when using OAuth2 using the ``Get current user guilds`` endpoint.
    large: NotRequired[:class:`bool`]
        Whether the guild is considered large.
    unavailable: NotRequired[:class:`bool`]
        Whether the guild is unavailable due to a Discord outage.
    member_count: NotRequired[:class:`int`]
        The number of members in the guild.
    voice_states: NotRequired[list[:class:`GuildPartialVoiceState`]]
        The voice states of members connected to voice channels.
    members: NotRequired[list[:class:`GuildMember`]]
        The members in the guild.
    channels: NotRequired[list[:class:`Channel`]]
        The channels in the guild.
    presences: NotRequired[list[:class:`PartialPresenceUpdate`]]
        The presences of members in the guild.

        .. note::
            This will not include offline members if the guild has more members than the large threshold sent when identifying.
    max_presences: NotRequired[:class:`int` | :data:`None`]
        The maximum number of presences for the guild.

        .. note::
            This is :data:`None` for most guilds. This will only be set for the biggest of guilds.
    max_members: NotRequired[:class:`int`]
        The maximum number of members in the guild.
    vanity_url_code: NotRequired[:class:`str` | :data:`None`]
        The vanity vanity code.

        .. note::
            This can only be set if the guild has the ``VANITY_URL`` feature.
    description: :class:`str` | :data:`None`
        The guild's description. This is used in the external embeds of the invite link and in guild discovery.

        .. note::
            This can only be set if the guild has the ``COMMUNITY`` feature.
    banner: :class:`str` | :data:`None`
        The guild's banner hash.

        .. note::
            This can only be set if the guild has the ``BANNER`` feature.
    premium_tier: :class:`PremiumTier`
        The guild's premium tier.
    premium_subscription_count: NotRequired[:class:`int`]
        The amount of boosts the guild has.
    preferred_locale: :class:`Locale`
        The guild's preferred locale. The default is ``en-US``.
    public_updates_channel_id: :class:`Snowflake` | :data:`None`
        The id of the channel where admins and moderators of Community guilds receive notices from Discord
    max_video_channel_users: NotRequired[:class:`int`]
        The maximum number of users allowed in a voice channel where video is being sent (LIVE or camera).
    approximate_member_count: NotRequired[:class:`int`]
        The approximate number of members in the guild.

        .. note::
            This is only sent when using the ``Get guild`` endpoint when ``with_counts`` is set to :data:`True`.
    approximate_presence_count: NotRequired[:class:`int`]
        The approximate number of non-offline members in the guild.

        .. note::
            This is only sent when using the ``Get guild`` endpoint when ``with_counts`` is set to :data:`True`.
    welcome_screen: NotRequired[:class:`WelcomeScreen`]
        The guild's welcome screen.

        .. note::
            This can only be set if the guild has the ``COMMUNITY`` feature.
        .. note::
            This is only sent when using the ``Get invite`` endpoint.
    nsfw_level: :class:`GuildNSFWLevel`
        The guild's nsfw level.
    stage_instances: NotRequired[list[:class:`StageInstance`]]
        The active stages in the guild.
    stickers: NotRequired[list[:class:`Sticker`]]
        The custom stickers added to the guild.
    guild_scheduled_events: NotRequired[list[:class:`GuildScheduledEvent`]]
        The scheduled events in the guild.
    premium_progress_bar_enabled: :class:`bool`
        Whether the guild has the premium progress bar enabled.
    """

    id: Snowflake
    name: str
    icon: str | None
    icon_hash: NotRequired[str | None]
    splash: str | None
    discovery_splash: str | None
    owner: NotRequired[bool]
    owner_id: Snowflake
    permissions: NotRequired[str]
    region: NotRequired[str | None]
    afk_channel_id: Snowflake | None
    afk_timeout: int
    widget_enabled: NotRequired[bool]
    widget_channel_id: NotRequired[Snowflake | None]
    verification_level: VerificationLevel
    default_message_notifications: DefaultMessageNotificationLevel
    explicit_content_filter: ExplicitContentFilterLevel  # TODO: Implement ExplicitContentFilterLevel
    roles: list[Role]  # TODO: Implement Role
    emojis: list[Emoji]
    features: list[GuildFeature]
    mfa_level: MFALevel  # TODO: Implement MFALevel
    application_id: Snowflake | None
    system_channel_id: Snowflake | None
    system_channel_flags: int
    rules_channel_id: Snowflake | None
    joined_at: NotRequired[str]
    large: NotRequired[bool]
    unavailable: NotRequired[bool]
    member_count: NotRequired[int]
    voice_states: list[GuildPartialVoiceState]  # TODO: Implement GuildPartialVoiceState
    members: list[GuildMember]  # TODO: Implement GuildMember
    channels: list[Channel]
    threads: list[Channel]
    presences: list[PartialPresenceUpdate]  # TODO: Implement PartialPresenceUpdate
    max_presences: NotRequired[int | None]
    max_members: NotRequired[int]
    vanity_url_code: str | None
    description: str | None
    banner: str | None
    premium_tier: PremiumTier
    premium_subscription_count: NotRequired[int]
    preferred_locale: Locale
    public_updates_channel_id: Snowflake | None
    max_video_channel_users: NotRequired[int]
    approximate_member_count: NotRequired[int]
    approximate_presence_count: NotRequired[int]
    welcome_screen: NotRequired[WelcomeScreen]  # TODO: Implement WelcomeScreen
    nsfw_level: GuildNSFWLevel
    stage_instances: NotRequired[list[StageInstance]]  # TODO: Implement StageInstance
    stickers: NotRequired[list[Sticker]]  # TODO: Implement Sticker
    guild_scheduled_events: NotRequired[list[GuildScheduledEvent]]  # TODO: Implement GuildScheduledEvent
    premium_progress_bar_enabled: bool

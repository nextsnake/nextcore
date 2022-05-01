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

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

__all__ = ("AuditLogChangeKey",)

# Not documented here due to Sphinx.
# This is documented manually in the docs/typings.rst file.
AuditLogChangeKey: TypeAlias = Literal[
    "afk_channel_id",  # afk channel changed
    "afk_timeout",  # afk timeout duration changed
    "allow",  # a permission on a text or voice channel was allowed for a role
    "application_id",  # application id of the added or removed webhook or bot
    "archived",  # thread is now archived/unarchived
    "asset",  # empty string
    "auto_archive_duration",  # auto archive duration changed
    "available",  # availability of sticker changed
    "avatar_hash",  # user avatar changed
    "banner_hash",  # guild banner changed
    "bitrate",  # voice channel bitrate changed
    "channel_id",  # channel for invite code or guild scheduled event changed
    "code",  # invite code changed
    "color",  # role color changed
    "command_id",  # permissions for a command were updated
    "communication_disabled_until",  # member timeout state changed
    "deaf",  # user server deafened/undeafened
    "default_auto_archive_duration",  # default auto archive duration for newly created threads changed
    "default_message_notifications",  # default message notification level changed
    "deny",  # a permission on a text or voice channel was denied for a role
    "description",  # description changed
    "discovery_splash_hash",  # discovery splash changed
    "enable_emoticons",  # integration emoticons enabled/disabled
    "entity_type",  # entity type of guild scheduled event was changed
    "expire_behavior",  # integration expiring subscriber behavior changed
    "expire_grace_period",  # integration expire grace period changed
    "explicit_content_filter",  # change in whose messages are scanned and deleted for explicit content in the server
    "format_type",  # format type of sticker changed
    "guild_id",  # guild sticker is in changed
    "hoist",  # role is now displayed/no longer displayed separate from online users
    "icon_hash",  # icon changed
    "image_hash",  # guild scheduled event cover image changed
    "id",  # the id of the changed entity - sometimes used in conjunction with other keys
    "invitable",  # private thread is now invitable/uninvitable
    "inviter_id",  # person who created invite code changed
    "location",  # change in channel id for guild scheduled event
    "locked",  # thread is now locked/unlocked
    "max_age",  # how long invite code lasts changed
    "max_uses",  # change to max number of times invite code can be used
    "mentionable",  # role is now mentionable/unmentionable
    "mfa_level",  # two-factor auth requirement changed
    "mute",  # user server muted/unmuted
    "name",  # name changed
    "nick",  # user nickname changed
    "nsfw",  # channel nsfw restriction changed
    "owner_id",  # owner changed
    "permission_overwrites",  # permissions on a channel changed
    "permissions",  # permissions for a role changed
    "position",  # text or voice channel position changed
    "preferred_locale",  # preferred locale changed
    "privacy_level",  # privacy level of the stage instance changed
    "prune_delete_days",  # change in number of days after which inactive and role-unassigned members are kicked
    "public_updates_channel_id",  # id of the public updates channel changed
    "rate_limit_per_user",  # amount of seconds a user has to wait before sending another message changed
    "region",  # region changed
    "rules_channel_id",  # id of the rules channel changed
    "splash_hash",  # invite splash page artwork changed
    "status",  # status of guild scheduled event was changed
    "system_channel_id",  # id of the system channel changed
    "tags",  # related emoji of sticker changed
    "temporary",  # invite code is temporary/never expires
    "topic",  # text channel topic or stage instance topic changed
    "type",  # type of entity created
    "unicode_emoji",  # role unicode emoji changed
    "user_limit",  # new user limit in a voice channel
    "uses",  # number of times invite code used changed
    "vanity_url_code",  # guild invite vanity url changed
    "verification_level",  # required verification level changed
    "widget_channel_id",  # channel id of the server widget changed
    "widget_enabled",  # server widget enabled/disable
    "$add",  # new role added
    "$remove",  # role removed
]

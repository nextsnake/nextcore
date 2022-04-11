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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .activity import Activity
    from .activity_assets import ActivityAssets
    from .activity_button import ActivityButton
    from .activity_party import ActivityParty
    from .activity_secrets import ActivitySecrets
    from .activity_timestamps import ActivityTimestamps
    from .activity_type import ActivityType
    from .channel import Channel
    from .channel_type import ChannelType
    from .emoji import Emoji
    from .explicit_content_filter_level import ExplicitContentFilterLevel
    from .guild import Guild
    from .guild_feature import GuildFeature
    from .locale import Locale
    from .member import Member
    from .message_notifications_level import MessageNotificationsLevel
    from .mfa_level import MFALevel
    from .permission_overwrite import PermissionOverwrite
    from .permission_overwrite_type import PermissionOverwriteType
    from .role import Role
    from .role_tags import RoleTags
    from .session_start_limit import SessionStartLimit
    from .status_type import StatusType
    from .unavailable_guild import UnavailableGuild
    from .update_presence import UpdatePresence
    from .user import User
    from .verification_level import VerificationLevel

    __all__ = (
        "Activity",
        "ActivityAssets",
        "ActivityButton",
        "ActivityParty",
        "ActivitySecrets",
        "ActivityTimestamps",
        "ActivityType",
        "Channel",
        "ChannelType",
        "Emoji",
        "ExplicitContentFilterLevel",
        "Guild",
        "GuildFeature",
        "Locale",
        "Member",
        "MessageNotificationsLevel",
        "MFALevel",
        "PermissionOverwrite",
        "PermissionOverwriteType",
        "Role",
        "RoleTags",
        "SessionStartLimit",
        "StatusType",
        "UnavailableGuild",
        "UpdatePresence",
        "VerificationLevel",
        "User",
        "VerificationLevel",
    )

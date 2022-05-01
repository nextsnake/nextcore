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

# Not documented here due to Sphinx.
# This is documented manually in the docs/typings.rst file.
AuditLogEvent: TypeAlias = Literal[
    1,  # GUILD_UPDATE
    10,  # CHANNEL_CREATE
    11,  # CHANNEL_UPDATE
    12,  # CHANNEL_DELETE
    13,  # CHANNEL_OVERWRITE_CREATE
    14,  # CHANNEL_OVERWRITE_UPDATE
    15,  # CHANNEL_OVERWRITE_DELETE
    20,  # MEMBER_KICK
    21,  # MEMBER_PRUNE
    22,  # MEMBER_BAN_ADD
    23,  # MEMBER_BAN_REMOVE
    24,  # MEMBER_UPDATE
    25,  # MEMBER_ROLE_UPDATE
    26,  # MEMBER_MOVE
    27,  # MEMBER_DISCONNECT
    28,  # BOT_ADD
    30,  # ROLE_CREATE
    31,  # ROLE_UPDATE
    32,  # ROLE_DELETE
    40,  # INVITE_CREATE
    41,  # INVITE_UPDATE
    42,  # INVITE_DELETE
    50,  # WEBHOOK_CREATE
    51,  # WEBHOOK_UPDATE
    52,  # WEBHOOK_DELETE
    60,  # EMOJI_CREATE
    61,  # EMOJI_UPDATE
    62,  # EMOJI_DELETE
    72,  # MESSAGE_DELETE
    73,  # MESSAGE_BULK_DELETE
    74,  # MESSAGE_PIN
    75,  # MESSAGE_UNPIN
    80,  # INTEGRATION_CREATE
    81,  # INTEGRATION_UPDATE
    82,  # INTEGRATION_DELETE
    83,  # STAGE_INSTANCE_CREATE
    84,  # STAGE_INSTANCE_UPDATE
    85,  # STAGE_INSTANCE_DELETE
    90,  # STICKER_CREATE
    91,  # STICKER_UPDATE
    92,  # STICKER_DELETE
    100,  # GUILD_SCHEDULED_EVENT_CREATE
    101,  # GUILD_SCHEDULED_EVENT_UPDATE
    102,  # GUILD_SCHEDULED_EVENT_DELETE
    110,  # THREAD_CREATE
    111,  # THREAD_UPDATE
    112,  # THREAD_DELETE
    121,  # APPLICATION_COMMAND_PERMISSION_UPDATE
]

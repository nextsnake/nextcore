# The MIT License (MIT)
# Copyright (c) 2021-present nextsnake developers

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

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

    from .user import User

    class Member(TypedDict):
        user: NotRequired[User]
        """The user that is a member of the guild."""
        nick: NotRequired[str]
        """The user's nickname in the guild. Not present if the user has no nickname."""
        avatar: NotRequired[str]
        """The user's avatar in the guild. Not present if the user has no guild spesific avatar."""
        roles: list[str]
        """The user's roles in the guild. This is a list of role IDs."""
        joined_at: str
        """When the user joined the guild. This is a ISO8601 timestamp"""
        premium_since: NotRequired[str | None]
        """When the user started boosting the guild. This is a ISO8601 timestamp."""
        deaf: bool
        """Whether the user is server deafened in voice channels."""
        mute: bool
        """Whether the user is server muted in voice channels."""
        pending: NotRequired[bool]
        """Whether the user is pending verification. This will not be set in non GUILD_* events where the user has to finish verification."""
        permissions: NotRequired[str]
        """The user's permissions in the guild. This is a bitwise Permission flag"""
        communication_disabled_until: NotRequired[str | None]
        """ISO8601 Timestamp of when the user's timeout ends. None or a time in the past if the user is not timed out."""

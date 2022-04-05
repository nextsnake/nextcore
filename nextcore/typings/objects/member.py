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

    from .user import User

    class Member(TypedDict):
        """A member of a guild.
        
        Attributes
        ----------
        user: NotRequired[:class:`User`]
            The user that is a member of the :class:`Guild`. This is provided seperately in `MESSAGE_CREATE` and `MESSAGE_UPDATE` events.
        nick: NotRequired[:class:`str`]
            The nickname of the user in this :class:`Guild`. Not present if the user has no nickname.
        avatar: NotRequired[:class:`str`]
            The avatar hash of this user's :class:`Guild` avatar. Not present if the user has no :class:`Guild` avatar.
        roles: list[:class:`str`]
            A list of :attr:`Role.id`'s that this member has.
        joined_at: str
            When the user joined the guild. This is a ISO8601 timestamp.
        premium_since: NotRequired[:class:`str` | :data:`None`]
            When the user started boosting the guild. This is a ISO8601 timestamp.
        deaf: :class:`bool`
            Whether the user is server deafened in voice channels.
        mute: :class:`bool`
            Whether the user is server muted in voice channels.
        pending: NotRequired[:class:`bool`]
            Whether the user is pending verification. This will not be set in non GUILD_* events where the user has to finish verification.
        permissions: :class:`str`
            The members guild permissions. This is a bitwise Permission flag.
        communication_disabled_until: NotRequired[:class:`str` | :data:`None`]
            ISO8601 Timestamp of when the user's timeout ends. None or a time in the past if the user is not timed out.
        """
        user: NotRequired[User]
        nick: NotRequired[str]
        avatar: NotRequired[str]
        roles: list[str]
        joined_at: str
        premium_since: NotRequired[str | None]
        deaf: bool
        mute: bool
        pending: NotRequired[bool]
        permissions: NotRequired[str]
        communication_disabled_until: NotRequired[str | None]

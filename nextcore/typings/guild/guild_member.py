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

__all__ = ("GuildMember",)

class GuildMember(TypedDict):
    """A `Guild Member <https://discord.com/developers/docs/resources/guild#guild-member-object-guild-member-structure>`__ object.
    
    Attributes
    ----------
    user: :class:`User`
        The :class:`User` this member is representing.
    nick: NotRequired[:class:`str` | :data:`None`]
        The nickname of this member.
    avatar: NotRequired[:class:`str` | :data:`None`]
        The avatar hash of this member.
    roles: list[:class:`Snowflake`]
        The roles this member has.
    joined_at: NotRequired[:class:`str` | :data:`None`]
        The date and time this member joined the guild.
    premium_since: NotRequired[:class:`str` | :data:`None`]
        The date and time this member started boosting the guild.
    deaf: :class:`bool`
        Whether this member is server deafened in voice channels.
    mute: :class:`bool`
        Whether this member is server muted in voice channels.
    pending: NotRequired[:class:`bool`]
        Whether this member is pending membership screening.

        .. note::
            In ``GUILD_`` events, :attr:`GuildMember.pending` will always be included as :data:`True` or false.

            In non ``GUILD_`` events which can only be triggered by non-:class:`attr:`GuildMember.pending` users, :attr:`GuildMember.pending` will not be included.
    """
    user: User # TODO: Implement User
    nick: NotRequired[str | None]
    avatar: NotRequired[str | None]
    roles: list[Snowflake]
    joined_at: NotRequired[str]
    premium_since: NotRequired[str | None]
    deaf: bool
    mute: bool
    pending: NotRequired[bool]
    permissions: NotRequired[str]
    communication_disabled_until: NotRequired[str | None]


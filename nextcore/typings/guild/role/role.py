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
    from ...common import Snowflake
    from .role_tags import RoleTags

    from typing_extensions import NotRequired

__all__ = ("RoleTags",)

class Role(TypedDict):
    """A `Role <https://discord.dev/topics/permissions#role-object-role-structure>`__ object

    Attributes
    ----------
    id: :class:`Snowflake`
        The role's ID.

        This uses the same ID as the :attr:`Guild.id` if this is the ``@everyone`` role.
    name: :class:`str`
        The role's name.
    color: :class:`int`
        The role's color as a :class:`int` representation of a hex color.
    hoist: :class:`bool`
        If the role will show server members with this role separately from other members if it is the highest role the :class:`GuildMember` has.
    icon: NotRequired[:class:`str` | :data:`None`]
        The role's icon hash.

        .. note::
            The role can only have an icon or a :attr:`Role.unicode_emoji`, not both.
    unicode_emoji: NotRequired[:class:`str` | :data:`None`]
        The role's unicode emoji to use as a role icon.

        .. note::
            The role can only have an icon or a :attr:`Role.unicode_emoji`, not both.
    position: :class:`int`
        The position of the role in the role hierarchy. The ``@everyone`` role always has a position of ``0``.
    permissions: :class:`int`
        A bitwise permissions flag
    managed: :class:`bool`
        If the role is managed by an integration.

        This means the role cannot be manually assigned to a :class:`GuildMember`
    mentionable: :class:`bool`
        If the role can be mentioned by :class:`members <GuildMember>` without the ``MENTION_EVERYONE`` permission.
    tags: NotRequired[:class:`RoleTags`]
        Metadata about the role.
    """
    id: Snowflake
    name: str
    color: int
    hoist: bool
    icon: NotRequired[str | None]
    unicode_emoji: NotRequired[str | None]
    position: int
    permissions: int
    managed: bool
    mentionable: bool
    tags: NotRequired[RoleTags]


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

    from .role_tags import RoleTags

    class Role(TypedDict):
        """A role in a :class:`Guild`.

        Attributes
        ----------
        id: :class:`str`
            The ID of the role.
        name: :class:`str`
            The name of the role.
        color: :class:`int`
            The color of the role.
            The role color highest up in the hierarchy is the one displayed on clients.
            If this is 0 it will not count towards a :class:`Member`'s color.
        hoist: :class:`bool`
            Whether the role is displayed separately in the member list.
        icon: NotRequired[:class:`str` | :data:`None`]
            The role's icon hash of the role.
        unicode_emoji: NotRequired[:class:`str` | :data:`None`]
            The role's icon emoji.
        position: :class:`int`
            The position in the list of roles. If two positions are equal, then the roles are sorted by id.
        permissions: :class:`int`
            The permissions for the role. This is a bitwise Permissions flag.
        managed: :class:`bool`
            Whether the role is managed by an integration.
        mentionable: :class:`bool`
            Whether the role is mentionable by everyone
        tags: NotRequired[:class:`RoleTags`]
            Info about the managed role.
        """

        id: str
        name: str
        color: int
        hoist: bool
        icon: NotRequired[str | None]
        unicode_emoji: NotRequired[str | None]
        position: int
        permissions: str
        managed: bool
        mentionable: bool
        tags: NotRequired[RoleTags]

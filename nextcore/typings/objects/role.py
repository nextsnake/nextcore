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
        id: int
        """The role's ID"""
        name: str
        """The role's name"""
        color: int
        """The role's color. If this is 0 it will not count towards a user's color"""
        hoist: bool
        """Whether the role is hoisted in the member sidebar"""
        icon: NotRequired[str | None]
        """The role's icon hash"""
        unicode_emoji: NotRequired[str | None]
        """The role's unicode emoji, used as a role icon"""
        position: int
        """The role's position in the list of roles"""
        permissions: str
        """The role's permissions"""
        managed: bool
        """Whether the role is managed by an integration"""
        mentionable: bool
        """Whether the role can be mentioned by everyone"""
        tags: NotRequired[RoleTags]

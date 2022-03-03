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

    from .role import Role
    from .user import User

    class Emoji(TypedDict):
        id: str | None
        """The emoji's ID"""
        name: str | None
        """The emoji's name. Can be None in reactions"""
        roles: NotRequired[Role]
        """Roles allowed to use this emoji. If this is not set, everyone can use it"""
        user: NotRequired[User]
        """The user who created this emoji"""
        require_colons: NotRequired[bool]
        """Whether this emoji must be wrapped in colons"""
        managed: NotRequired[bool]
        """Whether this emoji is managed by an integration"""
        animated: NotRequired[bool]
        """Whether this emoji is animated"""
        available: NotRequired[bool]
        """Whether this emoji is available to use. This may be due to losing a nitro boost level."""

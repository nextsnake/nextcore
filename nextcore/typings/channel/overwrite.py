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
    from typing import Literal

    from ..common import Snowflake


class Overwrite(TypedDict):
    """A `Overwrite <https://discord.dev/resources/channel#overwrite-object-overwrite-structure>`__ object.

    This can be added to :attr:`Channel.permission_overwrites` to change the permissions of a user or role for that specific channel.

    If a permission is not in :attr:`Overwrite.allow` or :attr:`Overwrite.deny`, it will be inherited from the :class:`Member's <Member>` :class:`Guild` permissions.

    Attributes
    ----------
    id: :class:`Snowflake`
        The ID of the user or role to change permissions for.
    type: :class:`Literal[0, 1]`
        The type of the overwrite. ``0`` for user, ``1`` for role.
    allow: :class:`int`
        The :class:`Permission` bitset for explicitly allowed permissions.
    deny: :class:`int`
        The :class:`Permission` bitset for explicitly denied permissions.
    """

    id: Snowflake
    type: Literal[0, 1]
    allow: int
    deny: int

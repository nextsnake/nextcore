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

from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from ..common import Snowflake
    from typing_extensions import NotRequired

__all__ = ("Emoji", )

class Emoji(TypedDict):
    """A `Emoji <https://discord.dev/resources/emoji#emoji-object-emoji-structure>`__ object.

    Example custom emoji:

    .. code-block:: json

        {
            "id": "41771983429993937",
            "name": "LUL",
            "roles": ["41771983429993000", "41771983429993111"],
            "user": {
                "username": "Luigi",
                "discriminator": "0002",
                "id": "96008815106887111",
                "avatar": "5500909a3274e1812beb4e8de6631111",
                "public_flags": 131328
            },
            "require_colons": true,
            "managed": false,
            "animated": false
        }

    Example standard emoji:

    .. code-block:: json
        
        {
            "id": null,
            "name": "🔥"
        }



    Attributes
    ----------
    id: :class:`Snowflake` | :data:`None`
        The emoji's ID.

        This will be :data:`None` if this is a standard emoji.
    name: :class:`str` | :data:`None`
        The emoji's name.

        .. note::
            This can be only be :data:`None` in :class:`ReactionEmoji` objects.

            This can be due to the emote being deleted.
    roles: NotRequired[list[:class:`Snowflake`]]
        A list of role IDs that can use this emoji.
    user: NotRequired[:class:`User`]
        The user that created this emoji.

        .. note::
            Not sent for standard emojis.
    require_colons: NotRequired[:class:`bool`]
        Whether this emoji must be wrapped in colons.
    managed: NotRequired[:class:`bool`]
        Whether this emoji is managed by a :class:`Integration`.
    animated: NotRequired[:class:`bool`]
        Whether this emoji is animated.

        This will count towards the animated emoji limit.
    available: NotRequired[:class:`bool`]
        Whether this emoji is available to use.

        This may be :data:`False` for when a emoji is no longer usable due to loosing a boost tier.
    """
    id: Snowflake | None
    name: str | None
    roles: NotRequired[list[Snowflake]]
    user: NotRequired[User] # TODO: Implement User
    require_colons: NotRequired[bool]
    managed: NotRequired[bool]
    animated: NotRequired[bool]
    available: NotRequired[bool]

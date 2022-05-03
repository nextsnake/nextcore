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
    from ..emoji import Emoji
    from .guild_feature import GuildFeature

__all__ = ("GuildPreview",)

class GuildPreview(TypedDict):
    """A `Guild <https://discord.dev/resources/guild#guild-preview-object-guild-preview-structure>`__ object.

    Attributes
    ----------
    id: :class:`Snowflake`
        The guild's ID.
    name: :class:`str`
        The guild's name.
    icon: :class:`str` | :data:`None`
        The guild's icon hash.
    splash: :class:`str` | :data:`None`
        The guild's invite splash hash.
    discovery_splash: :class:`str` | :data:`None`
        The guild's splash in the guild discovery.
    emojis: list[:class:`Emoji`]
        The custom emojis in the guild.
    features: list[:class:`GuildFeature`]
        The features that the guild has. These are used to toggle functionality on and off.
    approximate_member_count: NotRequired[:class:`int`]
        The approximate number of members in the guild.

        .. note::
            This is only sent when using the ``Get guild`` endpoint when ``with_counts`` is set to :data:`True`.
    approximate_presence_count: NotRequired[:class:`int`]
        The approximate number of non-offline members in the guild.

        .. note::
            This is only sent when using the ``Get guild`` endpoint when ``with_counts`` is set to :data:`True`.
    stickers: NotRequired[list[:class:`Sticker`]]
        The custom stickers added to the guild.
    description: :class:`str` | :data:`None`
        The guild's description. This is used in the external embeds of the invite link and in guild discovery.

        .. note::
            This can only be set if the guild has the ``COMMUNITY`` feature.

    """

    id: Snowflake
    name: str
    icon: str | None
    splash: str | None
    discovery_splash: str | None
    emojis: list[Emoji]
    features: list[GuildFeature]
    approximate_member_count: NotRequired[int]
    approximate_presence_count: NotRequired[int]
    stickers: NotRequired[list[Sticker]]  # TODO: Implement Sticker
    description: str | None

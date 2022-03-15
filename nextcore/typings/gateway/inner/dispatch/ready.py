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

    from ....objects.unavailable_guild import UnavailableGuild
    from ....objects.user import User

    class ReadyData(TypedDict):
        """The inner payload for the READY event

        Read the `documentation <https://discord.dev/topics/gateway#ready>`__

        Attributes
        ----------
        v: :class:`int`
            The Discord gateway version.
        user: :class:`User`
            The current bot.
        guilds: list[:class:`UnavailableGuild`]
            The list of guilds the bot is in.
        session_id: :class:`str`
            The current session ID. Used for resuming the connection
        shard: NotRequired[tuple[:class:`int`, :class:`int`]]
            The shard information sent when identifying.
        application: NotRequired[dict[:class:`str`, :class:`int`]]
            The application information sent when identifying. This only contains the ID and flags attributes.
        """
        v: int
        user: User
        guilds: list[UnavailableGuild]
        session_id: str
        shard: NotRequired[tuple[int, int]]
        application: NotRequired[dict[str, int]]  # TODO: What do we do about partials?

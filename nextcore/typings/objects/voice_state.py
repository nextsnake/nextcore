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

    from .member import Member

    class VoiceState(TypedDict):
        """A :class:`Member`s' voice state.

        Attributes
        ----------
        guild_id: NotRequired[:class:`str`]
            The guild ID this voice state is for.
        channel_id: :class:`str` | :data:`None`
            The ID of the voice channel this member is currently in.
        user_id: :class:`str`
            The :class:`User`s' ID this voice state is for.
        member: NotRequired[:class:`Member`]
            The :class:`Member` this voice state is for.
        session_id: :class:`str`
            The voice session ID for this member.
        deaf: :class:`bool`
            Whether this member is server deafened.
        mute: :class:`bool`
            Whether this member is server muted.
        self_deaf: :class:`bool`
            Whether this member has deafened themselves.
        self_mute: :class:`bool`
            Whether this member has muted themselves.
        self_stream: NotRequired[:class:`bool`]
            Whether this member is streaming.
        self_video: :class:`bool`
            Whether this member has turned on their webcam.
        suppress: :class:`bool`
            Muted by the bot. Doesn't seem to be used for bots.
        request_to_speak_timestamp: :class:`str`
            ISO8601 timestamp of when the user requested to speak in a stage channel.
        """
        guild_id: NotRequired[str]
        channel_id: str | None
        user_id: str
        member: NotRequired[Member]
        session_id: str
        deaf: bool
        mute: bool
        self_deaf: bool
        self_mute: bool
        self_stream: NotRequired[bool]
        self_video: bool
        suppress: bool
        request_to_speak_timestamp: str | None

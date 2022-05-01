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

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

# Not documented here due to Sphinx.
# This is documented manually in the docs/typings.rst file.
ChannelType: TypeAlias = Literal[
    0,  # a text channel within a server
    1,  # a direct message between users
    2,  # a voice channel within a server
    3,  # a direct message between multiple users
    4,  # an organizational category that contains up to 50 channels
    5,  # a channel that users can follow and crosspost into their own server
    10,  # a temporary sub-channel within a GUILD_NEWS channel
    11,  # a temporary sub-channel within a GUILD_TEXT channel
    12,  # a temporary sub-channel within a GUILD_TEXT channel that is only viewable by those invited and those with the MANAGE_THREADS permission
    13,  # a voice channel for hosting events with an audience
    14,  # the channel in a hub containing the listed servers
    15,  # (still in development) a channel that can only contain threads
]

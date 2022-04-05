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

    class SessionStartLimit(TypedDict):
        """Information about how much you can connect to the gateway.
        
        Attributes
        ----------
        total: :class:`int`
            How many times total you can send a IDENTIFY payload per hour. If this limit is hit the bot token will get reset and the bot owner will get a system message.
        remaining: :class:`int`
            How many times you can send a IDENTIFY payload before you hit the limit. If this limit is hit the bot token will get reset and the bot owner will get a system message.
        reset_after: :class:`int`
            When the ratelimit resets in seconds.
        max_concurrency: :class:`int`
            How many concurrent IDENTIFY payloads can be sent to the gateway.
        """
        total: int
        remaining: int
        reset_after: int
        max_concurrency: int

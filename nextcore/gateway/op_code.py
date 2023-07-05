# The MIT License (MIT)
# Copyright (c) 2021-present tag-epic
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

from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final

__all__: Final[tuple[str, ...]] = ("GatewayOpcode",)


class GatewayOpcode(IntEnum):
    """Enum of all opcodes that can be sent/received to/from the gateway."""

    DISPATCH = 0
    """Can be received"""
    HEARTBEAT = 1
    """Can be sent/received"""
    IDENTIFY = 2
    """Can be sent"""
    PRESENCE_UPDATE = 3
    """Can be sent"""
    VOICE_STATE_UPDATE = 4
    """Can be sent"""
    RESUME = 6
    """Can be sent"""
    RECONNECT = 7
    """Can be received"""
    REQUEST_GUILD_MEMBERS = 8
    """Can be sent"""
    INVALID_SESSION = 9
    """Can be received"""
    HELLO = 10
    """Can be received"""
    HEARTBEAT_ACK = 11
    """Can be received"""

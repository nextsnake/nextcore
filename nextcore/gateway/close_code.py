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

__all__: Final[tuple[str, ...]] = ("GatewayCloseCode",)


class GatewayCloseCode(IntEnum):
    """A gateway close code.

    .. note::
        Read the `documentation <https://discord.dev/topics/opcodes-and-status-codes#gateway>`_
    """

    UNKNOWN_ERROR = 4000
    """An unknown error occurred."""
    UNKNOWN_OPCODE = 4001
    """We sent a invalid gateway opcode."""
    DECODE_ERROR = 4002
    """We sent a invalid payload."""
    NOT_AUTHENTICATED = 4003
    """We sent a payload before we were authenticated."""
    AUTHENTICATION_FAILED = 4004
    """We sent a invalid token."""
    ALREADY_AUTHENTICATED = 4005
    """We tried to authenticate more than once."""
    INVALID_SEQUENCE = 4007
    """We tried to resume with a invalid sequence id."""
    RATE_LIMITED = 4008
    """We sent payloads too fast."""
    SESSION_TIMEOUT = 4009
    """Your session timed out."""
    INVALID_SHARD = 4010
    """We sent an invalid shard id or our shard count is too low."""
    SHARDING_REQUIRED = 4011
    """Sharding is required to continue."""
    INVALID_API_VERSION = 4012
    """We sent an invalid api version."""
    INVALID_INTENTS = 4013
    """We sent invalid intents."""
    DISALLOWED_INTENTS = 4014
    """We sent intents that are not allowed to use."""

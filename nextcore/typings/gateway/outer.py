# The MIT License (MIT)
# Copyright (c) 2021-present nextsnake developers

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

"""
Top level gateway objects. They usually contain inner objects such as :class:`ClientIdentifyPayload`

.. note::
    Classes inside this module only exists if we are typehinting. Please enable future annotations if you wish to use any of these as type-hints.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, TypedDict

    from .inner.dispatch.ready import ReadyData
    from .inner.hello import HelloData

    class _BaseGatewayPayload(TypedDict):
        """
        Gateway payload sent by either the client or the server
        """

        op: int
        """The gateway opcode. See the `documentation <https://discord.dev/topics/opcodes-and-status-codes#gateway-gateway-opcodes>`_ for a list of opcodes."""

    class ClientGatewayPayload(_BaseGatewayPayload):
        """
        Gateway payload sent by the client/us.
        """

        d: Any
        """The payload data"""

    class ServerGatewayPayload(_BaseGatewayPayload):
        """
        Gateway payload sent by the server/discord.
        """

        d: ReadyData | HelloData
        """The payload data"""
        t: str | None
        """The dispatch event name. This is unused"""

    class ServerGatewayDispatchPayload(ServerGatewayPayload):
        """
        Gateway payload for server dispatch.
        """

        s: int
        """The sequence number used for resuming the session."""
        t: str  # type: ignore
        """The dispatch event name."""

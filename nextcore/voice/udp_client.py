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
import asyncio
from logging import getLogger
from typing import TYPE_CHECKING
import anyio
import struct

VoicePacketHeader = struct.Struct(">HH")

if TYPE_CHECKING:
    from anyio.abc import ConnectedUDPSocket

__all__ = ("UDPClient", )

_logger = getLogger(__name__)

class UDPClient:
    def __init__(self) -> None:
        self.socket: ConnectedUDPSocket | None = None
    
    async def send(self, message: bytes):
        assert self.socket is not None
        _logger.debug("Sent %s", hex(int.from_bytes(message, byteorder="big")))
        await self.socket.send(message)



    async def connect(self, host: str, port: int):
        _logger.info("Connecting to %s:%s", host, port)
        self.socket = await anyio.create_connected_udp_socket(host, port)
        _logger.debug("Connected to %s:%s", host, port)

    async def receive_loop(self):
        assert self.socket is not None
        _logger.debug("Started udp receive loop")

        async for message in self.socket:
            pass
            # _logger.debug("Received %s", message)
        

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
import struct
from nextcore.http import HTTPClient # TODO: Replace with BaseHTTPClient
from typing import TYPE_CHECKING, Any
from nextcore.common import json_loads, json_dumps, Dispatcher
import time

from .udp_client import UDPClient

if TYPE_CHECKING:
    from discord_typings import Snowflake
    from aiohttp import ClientWebSocketResponse

__all__ = ("VoiceClient", )

_logger = getLogger(__name__)

class VoiceClient:
    def __init__(self, guild_id: Snowflake, user_id: Snowflake, session_id: str, token: str, endpoint: str, http_client: HTTPClient) -> None:
        self.guild_id: Snowflake = guild_id
        self.user_id: Snowflake = user_id
        self.session_id: str = session_id
        self.token: str = token # TODO: Replace with Authentication?
        self.endpoint: str = endpoint
        self.ssrc: int | None = None
        self.raw_dispatcher: Dispatcher[int] = Dispatcher()
        self._http_client: HTTPClient = http_client
        self._ws: ClientWebSocketResponse | None = None
        self._socket: UDPClient | None = None

        # Default event handlers
        self.raw_dispatcher.add_listener(self._handle_hello, 8)
        self.raw_dispatcher.add_listener(self._handle_ready, 2)

    async def connect(self) -> None:
        self._ws = await self._http_client.connect_to_voice_websocket(self.endpoint)
        asyncio.create_task(self._receive_loop(self._ws))

    async def send(self, message: Any) -> None:
        if self._ws is None:
            raise RuntimeError("Shame! Shame!") # TODO: Lol
        _logger.debug("Send to websocket: %s", message)
        await self._ws.send_json(message, dumps=json_dumps)


    async def identify(self, guild_id: Snowflake, user_id: Snowflake, session_id: str, token: str) -> None:
        await self.send({
            "op": 0,
            "d": {
                "server_id": guild_id, # Why is this called server_id?
                "user_id": user_id,
                "session_id": session_id,
                "token": token
            }
        })

    async def heartbeat(self) -> None:
        await self.send({
            "op": 3,
            "d": int(time.time()) # This should not be frequent enough that it becomes a issue.
        })
        
    async def _receive_loop(self, ws: ClientWebSocketResponse) -> None:
        _logger.debug("Started listening for messages")
        async for message in ws:
            data = message.json(loads=json_loads) # TODO: Type hint!
            _logger.debug("Received data from the websocket: %s", data)
            await self.raw_dispatcher.dispatch(data["op"], data)
        _logger.info("WebSocket closed with code %s!", ws.close_code)

    async def _heartbeat_loop(self, ws: ClientWebSocketResponse, interval_seconds: float) -> None:
        _logger.debug("Started heartbeating every %ss", interval_seconds)
        while not ws.closed:
            await self.heartbeat()
            await asyncio.sleep(interval_seconds)

    async def _handle_hello(self, event_data: dict[str, Any]) -> None:
        assert self._ws is not None, "WebSocket was None in hello"

        await self.identify(self.guild_id, self.user_id, self.session_id, self.token)
        heartbeat_interval_ms = event_data["d"]["heartbeat_interval"]
        heartbeat_interval_seconds = heartbeat_interval_ms / 1000

        asyncio.create_task(self._heartbeat_loop(self._ws, heartbeat_interval_seconds))

    async def _handle_ready(self, event: dict[str, Any]) -> None:
        event_data = event["d"]
        voice_ip = event_data["ip"]
        voice_port = event_data["port"]
        self.ssrc = event_data["ssrc"]

        self._socket = UDPClient()
        await self._socket.connect(voice_ip, voice_port)

        # IP Discovery
        HEADER_SIZE = 4
        PAYLOAD_SIZE = 70
        packet = bytearray(PAYLOAD_SIZE + HEADER_SIZE)
        struct.pack_into(">HHI", packet, 0, 0x1, PAYLOAD_SIZE, self.ssrc)
        await self._socket.send(packet)

        response = await self._socket.socket.receive()

        raw_ip, port = struct.unpack(">8x64sH", response)
        ip = raw_ip.decode("ascii")
        _logger.debug("Got public IP and port from discovery: %s:%s", ip, port)

        asyncio.create_task(self._socket.receive_loop())

        await self.send({"op": 1, "d": {
            "protocol": "udp",
            "data": {
                "address": ip,
                "port": port,
                "mode": "xsalsa20_poly1305_lite"
            }
        }})
        





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
from __future__ import annotations

from asyncio import Event, create_task, sleep
from logging import getLogger
from random import random
from sys import platform
from typing import TYPE_CHECKING, cast

from aiohttp import WSMsgType
from frozendict import frozendict  # type: ignore # No source package?

from ..utils import json_loads
from .decompressor import Decompressor
from .dispatcher import Dispatcher
from .times_per import TimesPer

if TYPE_CHECKING:
    from aiohttp import ClientWebSocketResponse

    from ..http import HTTPClient
    from ..typings.gateway.inner.dispatch.ready import ReadyData
    from ..typings.gateway.inner.hello import HelloData
    from ..typings.gateway.outer import (
        ClientGatewayPayload,
        ServerGatewayDispatchPayload,
        ServerGatewayPayload,
    )
    from ..typings.objects.update_presence import UpdatePresence


class Shard:
    """A discord shard implementation.

    .. note::
        You are probably looking for :class:`nextcore.gateway.Gateway` instead. This class requires you to manually respect max_concurrency and similar things.

    Parameters
    ----------
    shard_id: int
        The shard id.
    shard_count: int
        How many shards there are. This is used to compute which shard gets which events.
    token: str
        The bot token.
    intents: int
        The intents to use.
    http_client: :class:`nextcore.http.HTTPClient`
        HTTP Client to make requests from.
    library_name: str
        The name of the library you are making. If you are not making your own library, please use the default.
    default_presence: :class:`nextcore.objects.update_presence.UpdatePresence`
        The default presence to use when connecting. You should prefer this over :meth:`Shard.update_presence`
    """

    GATEWAY_URL = "wss://gateway.discord.gg?v=9&compress=zlib-stream"

    def __init__(
        self,
        shard_id: int,
        shard_count: int,
        token: str,
        intents: int,
        http_client: HTTPClient,
        *,
        library_name: str = "nextcore",
        default_presence: UpdatePresence | None = None,
    ) -> None:
        self.id: int = shard_id
        """The shard id."""
        self.shard_count: int = shard_count
        """How many shards there are."""
        self.token: str = token
        """The bot token."""
        self.intents: int = intents
        """The intents to use."""
        self.default_presence: UpdatePresence | None = default_presence
        """The default presence to use when connecting."""

        self.ready: Event = Event()
        """Event that is triggered when the shard has identified and connected to the gateway."""
        self.raw_dispatcher: Dispatcher = Dispatcher()
        """A dispatcher for raw websocket events."""
        self.event_dispatcher: Dispatcher = Dispatcher()
        """A dispatcher for DISPATCH events."""

        # Internal vars
        self._ws: ClientWebSocketResponse | None = None
        self._connected: Event = Event()
        self._http_client: HTTPClient = http_client
        # We allocate 3 spots for heartbeats. 2 for normal operations and one spare incase discord requests it.
        self._send_ratelimit = TimesPer(120 - 3, 60)
        self._library_name: str = library_name
        self._decompressor = Decompressor()
        self._logger = getLogger(f"nextcore.gateway.shard.{self.id}")
        self._has_acknowledged_heartbeat = True
        # Resuming info
        self._last_sequence: int | None = None
        self._session_id: str | None = None

        # Listener registration
        self.raw_dispatcher.add_listener(self._handle_hello, 10)
        self.raw_dispatcher.add_listener(self._handle_dispatch, 0)
        self.raw_dispatcher.add_listener(self._handle_reconnect, 7)

    async def connect(self) -> None:
        """Connects to discord's gateway.

        .. warning::
            The caller has to handle max_concurrency and similar things.
        """
        if self._ws is not None and not self._ws.closed:
            # Sessions will be invalidated if we disconnect with a 1000 status code (the default)
            await self._ws.close(code=999)
        if self._ws is None or self._ws.closed:
            # Here we are still allowing connected websockets to
            self._ws = await self._http_client.ws_connect(self.GATEWAY_URL)
        # Zlib shares state across messages, so we need to reset it.
        self._decompressor = Decompressor()

        if self._last_sequence is not None and self._session_id is not None:
            # TODO: Reconnect
            raise NotImplementedError("Reconnecting is not implemented yet")
        else:
            await self.identify()
        create_task(self._receive_loop(), name=f"nextcore:Shard {self.id}/{self.shard_count} receive loop")

    async def _send(
        self, data: ClientGatewayPayload, *, respect_ratelimit: bool = True, wait_until_identify: bool = True
    ) -> None:
        """Sends raw data to discord.

        Parameters
        ----------
        data: :class:`nextcore.gateway.outer.ClientGatewayPayload`
            The data to send.
        respect_ratelimit: bool
            .. warning::
                Invalid usage of this can lead to frequent disconnects and potentially your library being banned from discord.
            Whether to respect the ratelimit. This is useful as heartbeats have reserved 3 spots in the ratelimit.
        wait_until_identify: bool
            Whether to wait until the shard has identified and connected to the gateway.
        """
        # Most methods should never be called before identify as this will cause a disconnect.
        if wait_until_identify:
            await self.ready.wait()

        # Heartbeats has reserved 3 spots in the ratelimit, so they should not be counted towards the common pool.
        if respect_ratelimit:
            await self._send_ratelimit.wait()
        # Just a quick safety check to make sure we're connected.
        assert self._ws is not None, "Shard is not connected"
        assert not self._ws.closed, "Shard is not connected"

        self._logger.debug("Sending %s", data)
        await self._ws.send_json(data)

    async def _receive_loop(self) -> None:
        """Receives data from discord.
        This calls :meth:`Shard._on_receive` for every message received.
        """
        assert self._ws is not None, "Shard is not connected to a websocket connection"
        async for message in self._ws:
            # Seems like type is unknown? Maybe create a issue in aiohttp?
            message_type: WSMsgType = message.type  # type: ignore
            if message_type == WSMsgType.BINARY:
                data: bytes = message.data  # type: ignore
                await self._on_receive(data)
        close_code = self._ws.close_code
        self._logger.debug("Websocket connection was closed. Code: %s", close_code)

    async def _on_receive(self, uncompressed_data: bytes) -> None:
        """Callback for when data is received from discord."""
        try:
            raw_data = self._decompressor.decompress(uncompressed_data)
            if raw_data is None:
                # Partial message, wait for more data.
                return
        except ValueError:
            # Data is corrupt, we have to void all context.
            await self.connect()
            return

        decoded_data = raw_data.decode("utf-8")
        self._logger.debug("Received %s", decoded_data)

        data = json_loads(decoded_data)
        # As we are dispatching this it can't be mutable as it would cause modifying listeners to modify for all listeners.
        # Type ignore is here as frozendict is technically not a subclass of dict, meaning TypedDict does not support it.
        frozen_data: ServerGatewayPayload = frozendict(data)  # type: ignore
        del data
        self.raw_dispatcher.dispatch(frozen_data["op"], frozen_data)

        if "t" in frozen_data:
            # This is a dispatch event.
            # FrozenDict implements everything dict does so this should be fine.
            data: ServerGatewayDispatchPayload = frozen_data  # type: ignore
            self.event_dispatcher.dispatch(data["t"], frozen_data)

    async def _on_close(self, close_code: int) -> None:
        """Callback for when the websocket connection is closed.

        .. note::
            This will not include the client closing the websocket connection.

        Parameters
        ----------
        close_code: :class:`int`
            The close code of the websocket connection.
        """

    async def _heartbeat_loop(self, interval: float) -> None:
        """Sends heartbeats to discord.

        .. note::
            The caller should implement jitter

        Parameters
        ----------
        interval: :class:`float`
            The interval to send heartbeats at.
        """
        # We create our own variable here to avoid a weird bug where the loop would run twice.
        # This is due to self._ws being a new non-closed instance before the while loop check kicks in.
        # The fix for this is just to create a new reference to the ws that is running right now
        ws = self._ws
        assert ws is not None, "Shard is not connected"
        while ws is not None and not ws.closed:
            payload: ClientGatewayPayload = {"op": 1, "d": self._last_sequence}
            await self._send(payload, respect_ratelimit=False, wait_until_identify=False)
            await sleep(interval)

    async def close(self) -> None:
        """Reset the internal state and disconnect from discord."""
        if self._ws is not None:
            await self._ws.close()
            self._ws = None
        # Zlib shares state across messages, so we need to reset it.
        self._decompressor = Decompressor()

    # Default responses
    async def _handle_hello(self, data: ServerGatewayPayload) -> None:
        if TYPE_CHECKING:
            # Here we cast to a new variable due to a possible MyPY bug? I have not created a issue yet.
            inner = cast(HelloData, data["d"])
        else:
            # Some type hinters might warn about unused code here, however that is a bug
            inner = data["d"]
        heartbeat_interval = inner["heartbeat_interval"] / 1000  # Interval is in milliseconds
        jitter = random()

        self._logger.debug("Starting heartbeating with interval %s and jitter %s", heartbeat_interval, jitter)
        await sleep(heartbeat_interval * jitter)  # Discord wants us to wait a random time.
        create_task(
            self._heartbeat_loop(heartbeat_interval), name=f"nextcore:Shard {self.id}/{self.shard_count} heartbeat loop"
        )

    async def _handle_dispatch(self, data: ServerGatewayDispatchPayload) -> None:
        """Handles a dispatch event.

        Parameters
        ----------
        data: :class:`nextcore.gateway.outer.ServerGatewayDispatchPayload`
            The event data.
        """
        self._logger.debug("Updated dispatch sequence to %s", data["s"])
        self._last_sequence = data["s"]

    async def _handle_ready(self, data: ServerGatewayDispatchPayload) -> None:
        """Handles a hello event.

        Parameters
        ----------
        data: :class:`nextcore.gateway.outer.ServerGatewayDispatchPayload`
            The event data.
        """
        if TYPE_CHECKING:
            # Here we cast to a new variable due to a possible MyPY bug? I have not created a issue yet.
            inner = cast(ReadyData, data["d"])
        else:
            # Some type hinters might warn about unused code here, however that is a bug
            inner = data["d"]

        self._session_id = inner["session_id"]

    async def _handle_reconnect(self, data: ServerGatewayPayload) -> None:
        """Handles a reconnect request event.

        Parameters
        ----------
        data: :class:`nextcore.gateway.outer.ServerGatewayPayload`
            The event data.
        """
        self._logger.debug("Discord requested a reconnect")
        await self.connect()

    # Helper functions
    async def identify(self) -> None:
        """Identifies the shard to discord.

        .. warning::
            This is automatically called when running :meth:`Shard.connect`. Running this multiple times will cause a disconnect.
        """
        payload: ClientGatewayPayload = {
            "op": 2,
            "d": {
                "token": self.token,
                "intents": self.intents,
                "compress": True,
                "properties": {
                    "$os": platform,
                    "$browser": self._library_name,
                    "$device": self._library_name,
                },
            },
        }

        # Presence can't be None, only pass it if set.
        if self.default_presence is not None:
            payload["d"]["presence"] = self.default_presence

        await self._send(payload, wait_until_identify=False)

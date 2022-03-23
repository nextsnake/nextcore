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

from asyncio import Event, get_running_loop, sleep
from logging import Logger, getLogger
from random import random
from sys import platform
from typing import TYPE_CHECKING

from aiohttp import ClientConnectorError, ClientWebSocketResponse, WSMsgType
from frozendict import frozendict

from ..common.dispatcher import Dispatcher
from ..utils import json_dumps, json_loads
from .close_code import GatewayCloseCode
from .decompressor import Decompressor
from .errors import (
    DisallowedIntentsError,
    DisconnectError,
    InvalidApiVersionError,
    InvalidIntentsError,
    InvalidShardCountError,
    InvalidTokenError,
    ReconnectCheckFailedError,
    UnhandledCloseCodeError,
)
from .exponential_backoff import ExponentialBackoff
from .opcodes import GatewayOpcode
from .times_per import TimesPer

if TYPE_CHECKING:
    from typing import Final, cast

    from nextcore.typings.gateway.inner.dispatch.ready import ReadyData
    from nextcore.typings.gateway.inner.hello import HelloData
    from nextcore.typings.gateway.outer import (
        ClientGatewayPayload,
        ServerGatewayDispatchPayload,
        ServerGatewayPayload,
    )
    from nextcore.typings.objects.update_presence import UpdatePresence

    from ..http import HTTPClient

__all__ = ("Shard",)


class Shard:
    """A shard connection to the Discord gateway

    Parameters
    ----------
    shard_id: :class:`int`
        The ID of this shard.
    shard_count: :class:`int`
        How many shards is in this shard set. Used for splitting events on Discord's side.
    intents: :class:`int`
        The intents to connect with.
    token: :class:`str`
        The bot's token to connect with.
    identify_ratelimiter: :class:`TimesPer`
        The ratelimiter for IDENTIFYing the bot.
    http_client: :class:`HTTPClient<nextcore.http.HTTPClient>`
        HTTP client used to connect to Discord's gateway.
    presence: :class:`UpdatePresence`
        The initial presence info to send when connecting.
    large_threshold: :class:`int`
        A value between 50 and 250 that determines how many members a guild needs for the gateway to stop sending offline members in the guild member list.
    library_name: :class:`str`
        The name of the library that is using this gateway. This should be set if you are making your own library on top of nextcore.

    Attributes
    ----------
    shard_id: :class:`int`
        The ID of this shard.
    shard_count: :class:`int`
        How many shards are in this shard set. Used for splitting events on Discord's side.
    intents: :class:`int`
        The intents to connect with.
    token: :class:`str`
        The bot's token to connect with. If this is changed, the session will be invalidated.
    presence: :class:`UpdatePresence`
        The initial presence info to send when connecting.
    large_threshold: :class:`int`
        A value between 50 and 250 that determines how many members a guild needs for the gateway to stop sending offline members in the guild member list.
    library_name: :class:`str`
        The name of the library that is using this gateway. This should be set if you are making your own library on top of nextcore.
    ready: :class:`asyncio.Event`
        Fires when the gateway has connected and received the READY event.
    raw_dispatcher: :class:`Dispatcher<nextcore.common.Dispatcher>`
        A dispatcher with raw payloads sent by discord. The event name is the opcode, and the value is the raw data.
    event_dispatcher: :class:`Dispatcher<nextcore.common.Dispatcher>`
        A dispatcher for DISPATCH events sent by discord. The event name is the event name, and the value is the inner payload.
    dispatcher: :class:`Dispatcher<nextcore.common.Dispatcher>`
        A dispatcher for internal events.
    session_id: :class:`str`
        The ID of the current session.
    session_sequence_number: :class:`int`
        The last sequence number of the current session.
    should_reconnect: :class:`bool`
        Whether the gateway should reconnect or not.
    """

    __slots__ = (
        "shard_id",
        "shard_count",
        "intents",
        "token",
        "http_client",
        "presence",
        "large_threshold",
        "library_name",
        "ready",
        "raw_dispatcher",
        "event_dispatcher",
        "dispatcher",
        "session_id",
        "session_sequence_number",
        "should_reconnect",
        "_identify_ratelimiter",
        "_send_ratelimit",
        "_ws",
        "_decompressor",
        "_logger",
        "_received_heartbeat_ack",
    )
    GATEWAY_URL: Final[str] = "wss://gateway.discord.gg?v=10&compress=zlib-stream"
    """The gateway URL to connect to"""

    def __init__(
        self,
        shard_id: int,
        shard_count: int,
        intents: int,
        token: str,
        identify_ratelimiter: TimesPer,
        http_client: HTTPClient,
        *,
        presence: UpdatePresence | None = None,
        large_threshold: int | None = None,
        library_name: str = "nextcore",
    ) -> None:
        # User's params
        self.shard_id: Final[int] = shard_id
        self.shard_count: Final[int] = shard_count
        self.intents: int = intents
        self.token: str = token
        self.http_client: HTTPClient = http_client  # TODO: Should this be private?
        self.presence: UpdatePresence | None = presence
        self.large_threshold: int | None = large_threshold
        self.library_name: str = library_name

        # Publics
        self.ready: Event = Event()
        self.raw_dispatcher: Dispatcher = Dispatcher()
        self.event_dispatcher: Dispatcher = Dispatcher()
        self.dispatcher: Dispatcher = Dispatcher()

        # Session related
        self.session_id: str | None = None
        self.session_sequence_number: int | None = None
        self.should_reconnect: bool = True  # This should be set by the user.

        # User's internals
        # Should generally only be set once
        self._identify_ratelimiter: TimesPer = identify_ratelimiter

        # Internals
        self._send_ratelimit = TimesPer(60 - 3, 120)
        self._ws: ClientWebSocketResponse | None = None
        self._decompressor: Decompressor = Decompressor()
        self._logger: Logger = getLogger(f"nextcore.gateway.shard.{self.shard_id}")
        self._received_heartbeat_ack: bool = True

        # Register handlers
        # Raw
        self.raw_dispatcher.add_listener(self._handle_hello, GatewayOpcode.HELLO)
        self.raw_dispatcher.add_listener(self._handle_heartbeat_ack, GatewayOpcode.HEARTBEAT_ACK)
        self.raw_dispatcher.add_listener(self._handle_dispatch, GatewayOpcode.DISPATCH)
        self.raw_dispatcher.add_listener(self._handle_invalid_session, GatewayOpcode.INVALID_SESSION)
        self.raw_dispatcher.add_listener(self._handle_reconnect, GatewayOpcode.RECONNECT)

        # Events
        self.event_dispatcher.add_listener(self._handle_ready, "READY")

        # Disconnects
        self.dispatcher.add_listener(self._handle_disconnect, "disconnect")

    async def connect(self) -> None:
        """Connect to the gateway.

        This will automatically RESUME if a session is set.
        """
        # Clear state
        self._decompressor = Decompressor()
        self._received_heartbeat_ack = True

        # Connect to gateway
        if self._ws is not None and not self._ws.closed:
            # This is to keep the session alive.
            await self._ws.close(code=999)

        # Retry connection
        async for _ in ExponentialBackoff(0.5, 2, 10):
            try:
                self._ws = await self.http_client.ws_connect(Shard.GATEWAY_URL)
                break
            except ClientConnectorError:
                self._logger.error("Failed to connect to gateway? Check your internet connection.")

        if self.session_id is None and self.session_sequence_number is None:
            if not self.should_reconnect:
                raise ReconnectCheckFailedError
            # No session stored, create a new one.
            await self._identify_ratelimiter.wait()
            await self.identify()
        else:
            # Session stored, resume it.
            # Resumes don't use up the IDENTIFY ratelimit so we should prefer using it.
            await self.resume()

            # Discord does not provide a "session resume ok" event, they only do it after resuming every event which can take a long time.
            # We really have to hope that discord does not consume multiple events at once.
            self.ready.set()

        loop = get_running_loop()
        loop.create_task(self._receive_loop())

    async def _send(
        self, data: ClientGatewayPayload, *, respect_ratelimit: bool = True, wait_until_ready: bool = True
    ) -> None:
        if wait_until_ready:
            self._logger.debug("Waiting until ready")
            await self.ready.wait()
        if respect_ratelimit:
            # This pretty much only used for heartbeat as we allocate 3 spots in the ratelimit for it.
            # This is made as we have to heartbeat to avoid a disconnect.
            # This has a few downsides though. If discord changes the heartbeat interval or spams request heartbeats we would be instantly disconnected.
            await self._send_ratelimit.wait()
        assert self._ws is not None, "Websocket is not connected"
        assert self._ws.closed is False, "Websocket is closed"

        # We are formatting data outside to provide a JSON string to the logger. TODO: Possibly change this?
        formatted_data = json_dumps(data)
        self._logger.debug("Sent: %s", formatted_data)

        await self._ws.send_str(formatted_data)

    # Loops
    async def _receive_loop(self) -> None:
        assert self._ws is not None, "Websocket is not connected"
        assert not self._ws.closed, "Websocket is closed"

        # Here we create our own reference to the current websocket as we override self._ws on reconnect so there may be a chance that it gets overriden before the loop exists
        # This prevents multiple receive loops from running at the same time.
        ws = self._ws

        async for message in ws:
            # Aiohttp is not typing this? This should probably be fixed in aiohttp?
            message_type: WSMsgType = message.type  # type: ignore [reportUnknownMemberType]
            if message_type is WSMsgType.BINARY:
                # Same issue as above here.
                message_data: bytes = message.data  # type: ignore [reportUnknownMemberType]
                await self._on_raw_receive(message_data)

        # Generally having the exit condition outside is more consistent that having it inside.
        self._logger.debug("Disconnected!")
        await self._on_disconnect(ws)

    async def _heartbeat_loop(self, heartbeat_interval: float) -> None:
        assert self._ws is not None, "_ws is not set?"
        assert not self._ws.closed, "Websocket is closed"

        # Here we create our own reference to the current websocket as we override self._ws on reconnect so there may be a chance that it gets overriden before the loop exists
        # This prevents multiple heartbeat loops from running at the same time.
        ws = self._ws

        while not ws.closed:
            payload: ClientGatewayPayload = {
                "op": GatewayOpcode.HEARTBEAT.value,
                "d": self.session_sequence_number,
            }

            # Handle dead connecton checking
            # self._received_heartbeat_ack is set in self._handle_heartbeat_ack
            if not self._received_heartbeat_ack:
                # We have not received a heartbeat ack. This is usually a sign of a dead connection.
                # Just reconnect and hope that our session is still valid.
                self._logger.debug("Disconnecting due to lack of heartbeats!")
                return await self.connect()
            self._received_heartbeat_ack = False

            # Send the heartbeat
            await self._send(payload, respect_ratelimit=False, wait_until_ready=False)
            await sleep(heartbeat_interval)

    # Loop callbacks
    # These should be prefixed by on_ to avoid confusiuon with handlers
    async def _on_raw_receive(self, compressed_data: bytes) -> None:
        try:
            raw_data = self._decompressor.decompress(compressed_data)
        except ValueError as e:
            # Data is corrupted. Zlib requires context which we now do not have, so no future messages would be understood.
            # The best bet we have is to reconnect.
            self._logger.error("Failed to decompress message", exc_info=e)
            await self.connect()
            return
        if raw_data is None:
            # Partial data received. We should try to receive more.
            # Pretty sure this is un-used by discord however it is here just in case.
            self._logger.debug("Received partial data, waiting for more")
            return

        decoded_data = raw_data.decode("utf-8")
        self._logger.debug("Received %s", decoded_data)

        data = json_loads(decoded_data)
        # We are going to trust discord to provide us with the correct data here.
        # If it doesn't we have bigger issues
        frozen_data: ServerGatewayPayload = frozendict(data)  # type: ignore [assignment]

        # Processing of the payload
        opcode = frozen_data["op"]

        self.raw_dispatcher.dispatch(opcode, frozen_data)

        if opcode == GatewayOpcode.DISPATCH:
            # Received dispatch
            # We are just trusing discord to provide the correct data here.
            dispatch_data: ServerGatewayDispatchPayload = frozen_data  # type: ignore [assignment]
            self.event_dispatcher.dispatch(dispatch_data["t"], dispatch_data["d"])

    async def _on_disconnect(self, ws: ClientWebSocketResponse) -> None:
        self.ready.clear()

        close_code = ws.close_code
        if ws.close_code is None:
            # This happens when we closed the websocket. Just ignore it as there is basically no info here.
            return

        self._logger.debug("Disconnected with code %s", close_code)

        self.dispatcher.dispatch("disconnect", close_code)

    # Raw handlers
    # These should be prefixed by handle_ to avoid confusiuon with loop callbacks
    async def _handle_hello(self, data: ServerGatewayPayload) -> None:
        # ReadyData only exists while type checking hence the check here.
        # Please note that you may get a warning that the else block is unreachable. This is a bug and you should report it to your linter.
        if TYPE_CHECKING:
            inner = cast(HelloData, data["d"])
        else:
            inner = data["d"]

        heartbeat_interval = inner["heartbeat_interval"] / 1000  # Convert from ms to seconds

        # Discord requires us to wait a random amount up to heartbeat_interval.
        jitter = random()
        initial_heartbeat = heartbeat_interval * jitter

        self._logger.debug(
            "Starting heartbeat with interval %s with initial heartbeat %s", heartbeat_interval, initial_heartbeat
        )
        await sleep(initial_heartbeat)

        loop = get_running_loop()
        loop.create_task(self._heartbeat_loop(heartbeat_interval))

    async def _handle_heartbeat_ack(self, data: ServerGatewayPayload) -> None:
        del data  # Unused
        self._received_heartbeat_ack = True

    async def _handle_reconnect(self, data: ServerGatewayPayload) -> None:
        del data  # Unused
        self._logger.debug("Reconnecting due to gateway going away")
        await self.connect()

    async def _handle_invalid_session(self, data: ServerGatewayPayload) -> None:
        del data  # Unused
        self._logger.debug("Invalid session! Creating a new one")

        self.session_id = None
        self.session_sequence_number = None

        if self.should_reconnect:
            assert self._ws is not None, "_ws is not set?"
            if self._ws.closed:
                self._ws = await self.http_client.ws_connect(Shard.GATEWAY_URL)

            # Discord expects us to wait for up to 5s before resuming?
            jitter = random()
            resume_after = 5 * jitter
            self._logger.debug("Resuming after %s seconds", resume_after)
            await sleep(resume_after)

            await self.identify()

    async def _handle_dispatch(self, data: ServerGatewayDispatchPayload) -> None:
        # Save sequence number for reconnection
        self.session_sequence_number = data["s"]

    async def _handle_ready(self, data: ReadyData) -> None:
        # Save session id for resuming
        self.session_id = data["session_id"]
        self.ready.set()

    async def _handle_disconnect(self, close_code: int) -> None:
        if close_code < 2000:
            self._logger.info("Received close code in 1xxx range, reconnecting. This is usually due to network issues.")
            await self.connect()
        elif close_code == GatewayCloseCode.UNKNOWN_ERROR:
            # Unknown error, best we can do is just reconnect.
            self._logger.info("Recieved unknown error reconnect, reconnecting.")
            await self.connect()
        elif close_code == GatewayCloseCode.UNKNOWN_OPCODE:
            # This is probably a library fault!
            self._logger.error(
                "Sent unknown opcode, this is probably a library issue! Please make a issue on https://github.com/nextsnake/nextcore/issues"
            )
            await self.connect()  # Yes this can lead to a infinite loop. Not much we can do about it.
        elif close_code == GatewayCloseCode.DECODE_ERROR:
            # This is probably a library fault!
            self._logger.error(
                "Sent invalid data, this is probably a library issue! Please make a issue on https://github.com/nextsnake/nextcore/issues"
            )
            await self.connect()  # Yes this can lead to a infinite loop. Not much we can do about it.
        elif close_code == GatewayCloseCode.NOT_AUTHENTICATED:
            # This is probably a library fault!
            self._logger.error(
                "Sent a payload before authenticating. This is probably a library issue! Please make a issue on https://github.com/nextsnake/nextcore/issues"
            )
            await self.connect()  # Yes this can lead to a infinite loop. Not much we can do about it.
        elif close_code == GatewayCloseCode.ALREADY_AUTHENTICATED:
            # This is probably a library fault!
            self._logger.error(
                "Sent IDENTIFY/RESUME payload more than once. This is probably a library issue! Please make a issue on https://github.com/nextsnake/nextcore/issues"
            )
            await self.connect()  # Yes this can lead to a infinite loop. Not much we can do about it.
        elif close_code == GatewayCloseCode.INVALID_SEQUENCE:
            # Session data is broken? Let's just reconnect and hope for the best.
            self._logger.info("Sent a invalid sequence number while resuming, let's clear the session and try again.")

            # Clear session
            self.session_sequence_number = None
            self.session_id = None

            # Reconnect
            await self.connect()
        elif close_code == GatewayCloseCode.RATE_LIMITED:
            self._logger.error(
                "Sent too many messages to the gateway. This is probably a library issue! Please make a issue on https://github.com/nextsnake/nextcore/issues"
            )
            await self.connect()  # Yes this can lead to a infinite loop. Not much we can do about it.
        elif close_code == GatewayCloseCode.SESSION_TIMEOUT:
            self._logger.info("Session timed out, reconnecting without one.")

            # Clear session
            self.session_sequence_number = None
            self.session_id = None

            # Reconnect
            await self.connect()
        elif close_code == GatewayCloseCode.INVALID_SHARD:
            self.dispatcher.dispatch("critical", InvalidShardCountError())
        elif close_code == GatewayCloseCode.SHARDING_REQUIRED:
            self._logger.critical(
                "Received sharding required while sharding? Please make a issue on https://github.com/nextsnake/nextcore/issues"
            )
            # TODO: Should this be merged into the else block?
            self.dispatcher.dispatch("critical", UnhandledCloseCodeError(close_code))
        elif close_code == GatewayCloseCode.INVALID_API_VERSION:
            self._logger.critical("Received invalid api version. Please update nextcore!")
            self.dispatcher.dispatch("critical", InvalidApiVersionError())
        elif close_code == GatewayCloseCode.INVALID_INTENTS:
            self._logger.critical("Sent invalid intents. This should never happen!")
            self.dispatcher.dispatch("critical", InvalidIntentsError())
        elif close_code == GatewayCloseCode.DISALLOWED_INTENTS:
            self._logger.critical("Sent disallowed intents. This should be enabled in the settings.")
            self.dispatcher.dispatch("critical", DisallowedIntentsError())
        else:
            self.dispatcher.dispatch("critical", UnhandledCloseCodeError(close_code))
            raise RuntimeError(f"Close code not handled: {close_code}")

    # Send wrappers
    async def identify(self) -> None:
        """Identify to the gateway.

        .. note::
            See the `documentation <https://discord.dev/topics/gateway#identify>`__
        """
        payload: ClientGatewayPayload = {
            "op": GatewayOpcode.IDENTIFY.value,
            "d": {
                "token": self.token,
                "intents": self.intents,
                "properties": {
                    "$os": platform,
                    "$browser": self.library_name,
                    "$device": self.library_name,
                },
                "compress": True,
                "shard": [self.shard_id, self.shard_count],
            },
        }
        # Not required parameters can't be set to anything for
        if self.large_threshold is not None:
            payload["d"]["large_thereshold"] = self.large_threshold
        if self.presence is not None:
            payload["d"]["presence"] = self.presence

        await self._send(payload, wait_until_ready=False)

    async def resume(self) -> None:
        """Resume the session

        .. note::
            See the `documentation <https://discord.dev/topics/gateway#resume>`__
        """
        if self.session_id is None or self.session_sequence_number is None:
            raise ValueError("Session id or sequence number is not set")

        payload: ClientGatewayPayload = {
            "op": GatewayOpcode.RESUME.value,
            "d": {
                "token": self.token,
                "session_id": self.session_id,
                "seq": self.session_sequence_number,
            },
        }
        await self._send(payload, wait_until_ready=False)

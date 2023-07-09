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

import asyncio
from asyncio import (
    FIRST_COMPLETED,
    Event,
    Lock,
    create_task,
    get_running_loop,
    sleep,
    wait,
)
from logging import Logger, getLogger
from math import ceil
from random import random
from sys import platform
from time import time
from typing import TYPE_CHECKING, cast, overload

from aiohttp import (
    ClientConnectorError,
    ClientWebSocketResponse,
    WSMsgType,
    WSServerHandshakeError,
)
from frozendict import frozendict

from ..common import (
    UNDEFINED,
    Dispatcher,
    TimesPer,
    UndefinedType,
    json_dumps,
    json_loads,
)
from .close_code import GatewayCloseCode
from .decompressor import Decompressor
from .errors import (
    DisallowedIntentsError,
    DisconnectError,
    InvalidApiVersionError,
    InvalidIntentsError,
    InvalidShardCountError,
    ReconnectCheckFailedError,
    UnhandledCloseCodeError,
)
from .exponential_backoff import ExponentialBackoff
from .op_code import GatewayOpcode

if TYPE_CHECKING:
    from typing import Any, Final, Literal

    from discord_typings import (
        DispatchEvent,
        GatewayEvent,
        HeartbeatCommand,
        HelloEvent,
        IdentifyCommand,
        InvalidSessionEvent,
        ReconnectEvent,
        RequestGuildMembersCommand,
        ResumeCommand,
        UpdatePresenceCommand,
        UpdatePresenceData,
        UpdateVoiceStateCommand,
        UpdateVoiceStateData,
    )
    from discord_typings.gateway import ReadyData, UpdatePresenceData

    from ..http import HTTPClient

__all__: Final[tuple[str, ...]] = ("Shard",)


class Shard:
    """A shard connection to the Discord gateway

    Parameters
    ----------
    shard_id:
        The ID of this shard.
    shard_count:
        How many shards is in this shard set. Used for splitting events on Discord's side.
    intents:
        The intents to connect with.
    token:
        The bot's token to connect with.
    identify_rate_limiter:
        The rate limiter for IDENTIFYing the bot.
    http_client:
        HTTP client used to connect to Discord's gateway.
    presence:
        The initial presence info to send when connecting.
    large_threshold:
        A value between 50 and 250 that determines how many members a guild needs for the gateway to stop sending offline members in the guild member list.
    library_name:
        The name of the library that is using this gateway. This should be set if you are making your own library on top of nextcore.

    Attributes
    ----------
    shard_id:
        The ID of this shard.
    shard_count:
        How many shards are in this shard set. Used for splitting events on Discord's side.
    intents:
        The intents to connect with.
    token:
        The bot's token to connect with. If this is changed, the session will be invalidated.
    presence:
        The initial presence info to send when connecting.
    large_threshold:
        A value between 50 and 250 that determines how many members a guild needs for the gateway to stop sending offline members in the guild member list.
    library_name:
        The name of the library that is using this gateway. This should be set if you are making your own library on top of nextcore.
    connected:
        When this shard is connected to the gateway, but not identified yet.

        This also requires the gateway to send the `HELLO <https://discord.dev/topics/gateway-events#hello>` event, as rate-limiters are not setup yet.
    ready:
        Fires when the gateway has connected and received the READY event.
    raw_dispatcher:
        A dispatcher with raw payloads sent by discord. The event name is the opcode, and the value is the raw data.
    event_dispatcher:
        A dispatcher for DISPATCH events sent by discord. The event name is the event name, and the value is the inner payload.
    dispatcher:
        A dispatcher for internal events.
    session_id:
        The ID of the current session.
    session_sequence_number:
        The last sequence number of the current session.
    should_reconnect:
        Whether the gateway should reconnect or not.
    """

    __slots__ = (
        "shard_id",
        "shard_count",
        "intents",
        "token",
        "presence",
        "large_threshold",
        "library_name",
        "connected",
        "ready",
        "raw_dispatcher",
        "event_dispatcher",
        "dispatcher",
        "session_id",
        "session_sequence_number",
        "should_reconnect",
        "_identify_rate_limiter",
        "_send_rate_limit",
        "_connect_lock",
        "_ws",
        "_decompressor",
        "_logger",
        "_received_heartbeat_ack",
        "_http_client",
        "_heartbeat_sent_at",
        "_latency",
    )
    _GATEWAY_SEND_RATE_LIMITS: tuple[int, int] = (120, 60)  # Times, per

    def __init__(
        self,
        shard_id: int,
        shard_count: int,
        intents: int,
        token: str,
        identify_rate_limiter: TimesPer,
        http_client: HTTPClient,
        *,
        presence: UpdatePresenceData | None = None,
        large_threshold: int | None = None,
        library_name: str = "nextcore",
    ) -> None:
        # User's params
        self.shard_id: Final[int] = shard_id
        self.shard_count: Final[int] = shard_count
        self.intents: int = intents
        self.token: str = token
        self.presence: UpdatePresenceData | None = presence
        self.large_threshold: int | None = large_threshold
        self.library_name: str = library_name

        # Publics
        self.connected: Event = Event()
        self.ready: Event = Event()
        self.raw_dispatcher: Dispatcher[int] = Dispatcher()
        self.event_dispatcher: Dispatcher[str] = Dispatcher()
        self.dispatcher: Dispatcher[Literal["disconnect", "sent", "critical", "client_disconnect"]] = Dispatcher()

        # Session related
        self.session_id: str | None = None
        self.session_sequence_number: int | None = None
        self.should_reconnect: bool = True  # This should be set by the user.

        # User's internals
        # Should generally only be set once
        self._identify_rate_limiter: TimesPer = identify_rate_limiter

        # Internals
        self._send_rate_limit: TimesPer | None = None
        self._connect_lock: Lock = Lock()
        self._ws: ClientWebSocketResponse | None = None
        self._decompressor: Decompressor = Decompressor()
        self._logger: Logger = getLogger(f"{__name__}.{self.shard_id}")
        self._received_heartbeat_ack: bool = True
        self._http_client: HTTPClient = http_client  # TODO: Should this be private?

        # Latency
        self._heartbeat_sent_at: float | None = None
        self._latency: float | None = None  # Not public as we use a property that errors when not connected

        # Register the listeners
        self._register_event_listeners()

    def _register_event_listeners(self) -> None:
        # Raw
        self.raw_dispatcher.add_listener(self._handle_hello, GatewayOpcode.HELLO)
        self.raw_dispatcher.add_listener(self._handle_heartbeat_ack, GatewayOpcode.HEARTBEAT_ACK)
        self.raw_dispatcher.add_listener(self._handle_dispatch, GatewayOpcode.DISPATCH)
        self.raw_dispatcher.add_listener(self._handle_invalid_session, GatewayOpcode.INVALID_SESSION)
        self.raw_dispatcher.add_listener(self._handle_reconnect, GatewayOpcode.RECONNECT)

        # Events
        self.event_dispatcher.add_listener(self._handle_ready, "READY")
        self.event_dispatcher.add_listener(self._handle_resumed, "RESUMED")

        # Custom
        self.dispatcher.add_listener(self._handle_disconnect, "disconnect")

    async def connect(self) -> None:
        """Connect to the gateway

        .. note::
            This will try to automatically resume if a session is set.
        .. warning::
            This might not have fully completed at the end of this call as re-connects will be done in the background.

        Raises
        ------
        ReconnectCheckFailedError
            :attr:`Shard.should_reconnect` was set to :data:`False` and a :meth:`Shard.identify` call was needed.
        RuntimeError
            We are already reconnecting.
        """
        if self._connect_lock.locked():
            raise RuntimeError("We are already reconnecting.")

        async with self._connect_lock:
            ws = await self._connect_to_gateway()

            self._logger.debug("Connected to websocket")

            # Disconnect previously connected ws
            await self.close(cleanup=False)

            # Reset session
            self._decompressor = Decompressor()
            self._received_heartbeat_ack = True
            self._ws = ws  # Use the new connection

            create_task(self._receive_loop())

            # Connection logic is continued in _handle_hello to account for that rate limits are defined there.

            try:
                await asyncio.wait_for(self.connected.wait(), timeout=10)
            except asyncio.TimeoutError:
                self._logger.warning("Timeout waiting for HELLO. Reconnecting!")

                # A task is used here because of the connect lock.
                # TODO: This can probably be done in a cleaner way?
                asyncio.create_task(self.connect())

    async def _connect_to_gateway(self) -> ClientWebSocketResponse:
        async for _ in ExponentialBackoff(0.5, 2, 10):
            try:
                ws = await self._http_client.connect_to_gateway(version=10, encoding="json", compress="zlib-stream")
            except ClientConnectorError:
                self._logger.exception("Failed to connect to the gateway? Check your internet connection")
            except WSServerHandshakeError:
                self._logger.exception("Failed to connect to the gateway")
            else:
                break
        # TODO: This is a type hinting issue with ExponentialBackoff. For generators are always potentially limited in terms of type hinting
        # So it assumes it can end early which isnt the case here.
        return ws  # type: ignore [reportUnboundVariable]

    @classmethod
    def _calculate_heartbeat_rate_limit_spots(cls, heartbeat_interval: float) -> int:
        return ceil(heartbeat_interval / 60)  # 60 here being how often the send rate limit resets

    async def close(self, *, cleanup: bool = True) -> None:
        """Close the connection to the gateway and destroy the session.

        .. note::
            This will dispatch a ``client_disconnect`` event.

        Parameters
        ----------
        cleanup:
            Whether to close the Discord session.
            This will stop you from being able to resume, but also remove the bots status faster.
        """
        if self._ws is not None:
            if cleanup:
                await self.dispatcher.dispatch("client_disconnect", True)
                await self._ws.close()  # Disconnecting with a 1000 close code deletes the session.
            else:
                await self.dispatcher.dispatch("client_disconnect", False)
                await self._ws.close(code=999)
        self._ws = None  # Clear it to save some ram
        self._send_rate_limit = None  # No longer applies
        self.connected.clear()

    @property
    def latency(self) -> float:
        """Time in seconds between a heartbeat being sent and discord acknowledging it.

        Raises
        ------
        :exc:`RuntimeError`
            Not connected to the gateway.
        :exc:`RuntimeError`
            Not heartbeated yet.
        """
        if self._ws is None or self._ws.closed:
            raise RuntimeError("Not connected to the gateway.")
        if self._latency is None:
            raise RuntimeError("Not heartbeated yet.")
        return self._latency

    async def _send(
        self, data: Any, wait_until_ready: bool = True
    ) -> None:  # TODO: A command union is not implemented in discord_typings yet.
        if wait_until_ready:
            self._logger.debug("Waiting until ready")
            await self.ready.wait()
        assert (
            self._send_rate_limit is not None
        ), "Send rate limit was not set yet. Probably due to not receiving HELLO yet."
        async with self._send_rate_limit.acquire():
            # These are inside the rate limit block in case it disconnects while waiting for the rate limit
            # TODO: This should re-wait for the shard to connect.
            assert self._ws is not None, "Websocket is not connected"
            assert self._ws.closed is False, "Websocket is closed"

            await self._ws.send_json(data, dumps=json_dumps)

        self._logger.debug("Sent: %s", data)
        await self.dispatcher.dispatch("sent", data)

    # Loops
    async def _receive_loop(self) -> None:
        assert self._ws is not None, "Websocket is not connected"
        assert not self._ws.closed, "Websocket is closed"

        # Here we create our own reference to the current websocket as we override self._ws on reconnect so there may be a chance that it gets overriden before the loop exists
        # This prevents multiple receive loops from running at the same time.
        ws = self._ws

        async for message in ws:
            # Aiohttp is not typing this? This should probably be fixed in aiohttp?
            # The type ignore is because we are accessing a Unknown type (message.type)
            message_type = cast(WSMsgType, message.type)  # pyright: ignore [reportUnknownMemberType]
            if message_type is WSMsgType.BINARY:
                # Same issue as above here.
                message_data = cast(bytes, message.data)  # pyright: ignore [reportUnknownMemberType]
                await self._on_raw_receive(message_data)

        # Generally having the exit condition outside is more consistent that having it inside.
        self._logger.debug("Disconnected!")
        await self._on_disconnect(ws)

    async def _identify_flow(self) -> None:
        # Cleanup session info as they are no longer relevant.
        self.session_id = None
        self.session_sequence_number = None

        if not self.should_reconnect:
            raise ReconnectCheckFailedError()

        try:
            async with self._identify_rate_limiter.acquire():
                # Send a IDENTIFY command, hope it succeeds.
                await self._identify()

                # Tasks
                ready_task = create_task(self.event_dispatcher.wait_for(lambda _: True, "READY"))
                disconnect_task = create_task(self.dispatcher.wait_for(lambda _: True, "disconnect"))

                # Wait for the READY event to get sent or to get disconnected
                done, pending = await wait([ready_task, disconnect_task], return_when=FIRST_COMPLETED, timeout=30)

                # Cancel the ones that wasn't the first
                for task in pending:
                    task.cancel()

                if len(done) == 0:
                    # Both timed out. Try reconnecting on a fresh connection?
                    create_task(self.connect())
                    # TODO: Should we cancel the use of the rate limit here?
                    return

                task = done.pop()  # The task that completed

                if task == ready_task:
                    # Everything good!
                    self.ready.set()
                else:
                    raise DisconnectError()
        except DisconnectError:
            # Disconnects doesn't count towards the rate limit.
            # This is just to error so the rate limit context manager undos our request
            pass

    async def _heartbeat_loop(self, heartbeat_interval: float) -> None:
        assert self._ws is not None, "_ws is not set?"
        assert not self._ws.closed, "Websocket is closed"

        # Here we create our own reference to the current websocket as we override self._ws on reconnect so there may be a chance that it gets overriden before the loop exists
        # This prevents multiple heartbeat loops from running at the same time.
        # This also allows us to bypass the rate limit.
        ws = self._ws

        # Discord requires us to wait a random amount up to heartbeat_interval on the first interval
        jitter = random()
        initial_heartbeat = heartbeat_interval * jitter

        self._logger.debug(
            "Starting heartbeat with interval %s with initial heartbeat %s", heartbeat_interval, initial_heartbeat
        )
        await sleep(initial_heartbeat)

        while not ws.closed:
            payload: HeartbeatCommand = {
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

            # Set the heartbeat time for the latency calculation
            self._heartbeat_sent_at = time()

            # Send the heartbeat
            await ws.send_json(payload, dumps=json_dumps)
            await sleep(heartbeat_interval)

    # Loop callbacks
    # These should be prefixed by on_ to avoid confusiuon with handlers
    async def _on_raw_receive(self, compressed_data: bytes) -> None:
        try:
            raw_data = self._decompressor.decompress(compressed_data)
        except ValueError as e:
            self._logger.error("Failed to decompress message", exc_info=e)

            # Data is corrupted. Zlib requires context which we now do not have, so no future messages would be understood.
            # The best bet we have is to reconnect.
            await self.connect()
            return
        if raw_data is None:
            # Partial data received. We should try to receive more.
            # Pretty sure this is un-used by discord however it is here just in case.
            self._logger.debug("Received partial data, waiting for more")
            return

        # Discord is trusted to send valid payloads here.
        data = json_loads(raw_data.decode("utf-8"))

        self._logger.debug("Received %s", data)

        # We are going to trust discord to provide us with the correct data here.
        # If it doesn't we have bigger issues
        frozen_data: DispatchEvent = frozendict(data)  # type: ignore [assignment]

        # Processing of the payload
        opcode = frozen_data["op"]

        await self.raw_dispatcher.dispatch(opcode, frozen_data)

        # NOTE: .value is not needed here, however pyright seems to complain if it's not here.
        if opcode == GatewayOpcode.DISPATCH.value:
            # Received dispatch
            # We are just trusing discord to provide the correct data here.
            dispatch_data: DispatchEvent = frozen_data
            await self.event_dispatcher.dispatch(dispatch_data["t"], dispatch_data["d"])

    async def _on_disconnect(self, ws: ClientWebSocketResponse) -> None:
        self.connected.clear()
        self.ready.clear()

        close_code = ws.close_code
        if ws.close_code is None:
            # This happens when we closed the websocket. Just ignore it as there is basically no info here.
            return

        self._logger.debug("Disconnected with code %s", close_code)

        await self.dispatcher.dispatch("disconnect", close_code)

    # Raw handlers
    # These should be prefixed by handle_ to avoid confusiuon with loop callbacks
    async def _handle_hello(self, data: HelloEvent) -> None:
        self.connected.set()

        # Start heartbeating
        heartbeat_interval = data["d"]["heartbeat_interval"] / 1000  # Convert from ms to seconds

        loop = get_running_loop()
        loop.create_task(self._heartbeat_loop(heartbeat_interval))

        # Create a rate limiter
        times, per = self._GATEWAY_SEND_RATE_LIMITS

        # Add space for heartbeats
        reserved_for_heartbeats = self._calculate_heartbeat_rate_limit_spots(heartbeat_interval)
        times = times - reserved_for_heartbeats

        self._send_rate_limit = TimesPer(times, per)

        if self.session_id is not None and self.session_sequence_number != 0:
            # Send the resume command
            await self._resume()

            # Manually set the ready flag as Discord does not send a resume acknowledge
            # However it does send a RESUMED event, which is unfortunatly only sent when all events have been repeated.
            # Which can be a very long time.
            self.ready.set()
        else:
            # Need to identify
            # As this is more of a complicated process, i've split it into a seperate function
            await self._identify_flow()  # TODO: Better name?

    async def _handle_heartbeat_ack(self, data: GatewayEvent) -> None:
        del data  # Unused
        self._received_heartbeat_ack = True

        # Update the latency
        assert self._heartbeat_sent_at is not None, "Received heartbeat ack without having sent a heartbeat"
        self._latency = time() - self._heartbeat_sent_at

    async def _handle_reconnect(self, data: ReconnectEvent) -> None:
        del data  # Unused
        self._logger.debug("Reconnecting due to gateway going away")
        await self.connect()

    async def _handle_invalid_session(self, data: InvalidSessionEvent) -> None:
        del data  # Unused
        self._logger.debug("Invalid session! Creating a new one")

        self.session_id = None
        self.session_sequence_number = None

        if self.should_reconnect:
            assert self._ws is not None, "_ws is not set?"
            if self._ws.closed:
                self._ws = await self._http_client.connect_to_gateway(
                    version=10, encoding="json", compress="zlib-stream"
                )

            # Discord expects us to wait for up to 5s before resuming?
            jitter = random()
            resume_after = 5 * jitter
            self._logger.debug("Re-identifying after %s seconds", resume_after)
            await sleep(resume_after)

            await self._identify_flow()

    async def _handle_dispatch(self, data: DispatchEvent) -> None:
        # Save sequence number for resuming.
        self.session_sequence_number = data["s"]

    async def _handle_ready(self, data: ReadyData) -> None:
        # Save session id for resuming
        self.session_id = data["session_id"]
        self.ready.set()

    async def _handle_resumed(self, data: dict[Any, Any]) -> None:  # TODO: This is not implemented in discord_typings.
        del data  # Unused
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
            await self.dispatcher.dispatch("critical", InvalidShardCountError())
        elif close_code == GatewayCloseCode.SHARDING_REQUIRED:
            self._logger.critical(
                "Received sharding required while sharding? Please make a issue on https://github.com/nextsnake/nextcore/issues"
            )
            # TODO: Should this be merged into the else block?
            await self.dispatcher.dispatch("critical", UnhandledCloseCodeError(close_code))
        elif close_code == GatewayCloseCode.INVALID_API_VERSION:
            self._logger.debug("Received invalid api version. Please update nextcore!")
            await self.dispatcher.dispatch("critical", InvalidApiVersionError())
        elif close_code == GatewayCloseCode.INVALID_INTENTS:
            self._logger.debug("Sent invalid intents.")
            await self.dispatcher.dispatch("critical", InvalidIntentsError())
        elif close_code == GatewayCloseCode.DISALLOWED_INTENTS:
            self._logger.debug("Sent disallowed intents. This should be enabled in the settings.")
            await self.dispatcher.dispatch("critical", DisallowedIntentsError())
        else:
            await self.dispatcher.dispatch("critical", UnhandledCloseCodeError(close_code))
            raise RuntimeError(f"Close code not handled: {close_code}")

    # Send wrappers
    async def _identify(self) -> None:
        """Identify to the gateway.

        .. note::
            See the `documentation <https://discord.dev/topics/gateway#identify>`__
        .. warning::
            This does not handle rate-limiting
        """
        payload: IdentifyCommand = {
            "op": GatewayOpcode.IDENTIFY.value,
            "d": {
                "token": self.token,
                "intents": self.intents,
                "properties": {
                    "os": platform,
                    "browser": self.library_name,
                    "device": self.library_name,
                },
                "compress": True,
                "shard": [self.shard_id, self.shard_count],
            },
        }
        # Not required parameters can't be set to anything for
        if self.large_threshold is not None:
            payload["d"]["large_threshold"] = self.large_threshold
        if self.presence is not None:
            payload["d"]["presence"] = self.presence

        await self._send(payload, wait_until_ready=False)

    async def presence_update(self, presence: UpdatePresenceData) -> None:
        """Changes the bot's presence for the current session.

        .. warning::
            This will not persist across sessions!

            Use the ``presence`` parameter to :class:`Shard`

        """
        payload: UpdatePresenceCommand = {"op": GatewayOpcode.PRESENCE_UPDATE.value, "d": presence}

        await self._send(payload)

    async def voice_state_update(self, update: UpdateVoiceStateData):
        """Updates the voice state of the logged in user.

        This is per guild.
        """

        payload: UpdateVoiceStateCommand = {"op": GatewayOpcode.VOICE_STATE_UPDATE.value, "d": update}

        await self._send(payload)

    async def _resume(self) -> None:
        """Resume the session

        .. note::
            See the `documentation <https://discord.dev/topics/gateway#resume>`__

        Raises
        ------
        :exc:`RuntimeError`
            Session id or sequence number is not set.
        """
        if self.session_id is None or self.session_sequence_number is None:
            raise RuntimeError("Session id or sequence number is not set")

        payload: ResumeCommand = {
            "op": GatewayOpcode.RESUME.value,
            "d": {
                "token": self.token,
                "session_id": self.session_id,
                "seq": self.session_sequence_number,
            },
        }
        await self._send(payload, wait_until_ready=False)

    @overload
    async def request_guild_members(
        self,
        guild_id: str | int,
        *,
        query: str,
        limit: int,
        presences: bool | UndefinedType = UNDEFINED,
        user_ids: str | int | list[str | int] | UndefinedType = UNDEFINED,
        nonce: str | UndefinedType = UNDEFINED,
    ) -> None:
        ...

    @overload
    async def request_guild_members(
        self,
        guild_id: str | int,
        *,
        limit: int | UndefinedType = UNDEFINED,
        presences: bool | UndefinedType = UNDEFINED,
        user_ids: str | int | list[str | int],
        nonce: str | UndefinedType = UNDEFINED,
    ) -> None:
        ...

    async def request_guild_members(
        self,
        guild_id: str | int,
        *,
        query: str | UndefinedType = UNDEFINED,
        limit: int | UndefinedType = UNDEFINED,
        presences: bool | UndefinedType = UNDEFINED,
        user_ids: str | int | list[str | int] | UndefinedType = UNDEFINED,
        nonce: str | UndefinedType = UNDEFINED,
    ) -> None:
        """Request info about the members in this guild.

        .. note::
            This will dispatch ``GUILD_MEMBERS_CHUNK`` events as a response.

        .. warning::
            This may be cancelled if the shard disconnects while chunking.

        Parameters
        ----------
        guild_id:
            The guild to request members from
        query:
            What the members username have to start with to be returned

            .. note::
                If this is not empty limit will be max 100.
        limit:
            The max amount of members to return.

            .. note::
                This can be 0 when used with a empty query.

                If this is 0, this would require the ``GUILD_MEMBERS`` intent
        presences:
            Whether to include presences for members requested.

            .. note::
                This requires the ``GUILD_PRESENCES`` intent.
        user_ids:
            The ID of the members to query.

            .. note::
                This has a limit of 100 members.
        nonce:
            A string which will be provided in the ``guild members chunk`` response to identify this request.

            .. note::
                This is max 32 characters.

                If it is longer it will be ignored.
        """
        data: dict[str, Any] = {"guild_id": guild_id}
        if query is not UNDEFINED:
            data["query"] = query
        if limit is not UNDEFINED:
            data["limit"] = limit
        if presences is not UNDEFINED:
            data["presences"] = presences
        if user_ids is not UNDEFINED:
            data["user_ids"] = user_ids
        if nonce is not UNDEFINED:
            data["nonce"] = nonce

        payload: RequestGuildMembersCommand = {"op": GatewayOpcode.REQUEST_GUILD_MEMBERS.value, "d": data}  # type: ignore [reportGeneralTypeIssues]

        await self._send(payload)

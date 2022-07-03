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

from collections import defaultdict
from logging import getLogger
from typing import TYPE_CHECKING

from aiohttp.helpers import get_running_loop

from nextcore.gateway.times_per import TimesPer

from ..common.dispatcher import Dispatcher
from .errors import InvalidShardCountError
from .shard import Shard

if TYPE_CHECKING:
    from typing import Any, Final

    from discord_typings import GatewayEvent
    from discord_typings.gateway import UpdatePresenceData

    from ..http import BotAuthentication, HTTPClient

__all__: Final[tuple[str, ...]] = ("ShardManager",)

logger = getLogger(__name__)


class ShardManager:
    """A automatic sharder implementation

    Parameters
    ----------
    authentication:
        Authentication info.
    intents:
        The intents the bot should connect with. See the `documentation <https://discord.dev/topics/gateway#gateway-intents>`__.
    http_client:
        The HTTP client to use for fetching info to connect to the gateway.
    shard_count:
        The amount of shards the bot should spawn. If this is not set, the bot will automatically decide and keep the shard count up to date.
    shard_ids:
        The shard ids the bot should spawn. If this is not set, the bot will use all shard ids possible with the :attr:`ShardManager.shard_count`. This requires :attr:`ShardManager.shard_count` to be set.
    presence:
        The initial presence the bot should connect with.

    Attributes
    ----------
    token:
        The bot's token
    intents:
        The intents the bot should connect with. See the `documentation <https://discord.dev/topics/gateway#gateway-intents>`__.
    shard_count:
        The amount of shards the bot should spawn. If this is not set, the bot will automatically decide and keep the shard count up to date.
    shard_ids:
        The shard ids the bot should spawn. If this is not set, the bot will use all shard ids possible with the :attr:`ShardManager.shard_count`. This requires :attr:`ShardManager.shard_count` to be set.
    presence:
        The initial presence the bot should connect with.
    active_shards:
        A list of all shards that are currently connected.
    raw_dispatcher:
        A dispatcher with raw payloads sent by discord. The event name is the opcode, and the value is the raw data.
    event_dispatcher:
        A dispatcher for DISPATCH events sent by discord. The event name is the event name, and the value is the inner payload.
    max_concurrency:
        The maximum amount of concurrent IDENTIFY's the bot can make.
    """

    __slots__ = (
        "authentication",
        "intents",
        "shard_count",
        "shard_ids",
        "presence",
        "active_shards",
        "pending_shards",
        "raw_dispatcher",
        "event_dispatcher",
        "dispatcher",
        "max_concurrency",
        "_active_shard_count",
        "_pending_shard_count",
        "_identify_rate_limits",
        "_http_client",
    )

    # TODO: Fix typehints in the docstring for shard_ids
    def __init__(
        self,
        authentication: BotAuthentication,
        intents: int,
        http_client: HTTPClient,
        *,
        shard_count: int | None = None,
        shard_ids: list[int] | None = None,
        presence: UpdatePresenceData | None = None,
    ) -> None:
        # User's params
        self.authentication: BotAuthentication = authentication
        self.intents: int = intents
        self.shard_count: Final[int | None] = shard_count
        self.shard_ids: Final[list[int] | None] = shard_ids
        self.presence: UpdatePresenceData | None = presence

        # Publics
        self.active_shards: list[Shard] = []
        self.pending_shards: list[Shard] = []
        self.raw_dispatcher: Dispatcher[int] = Dispatcher()
        self.event_dispatcher: Dispatcher[str] = Dispatcher()
        self.dispatcher: Dispatcher[str] = Dispatcher()
        self.max_concurrency: int | None = None

        # Privates
        self._active_shard_count: int | None = self.shard_count
        self._pending_shard_count: int | None = None
        self._identify_rate_limits: defaultdict[int, TimesPer] = defaultdict(lambda: TimesPer(1, 5))
        self._http_client: HTTPClient = http_client

        # Checks
        if shard_count is None and shard_ids is not None:
            raise ValueError("You have to specify shard_count if you specify shard_ids")

    async def connect(self) -> None:
        """Connect all the shards to the gateway.

        .. note::
            This will return once all shard have started connecting.

        Raises
        ------
        :exc:`RuntimeError`
            Already connected.
        """
        if self.active_shards:
            raise RuntimeError("Already connected!")
        connection_info = await self._http_client.get_gateway_bot(self.authentication)
        session_start_limits = connection_info["session_start_limit"]
        self.max_concurrency = session_start_limits["max_concurrency"]

        if self._active_shard_count is None:
            self._active_shard_count = connection_info["shards"]

        if self.shard_ids is None:
            shard_ids = list(range(self._active_shard_count))
        else:
            shard_ids = self.shard_ids

        for shard_id in shard_ids:
            shard = self._spawn_shard(shard_id, self._active_shard_count)

            # Register event listeners
            shard.raw_dispatcher.add_listener(self._on_raw_shard_receive)
            shard.event_dispatcher.add_listener(self._on_shard_dispatch)
            shard.dispatcher.add_listener(self._on_shard_critical, "critical")

            logger.info("Added shard event listeners")

            self.active_shards.append(shard)

    def _spawn_shard(self, shard_id: int, shard_count: int) -> Shard:
        assert self.max_concurrency is not None, "max_concurrency is not set. This is set in connect"
        rate_limiter = self._identify_rate_limits[shard_id % self.max_concurrency]

        shard = Shard(
            shard_id,
            shard_count,
            self.intents,
            self.authentication.token,
            rate_limiter,
            self._http_client,
            presence=self.presence,
        )

        # Here we lazy connect the shard. This gives us a bit more speed when connecting large sets of shards.
        loop = get_running_loop()
        loop.create_task(shard.connect())

        return shard

    # Handlers
    async def _on_raw_shard_receive(self, opcode: int, data: GatewayEvent) -> None:
        logger.debug("Relaying raw event")
        await self.raw_dispatcher.dispatch(opcode, data)

    async def _on_shard_dispatch(self, event_name: str, data: Any) -> None:
        logger.debug("Relaying event")
        await self.event_dispatcher.dispatch(event_name, data)

    async def _on_shard_critical(self, error: Exception):
        if isinstance(error, InvalidShardCountError):
            raise NotImplementedError("Re-scaling of shards is not implemented yet.")

        await self.dispatcher.dispatch("critical", error)

        await self.close()

    async def close(self) -> None:
        logger.debug("Closing shards")
        for shard in self.active_shards:
            await shard.close()
        for shard in self.pending_shards:
            await shard.close()

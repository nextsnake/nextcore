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
from typing import TYPE_CHECKING

from aiohttp.helpers import get_running_loop

from nextcore.gateway.times_per import TimesPer

from .dispatcher import Dispatcher
from .shard import Shard

if TYPE_CHECKING:
    from nextcore.typings.gateway.outer import (
        ServerGatewayDispatchPayload,
        ServerGatewayPayload,
    )
    from nextcore.typings.objects.update_presence import UpdatePresence

    from ..http.client import HTTPClient


class ShardManager:
    def __init__(
        self,
        token: str,
        intents: int,
        http_client: HTTPClient,
        *,
        shard_count: int | None = None,
        shard_ids: list[int] | None = None,
        presence: UpdatePresence | None = None,
    ) -> None:
        # User's params
        self.token: str = token
        self.intents: int = intents
        self.http_client: HTTPClient = http_client
        self.shard_count: int | None = shard_count
        self.shard_ids: list[int] | None = shard_ids
        self.presence: UpdatePresence | None = presence

        # Publics
        self.active_shards: list[Shard] = []
        self.pending_shards: list[Shard] = []
        self.raw_dispatcher: Dispatcher = Dispatcher()
        self.event_dispatcher: Dispatcher = Dispatcher()
        self.max_concurrency: int | None = None

        # Privates
        self._active_shard_count: int | None = self.shard_count
        self._pending_shard_count: int | None = None
        self._identify_ratelimits: defaultdict[int, TimesPer] = defaultdict(lambda: TimesPer(1, 5))

        # Checks
        if shard_count is None and shard_ids is not None:
            raise ValueError("You have to specify shard_count if you specify shard_ids")

    async def connect(self) -> None:
        connection_info = await self.http_client.get_gateway_bot()
        session_start_limits = connection_info["session_start_limit"]
        self.max_concurrency = session_start_limits["max_concurrency"]

        if self._active_shard_count is None:
            self._active_shard_count = connection_info["shards"]

        if self.shard_ids is None:
            shard_ids = [shard_id for shard_id in range(self._active_shard_count)]
        else:
            shard_ids = self.shard_ids

        for shard_id in shard_ids:
            shard = await self._spawn_shard(shard_id, self._active_shard_count)

            # Register event listeners
            shard.raw_dispatcher.add_listener(self._on_raw_shard_receive)
            shard.event_dispatcher.add_listener(self._on_shard_dispatch)

            self.active_shards.append(shard)

    async def _spawn_shard(self, shard_id: int, shard_count: int) -> Shard:
        assert self.max_concurrency is not None, "max_concurrency is not set. This is set in connect"
        ratelimiter = self._identify_ratelimits[shard_id % self.max_concurrency]

        shard = Shard(
            shard_id, shard_count, self.intents, self.token, ratelimiter, self.http_client, presence=self.presence
        )

        # Here we lazy connect the shard. This gives us a bit more speed when connecting large sets of shards.
        loop = get_running_loop()
        loop.create_task(shard.connect())

        return shard

    # Handlers
    async def _on_raw_shard_receive(self, opcode: int, data: ServerGatewayPayload) -> None:
        self.raw_dispatcher.dispatch(opcode, data)

    async def _on_shard_dispatch(self, event_name: str, data: ServerGatewayDispatchPayload) -> None:
        self.event_dispatcher.dispatch(event_name, data)
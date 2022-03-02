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

from collections import defaultdict
from logging import getLogger
from typing import TYPE_CHECKING

from .shard import Shard
from .times_per import TimesPer

if TYPE_CHECKING:
    from typing import Dict, List, Optional

    from ..http import HTTPClient

logger = getLogger(__name__)


class Gateway:
    """Automatic sharder and load balancer

    Parameters
    ----------
    token : :class:`str`
        The bot's token.
    intents : :class:`int`
        The bot's intents.
    http_client : :class:`HTTPClient`
        The HTTP client to use.
    shard_count : :class:`int`
        The number of shards to connect with. If set to None, this will automatically fetch the recommended amount of shards and update that number.
    """

    def __init__(self, token: str, intents: int, http_client: HTTPClient, *, shard_count: int | None = None) -> None:
        self.intents: int = intents
        """The bot's intents."""
        self.token = token
        """The token of the bot."""
        self.shard_count: Optional[int] = shard_count
        """How many shards the bot connects with. This may be None if the bot has not started yet."""
        self.max_concurrency: Optional[int] = None
        """How many shards the bot can connect with at the same time. This may be None if the bot has not started yet."""
        self.shard_count_locked: bool = shard_count is not None
        """If the shard count can't change. This will be set if shard_count is set."""

        self._active_shards: List[Shard] = []
        self._inactive_shards: List[Shard] = []
        self._http: HTTPClient = http_client
        self._identify_ratelimits: Dict[int, TimesPer] = defaultdict(lambda: TimesPer(1, 5))

    async def connect(self) -> None:
        """Connects the bot to the gateway.
        This will handle concurrency ratelimiting as long as you are not clustering.

        .. note::
            This will not run forever.
        """
        # Fetch gateway info.
        gateway_info = await self._http.get_gateway_bot()
        if self.shard_count is None:
            self.shard_count = gateway_info["shards"]
        self.max_concurrency = gateway_info["session_start_limit"]["max_concurrency"]

        # Connect shards.
        for shard_id in range(self.shard_count):
            shard = Shard(shard_id, self.shard_count, self.token, self.intents, self._http)
            self._active_shards.append(shard)
            await self._connect_shard(shard)

    async def _connect_shard(self, shard: Shard) -> None:
        """
        Connects a shard to the gateway.

        Parameters
        ----------
        shard : :class:`Shard`
            The shard to connect.
        """
        assert self.max_concurrency is not None, "Max concurrency is not set yet."

        # See https://discord.dev/topics/gateway#sharding-max-concurrency for more information.
        concurrency_key = shard.id % self.max_concurrency

        ratelimiter = self._identify_ratelimits[concurrency_key]
        logger.debug("Waiting for connect ratelimiter for shard %s.", shard.id)
        await ratelimiter.wait()
        logger.debug("Connecting to shard %s.", shard.id)
        await shard.connect()

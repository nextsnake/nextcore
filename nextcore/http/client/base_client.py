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

from abc import ABC, abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING
from nextcore.common import UNDEFINED

from ..route import Route

if TYPE_CHECKING:
    from typing import Any, Final, Literal
    from nextcore.common import UndefinedType

    from aiohttp import ClientResponse, ClientWebSocketResponse

logger = getLogger(__name__)

__all__: Final[tuple[str, ...]] = ("BaseHTTPClient",)


class BaseHTTPClient(ABC):
    """Base class for HTTP clients.

    This defines :meth:`BaseHTTPClient._request` for HTTP endpoint wrappers to use.
    """

    __slots__ = ()

    @abstractmethod
    async def request(
        self,
        route: Route,
        rate_limit_key: str | None,
        *,
        headers: dict[str, str] | None = None,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
        **kwargs: Any,
    ) -> ClientResponse:
        ...

    @abstractmethod
    async def connect_to_gateway(
        self,
        *,
        version: Literal[6, 7, 8, 9, 10] | UndefinedType = UNDEFINED,
        encoding: Literal["json", "etf"] | UndefinedType = UNDEFINED,
        compress: Literal["zlib-stream"] | UndefinedType = UNDEFINED,
    ) -> ClientWebSocketResponse:
        """Connects to the gateway

        **Example usage:**

        .. code-block:: python

            ws = await http_client.connect_to_gateway()


        Parameters
        ----------
        version:
            The major API version to use

            .. hint::
                It is a good idea to pin this to make sure something doesn't unexpectedly change
        encoding:
            Whether to use json or etf for payloads
        compress:
            Payload compression from data sent from Discord.

        Returns
        -------
        aiohttp.ClientWebSocketResponse
            The gateway websocket
        """
        
        ...


    @abstractmethod
    async def connect_to_voice_websocket(
        self,
        endpoint: str,
        *,
        version: Literal[1,2,3,4] | UndefinedType = UNDEFINED,
    ) -> ClientWebSocketResponse:
        """Connects to the voice WebSocket gateway

        **Example usage:**

        .. code-block:: python

            ws = await http_client.connect_to_voice_websocket()


        Parameters
        ----------
        endpoint:
            The voice server to connect to. 

            .. note::
                This can obtained from the `voice server update event <https://discord.dev/topics/gateway-events#voice-server-update>` and is usually in the format of ``servername.discord.media:443``
        version:
            The major API version to use

            .. hint::
                It is a good idea to pin this to make sure something doesn't unexpectedly change
            .. note::
                A list of versions can be found on the `voice versioning page <https://discord.dev/topics/voice-connections#voice-gateway-versioning>`__

        Returns
        -------
        aiohttp.ClientWebSocketResponse
            The voice websocket gateway
        """
        
        ...

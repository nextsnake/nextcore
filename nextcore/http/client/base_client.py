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

from ...common import UNDEFINED, UndefinedType
from .wrappers import (
    ApplicationCommandsHTTPWrappers,
    AuditLogHTTPWrappers,
    ChannelHTTPWrappers,
    EmojiHTTPWrappers,
    GatewayHTTPWrappers,
    GuildHTTPWrappers,
    GuildScheduledEventHTTPWrappers,
    GuildTemplateHTTPWrappers,
    InviteHTTPWrappers,
    OAuth2HTTPWrappers,
    StageInstanceHTTPWrappers,
    StickerHTTPWrappers,
    UserHTTPWrappers,
    VoiceHTTPWrappers,
    WebhookHTTPWrappers,
)

if TYPE_CHECKING:
    from typing import Final, Literal

    from aiohttp import ClientWebSocketResponse

logger = getLogger(__name__)

__all__: Final[tuple[str, ...]] = ("BaseHTTPClient",)


class BaseHTTPClient(
    ApplicationCommandsHTTPWrappers,
    AuditLogHTTPWrappers,
    ChannelHTTPWrappers,
    EmojiHTTPWrappers,
    GuildHTTPWrappers,
    GuildScheduledEventHTTPWrappers,
    GuildTemplateHTTPWrappers,
    InviteHTTPWrappers,
    StageInstanceHTTPWrappers,
    StickerHTTPWrappers,
    UserHTTPWrappers,
    VoiceHTTPWrappers,
    WebhookHTTPWrappers,
    GatewayHTTPWrappers,
    OAuth2HTTPWrappers,
    ABC,
):
    """Abstract base class for HTTP clients.

    This defines :meth:`AbstractHTTPClient._request` for HTTP endpoint wrappers to use.
    """

    __slots__ = ()

    @abstractmethod
    async def setup(self) -> None:
        """Sets up the HTTP session

        .. warning::
            This has to be called before :meth:`BaseHTTPClient._request` or :meth:`BaseHTTPClient.connect_to_gateway`

        Raises
        ------
        RuntimeError
            This can only be called once
        """
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

        Raises
        ------
        RuntimeError
            :meth:`BaseHTTPClient.setup` was not called yet.
        RuntimeError
            BaseHTTPClient was closed.

        Returns
        -------
        aiohttp.ClientWebSocketResponse
            The gateway websocket
        """

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

from aiohttp import web
from json import JSONDecodeError
from logging import getLogger
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
from typing import TYPE_CHECKING

from nextcore.common import Dispatcher


if TYPE_CHECKING:
    from typing import Final

    from discord_typings import InteractionData
    from multidict import CIMultiDictProxy


logger = getLogger(__name__)


__all__: Final[tuple[str, ...]] = (
    "InteractionEndpoint",
    "verify_signature",
)


def verify_signature(public_key: str, signature: str, timestamp: str, body: str) -> bool:
    verify_key = VerifyKey(bytes.fromhex(public_key))
    verify_key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))
    return True


class InteractionEndpoint:
    _public_key: str | None
    _route: str | None
    event_dispatcher: Dispatcher

    # def __init__(
    #         self,
    #         *,
    #         web_app: web.Application = None,
    #         route_path: str = "/interactions/test"
    # ):
    #     self.public_key: str | None = None
    #     self.app: web.Application = web_app or web.Application(middlewares=[interaction_endpoint("asdf", "/interactions/test")])
    #     self.site: web.TCPSite | None = None
    #     self.event_dispatcher: Dispatcher = Dispatcher()
    #
    #     self.app.add_routes([
    #         web.route("POST", route_path, self._on_interaction_incoming)
    #     ])

    def __init__(self):
        self._public_key = None
        self._route = None
        self.event_dispatcher = Dispatcher()

    def _verify_from_headers(self, headers: CIMultiDictProxy, body: str) -> bool:
        try:
            signature: str = headers.get("x-signature-ed25519")
            timestamp: str = headers.get("x-signature-timestamp")
            verify_signature(self._public_key, signature, timestamp, body)
            return True
        except BadSignatureError:
            return False

    async def _on_interaction_incoming(self, request: web.Request) -> web.Response | None:
        logger.debug("Incoming interaction endpoint request.")
        try:
            body = (await request.read()).decode("utf-8")
            if self._verify_from_headers(request.headers, body):
                logger.debug("Verified Discord signature headers, continuing.")
                interaction: InteractionData = await request.json()
                if interaction.get("type") == 1:
                    # logger.debug("Dispatching ping.")
                    await self.event_dispatcher.dispatch("ping", request, interaction)
                else:
                    await self.event_dispatcher.dispatch("interaction", request, interaction)

                return None
            else:
                logger.debug("Failed Discord signature headers, returning 401.")
                return web.Response(body="invalid request signature", status=401)

        except JSONDecodeError:
            logger.debug("Invalid json given, ignoring: %s", (await request.read()).decode())
            return web.Response(status=400)

    async def _handle_ping(self, request: web.Request, interaction):
        response = web.json_response(data={"type": 1})
        await response.prepare(request)
        await response.write_eof()

    def middleware(self, public_key: str, route: str = "/interactions"):
        self._public_key = public_key
        self._route = route

        @web.middleware
        async def interaction_endpoint_middleware(request: web.Request, handler):
            print("MIDDLEWARE TRIGGERED.")
            if request.path == self._route and request.method == "POST":
                logger.debug("Request POSTing on interaction endpoint route, intercepting.")
                return await self._on_interaction_incoming(request)
            else:
                resp = await handler(request)
                return resp

        return interaction_endpoint_middleware

    async def start(self, public_key: str, *, port: int = 8080, route="/interactions"):
        app = web.Application(middlewares=[self.middleware(public_key, route)])
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        self.event_dispatcher.add_listener(self._handle_ping, "ping")
        await site.start()
        logger.info("%s listening on %s", self.__class__.__name__, site.name)

    def run(
            self,
            public_key: str,
            *,
            loop: asyncio.AbstractEventLoop | None = None,
            port: int = 8080,
            route: str = "/interactions",
    ):
        loop = loop or asyncio.new_event_loop()
        task = loop.create_task(self.start(public_key, port=port, route=route))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            logger.debug("KeyboardInterrupt encountered, stopping loop.")
            task.cancel()

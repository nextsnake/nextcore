from __future__ import annotations

from aiohttp import web
from json import JSONDecodeError
from logging import getLogger
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from multidict import CIMultiDictProxy


logger = getLogger(__name__)


__all__ = (
    "InteractionEndpoint",
    "verify_signature",
)


def verify_signature(public_key: str, signature: str, timestamp: str, body: str):
    verify_key = VerifyKey(bytes.fromhex(public_key))
    verify_key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))


class InteractionEndpoint:
    def __init__(
            self,
            public_key: str,
            *,
            web_app: web.Application = None,
            route_path: str = "/"
    ):
        self.public_key: str = public_key
        self.app: web.Application = web_app or web.Application()
        self.site: web.TCPSite | None = None

        self.app.add_routes([
            web.route("POST", route_path, self._on_interaction_incoming)
        ])

    async def _verify_from_headers(self, headers: CIMultiDictProxy, body: str) -> bool:
        try:
            signature = headers.get("x-signature-ed25519")
            timestamp = headers.get("x-signature-timestamp")
            verify_signature(self.public_key, signature, timestamp, body)
            return True
        except BadSignatureError:
            return False

    async def _on_interaction_incoming(self, request: web.Request) -> web.Response:
        logger.debug("Incoming interaction endpoint request.")
        try:
            body = (await request.read()).decode("utf-8")
            if await self._verify_from_headers(request.headers, body):
                logger.debug("Verified Discord signature headers, continuing.")
                interaction = await request.json()
                if interaction.get("type") == 1:
                    logger.debug("Calling on_ping.")
                    return await self.on_ping(interaction)
                elif interaction.get("type") == 2:
                    logger.debug("Calling on_application_command.")
                    return await self.on_application_command(interaction)
                elif interaction.get("type") == 3:
                    logger.debug("Calling on_message_component.")
                    return await self.on_message_component(interaction)
                elif interaction.get("type") == 4:
                    logger.debug("Calling on_application_command_autocomplete.")
                    return await self.on_application_command_autocomplete(interaction)
                elif interaction.get("type") == 5:
                    logger.debug("Calling on_modal_submit.")
                    return await self.on_modal_submit(interaction)
                else:
                    logger.warning(
                        "Received interaction of unhandled type %s: %s", interaction.get("type"), interaction
                    )

            else:
                logger.debug("Failed Discord signature headers, returning 401.")
                return web.Response(body="invalid request signature", status=401)

        except JSONDecodeError:
            logger.debug("Invalid json given, ignoring: %s", (await request.read()).decode())
            return web.Response(status=400)

    async def on_ping(self, interaction) -> web.Response:
        return web.json_response(data={"type": 1})

    async def on_application_command(self, interaction) -> web.Response:
        return web.json_response(
            {
                "type": 4,
                "data": {
                    "content": "THIS IS ~~A PLACEHOLDER~~ SPARTA! <https://www.youtube.com/watch?v=PCiIhr8QN1c>"
                }
            }
        )

    async def on_message_component(self, interaction) -> web.Response:
        pass

    async def on_application_command_autocomplete(self, interaction) -> web.Response:
        pass

    async def on_modal_submit(self, interaction) -> web.Response:
        pass

    async def start(self, *, site: web.TCPSite = None, port: int = 8080):
        if site:
            self.site = site

        if not self.site:
            runner = web.AppRunner(self.app)
            await runner.setup()
            self.site = web.TCPSite(runner, "0.0.0.0", port)

        await self.site.start()
        logger.info("%s listening on %s", self.__class__.__name__, self.site.name)

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
from logging import getLogger
from typing import TYPE_CHECKING

from nextcore.common.dispatcher import Dispatcher
from ...common.maybe_coro import maybe_coro
from ...common.json import json_dumps, json_loads
from .request import InteractionRequest
from .response import InteractionResponse
from .request_verifier import RequestVerifier
from .errors import RequestVerificationError
from .interaction import Interaction

if TYPE_CHECKING:
    from typing import Final, Callable, Awaitable, Union, Literal
    from typing_extensions import TypeAlias

    from discord_typings import InteractionData

    RequestCheck: TypeAlias = Callable[[InteractionRequest], Union[Awaitable[None], None]]

logger = getLogger(__name__)

# TODO: The controller name is stupid.
class InteractionController:
    """A class for handling endpoint interactions
    
    .. warn::
        Endpoint interactions are weird.

        While endpoint interactions are easier to scale, gateway interactions are easier to use and seem more stable.
    """
    def __init__(self, public_key: str | bytes) -> None:
        self.dispatcher: Final[Dispatcher[Literal["raw_request", "check_failed", "check_error"]]] = Dispatcher()
        self.interaction_dispatcher: Final[Dispatcher[int]] = Dispatcher()

        # Request verification
        self.request_verifier: Final[RequestVerifier] = RequestVerifier(public_key)
        self.request_checks: list[RequestCheck] = [self.check_has_required_headers, self.check_has_valid_signature]

        self.add_default_interaction_handlers()

    def add_default_interaction_handlers(self):
        self.interaction_dispatcher.add_listener(self.handle_interaction_ping, 1) # TODO: Extract magic value to a enum

    async def handle_interaction_request(self, request: InteractionRequest) -> InteractionResponse:
        """Callback for handling a interaction request

        .. note::
            This is meant to be called by a web-framework adapter.

        Parameters
        ----------
        request:
            The HTTP request that was received for this interaction

        Returns
        -------
        InteractionResponse:
            What to respond with.

        """
        await self.dispatcher.dispatch("raw_request", request)
        try:
            await self.verify_request(request)
        except RequestVerificationError as error:
            await self.dispatcher.dispatch("check_failed", error.reason)
            return InteractionResponse(401, error.reason)
        except Exception as error:
            await self.dispatcher.dispatch("check_error", error)
            logger.exception("Error occured while handling interaction")
            error_response = {"detail": f"Internal check error. Check the {__name__} logger for details"}
            return InteractionResponse(500, json_dumps(error_response))
        
        data: InteractionData = json_loads(request.body)

        interaction = Interaction(request, data)
        await self.interaction_dispatcher.dispatch(data["type"], interaction, wait=True)

        if interaction.response is None:
            error_response = {"detail": "Interaction.response was never set!"}
            logger.error("No interaction.response was set!")
            return InteractionResponse(500, json_dumps(error_response))

        return InteractionResponse(200, json_dumps(interaction.response))

    async def verify_request(self, request: InteractionRequest) -> None:
        """Try all request checks

        Parameters
        ----------
        request:
            The request made
        Raises
        ------
        RequestVerificationError:
            The request checks did not succeed, so you should not let it execute.
            The reason it did not succeed is also in the error.
        Exception:
            A error in one of the checks was raised. In this case, 
        """
        for check in self.request_checks:
            await maybe_coro(check, request)

    # Built-in checks
    def check_has_required_headers(self, request: InteractionRequest) -> None:
        """A request check that makes sure the signature and timestamp headers are present

        .. note::
            This check is added by default to :attr:`request_checks`
        .. warning::
            This must be included before :meth:`check_has_valid_signature` unless you have something else similar.

            If not, a server error will happen.
        
        The headers that are checked for are:
        - ``X-Signature-Ed25519``
        - ``X-Signature-Timestamp``
        """
        required_headers = ["X-Signature-Ed25519", "X-Signature-Timestamp"]

        for header in required_headers:
            if header not in request.headers:
                raise RequestVerificationError(f"Missing the \"{header}\" header")

    def check_has_valid_signature(self, request: InteractionRequest) -> None:
        """A request check that makes sure the request is signed by your applications public key.

        .. note::
            This check is added by default to :attr:`request_checks`
        .. warning::
            This or something similar must check the request or Discord will reject adding the interactions endpoint url.
        """
        signature = request.headers["X-Signature-Ed25519"]
        timestamp = request.headers["X-Signature-Timestamp"]
        is_from_discord = self.request_verifier.is_valid(signature, timestamp, request.body)

        if not is_from_discord:
            raise RequestVerificationError("Request signature is invalid")

    # Default handlers
    async def handle_interaction_ping(self, interaction: Interaction):
        # Acknowledge ping
        interaction.response = {"type": 1}

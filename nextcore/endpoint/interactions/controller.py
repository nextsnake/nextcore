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
from ...common.maybe_coro import maybe_coro
from ...common.json import json_dumps
from .request import InteractionRequest
from .response import InteractionResponse
from .request_verifier import RequestVerifier
from .errors import RequestVerificationError

if TYPE_CHECKING:
    from typing import Final, Callable, Awaitable, Union
    from typing_extensions import TypeAlias

    RequestCheck: TypeAlias = Callable[[InteractionRequest], Union[Awaitable[None], None]]

logger = getLogger(__name__)

# TODO: The controller name is stupid.
class InteractionController:
    """A class for handling endpoint interactions"""
    def __init__(self, public_key: str | bytes) -> None:
        self.request_verifier: Final[RequestVerifier] = RequestVerifier(public_key)
        self.request_checks: list[RequestCheck] = [self.check_has_required_headers, self.check_has_valid_signature]

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
        try:
            await self.verify_request(request)
        except RequestVerificationError as error:
            return InteractionResponse(401, error.reason)
        except:
            logger.exception("Error occured while handling interaction")
            error_response = {"detail": f"Internal check error. Check the {__name__} logger for details"}
            return InteractionResponse(500, json_dumps(error_response))

        return InteractionResponse(status_code=200, body="{\"type\": 1}")

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

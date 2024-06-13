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
from typing import TYPE_CHECKING
from aiohttp.web_app import Application
from logging import getLogger

from aiohttp.web_response import json_response, Response

from ...interactions.request import InteractionRequest
from ..abc import AbstractAdapter

if TYPE_CHECKING:
    from ...interactions.controller import InteractionController
    from aiohttp.web_request import Request
    from aiohttp.web_response import StreamResponse
    from typing import Final

logger = getLogger(__name__)

class AIOHTTPAdapter(AbstractAdapter):
    """The AIOHTTP endpoint adapter
    """

    def __init__(self) -> None:
        self.app: Application = Application()
        
        # Controllers
        self._interaction_controller: InteractionController | None = None

        self._add_routes()

    def _add_routes(self):
        """This is automatically called by :meth:`__init__`!

        The point of this being a seperate function is that it can be overriden by a sub-class.

        .. note::
            This counts as the public API, so any major changes to this will require a major version bump.
        """

        self.app.router.add_post("/interaction", self.handle_interaction_request)

    # Controller registrations
    def set_interaction_controller(self, controller: InteractionController | None) -> None:
        """Set the interaction controller

        This should register the controller and all events relating to interactions should be passed to the controller.

        Parameters
        ----------
        controller:
            The controller to set. If this is :data:`None` remove the controller.

            If a controller is already set, remove it.
        """
        self._interaction_controller = controller

    async def handle_interaction_request(self, request: Request) -> StreamResponse:
        if self._interaction_controller is None:
            return json_response({"detail": "No interaction controller registered"})

        raw_body = await request.read()

        try:
            body = raw_body.decode()
        except ValueError:
            return json_response({"detail": "Request body is not UTF-8 encoded"}, status=400)

        interaction_request = InteractionRequest(request.headers, body)
        
        interaction_response = await self._interaction_controller.handle_interaction_request(interaction_request)

        return Response(body=interaction_response.body, status=interaction_response.status_code, headers={"Content-Type": "application/json"})


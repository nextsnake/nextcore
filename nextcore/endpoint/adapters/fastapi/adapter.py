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

from fastapi import FastAPI
from typing import TYPE_CHECKING
from .models.interactions.error import Error as ErrorModel

if TYPE_CHECKING:
    from typing import Final
    from fastapi import Request, Response

class FastAPIAdapter:
    """The FastAPI endpoint adapter.
    """
    def __init__(self) -> None:
        self.app: Final[FastAPI] = FastAPI()

        # Register handlers
        self.app.add_api_route("/interaction", self.on_interaction_request, responses={200: ErrorModel})

    async def on_interaction_request(self, request: Request) -> Response:
        ...

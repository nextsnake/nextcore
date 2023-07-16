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

if TYPE_CHECKING:
    from discord_typings import InteractionData, InteractionResponseData
    from .request import InteractionRequest
    from typing import Final

class Interaction:
    """A wrapper around a endpoint interaction to allow responses to a HTTP request

    **Example Usage**

    .. code-block:: python3

        interaction = Interaction(request, json.loads(request.body))

        interaction.response = {"type": 1}

    Attributes
    ----------
    request:
        The raw HTTP request made by Discord.
    data:
        The json data inside the HTTP request.
    response:
        What to respond to the HTTP request with.
    """
    def __init__(self, request: InteractionRequest, data: InteractionData) -> None:
        self.request: Final[InteractionRequest] = request
        self.data: Final[InteractionData] = data
        self.response: InteractionResponseData | None = None

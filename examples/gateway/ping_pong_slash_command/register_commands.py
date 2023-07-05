# The MIT License (MIT)
#
# Copyright (c) 2022-present tag-epic
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
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

"""
The register script for this example.

This will register the "ping" slash command we need for this example.

NOTE: This only needs to be run once per bot, and should be ran before the example.
WARNING: This will remove all other commands
"""

from __future__ import (  # We want to use newer type hinting. If you are using python 3.9+ feel free to remove this.
    annotations,
)

import asyncio
from os import environ

from discord_typings import ApplicationCommandPayload

from nextcore.http import BotAuthentication, HTTPClient, Route

# Constants
AUTHENTICATION = BotAuthentication(environ["TOKEN"])
APPLICATION_ID = environ["APPLICATION_ID"]  # This should also usually be the same as your bots id.
COMMANDS: list[ApplicationCommandPayload] = [  # TODO: Currently we have no TypedDict for this.
    {"name": "ping", "description": "Responds with pong!"}
]

http_client = HTTPClient()


async def main() -> None:
    await http_client.setup()

    route = Route("PUT", "/applications/{application_id}/commands", application_id=APPLICATION_ID)
    await http_client.request(
        route, rate_limit_key=AUTHENTICATION.rate_limit_key, headers=AUTHENTICATION.headers, json=COMMANDS
    )

    print("Commands registered")

    await http_client.close()


asyncio.run(main())

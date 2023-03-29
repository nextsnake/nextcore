# The MIT License (MIT)
#
# Copyright (c) 2022-present nextcore developers
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

import asyncio
from os import environ

from discord_typings import ChannelData

from nextcore.http import BotAuthentication, HTTPClient, Route

# Constants
AUTHENTICATION = BotAuthentication(environ["TOKEN"])
CHANNEL_ID = environ["CHANNEL_ID"]


async def main():
    http_client = HTTPClient()
    await http_client.setup()

    # Documentation can be found on https://discord.dev/resources/channel#get-channel

    # Making Routes is almost like a f-string.
    # What you do is you take the route from the docs, "/channels/{channel.id}" for example
    # And replace . with _ and pass parameters as kwargs
    # Do note that you cannot replace {channel_id} directly with your channel id, that will cause issues.
    route = Route("GET", "/channels/{channel_id}", channel_id=CHANNEL_ID)

    # No authentication is used, so rate_limit_key None here is equivilent of your IP.
    response = await http_client.request(
        route,
        rate_limit_key=AUTHENTICATION.rate_limit_key,
        headers=AUTHENTICATION.headers,
    )
    channel: ChannelData = await response.json()

    print(channel.get("name"))  # DM channels do not have names

    await http_client.close()


asyncio.run(main())

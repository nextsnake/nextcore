# The MIT License (MIT)
#
# Copyright (c) 2022-present nextcore
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
A simple "ping pong" example of using nextcore.

This will respond with "pong" every time someone sends "ping" in the chat.
"""

import asyncio
from os import environ

from nextcore.gateway import ShardManager
from nextcore.http import HTTPClient, Route

# Constants
TOKEN = environ["TOKEN"]
INTENTS = 33280  # Guild messages and message content intents.

# Create a ratelimit_key
RATELIMIT_KEY = hash(TOKEN)

# Create a HTTPClient and a ShardManager.
# A ShardManager is just a neat wrapper around Shard objects.
http_client = HTTPClient()
shard_manager = ShardManager(environ["TOKEN"], INTENTS, http_client)


@shard_manager.event_dispatcher.listen("MESSAGE_CREATE")
async def on_message(message):  # TODO: discord_typings doesnt have message create event yet
    # This receives the raw message data.
    if message["content"] == "ping":
        # Create a endpoint object. This is used for calculating the ratelimit.
        # The second argument will be run .format on with the kwargs from Route.
        # If you specify guild_id, channel_id or webhook_id, this will be used to calculate the ratelimit.
        route = Route("POST", "/channels/{channel_id}/messages", channel_id=message["channel_id"])
        await http_client._request(
            route,
            json={"content": "pong"},
            ratelimit_key=RATELIMIT_KEY,
            headers={"Authorization": f"Bot {TOKEN}"},
        )  # TODO: Move to a wrapper function


async def main():
    # This should return once all shards have started to connect.
    # This does not mean they are connected.
    await shard_manager.connect()

    # We need to wait so asyncio doesn't cleanup the bot.
    # This will wait forever.
    # TODO: Replace this with wait until a critical error occurs.

    future: asyncio.Future[None] = asyncio.Future()
    await future


asyncio.run(main())

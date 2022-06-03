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

"""
A simple "ping pong" example of using nextcore.

This will respond with "pong" every time someone sends "ping" in the chat.
"""

import asyncio
from os import environ
from typing import cast

from discord_typings import MessageData

from nextcore.gateway import ShardManager
from nextcore.http import BotAuthentication, HTTPClient

# Constants
AUTHENTICATION = BotAuthentication(environ["TOKEN"])

# Intents are a way to select what intents Discord should send to you.
# For a list of intents see https://discord.dev/topics/gateway#gateway-intents
INTENTS = 1 << 9 | 1 << 15  # Guild messages and message content intents.


# Create a HTTPClient and a ShardManager.
# A ShardManager is just a neat wrapper around Shard objects.
http_client = HTTPClient()
shard_manager = ShardManager(AUTHENTICATION, INTENTS, http_client)


@shard_manager.event_dispatcher.listen("MESSAGE_CREATE")
async def on_message(message: MessageData):
    # This function will be called every time a message is sent.
    if message["content"] == "ping":
        # Send a pong message to respond.
        await http_client.create_message(AUTHENTICATION, message["channel_id"], content="pong")


async def main():
    # This should return once all shards have started to connect.
    # This does not mean they are connected.
    await shard_manager.connect()

    # Raise a error and exit whenever a critical error occurs
    error = await shard_manager.dispatcher.wait_for(lambda: True, "critical")

    raise cast(Exception, error)


asyncio.run(main())

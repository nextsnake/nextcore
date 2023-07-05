<div align="center">

  <img alt="" src="docs/_static/logo.svg" width="160px"/>
  
  # Nextcore
  <sub>A low level Discord API wrapper.</sub>
  
</div>

### ✨ Features

- #### Speed

  We try to make the library as fast as possible, without compromising on readability of the code or features.
  
- #### Modularity

  All the components can easily be swapped out with your own.

- #### Control

  Nextcore offers fine-grained control over things most libraries don't support.  
  
  This currently includes:  
  - Setting priority for individual requests
  - Swapping out components

<br>

<div align="center">

  # Examples
  
</div>

### 🏓 Ping pong
A simple "ping pong" example in nextcore.
This will respond with "pong" each time someone sends "ping" in the chat.
```py
import asyncio
from os import environ
from typing import cast

from discord_typings import MessageData

from nextcore.gateway import ShardManager
from nextcore.http import BotAuthentication, HTTPClient, Route

# Constants
AUTHENTICATION = BotAuthentication(environ["TOKEN"])

# Intents are a way to select what intents Discord should send to you.
# For a list of intents see https://discord.dev/topics/gateway#gateway-intents
GUILD_MESSAGES_INTENT = 1 << 9
MESSAGE_CONTENT_INTENT = 1 << 15

INTENTS = GUILD_MESSAGES_INTENT | MESSAGE_CONTENT_INTENT  # Guild messages and message content intents.


# Create a HTTPClient and a ShardManager.
# A ShardManager is just a neat wrapper around Shard objects.
http_client = HTTPClient()
shard_manager = ShardManager(AUTHENTICATION, INTENTS, http_client)


@shard_manager.event_dispatcher.listen("MESSAGE_CREATE")
async def on_message(message: MessageData):
    # This function will be called every time a message is sent.
    if message["content"] == "ping":
        # Send a pong message to respond.
        route = Route("POST", "/channels/{channel_id}/messages", channel_id=message["channel_id"])

        await http_client.request(
            route,
            rate_limit_key=AUTHENTICATION.rate_limit_key,
            json={"content": "pong"},
            headers=AUTHENTICATION.headers,
        )


async def main():
    await http_client.setup()

    # This should return once all shards have started to connect.
    # This does not mean they are connected.
    await shard_manager.connect()

    # Raise a error and exit whenever a critical error occurs
    (error,) = await shard_manager.dispatcher.wait_for(lambda: True, "critical")

    raise cast(Exception, error)


asyncio.run(main())
```

> More examples can be seen in the [examples](examples/) directory.

<br>

## Contributing
Want to help us out? Please read our [contributing](https://nextcore.readthedocs.io/en/latest/contributing/getting_started.html) docs.

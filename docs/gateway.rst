.. currentmodule:: nextcore.gateway

Gateway
=======

Gateway quickstart
------------------

.. hint::
   We recommend that you read the :ref:`Making requests` tutorial before this, as we will not explain HTTP concepts here.
.. hint::
   The finished example can be found `here <https://github.com/nextsnake/nextcore/tree/master/examples/gateway/ping_pong>`__
.. note::
   We will use await at the top level here as it's easier to explain. For your own code, please use an async function.

   If you want a example of how it can be done in an async function, see the full example.

Setting up
^^^^^^^^^^
.. code-block:: python3

    import asyncio
    from os import environ
    from typing import cast

    from discord_typings import MessageData

    from nextcore.gateway import ShardManager
    from nextcore.http import BotAuthentication, HTTPClient, Route

    # Constants
    AUTHENTICATION = BotAuthentication(environ["TOKEN"])

Intents
^^^^^^^
Discord uses intents to select what you want to be received from the gateway to reduce wasted resources.
This is done via bitflags.

A list of intents can be found on the `intents page <https://discord.dev/topics/gateway#gateway-intents>`__

In this example we want the message intent, and the message content intent.

.. code-block:: python3

   GUILD_MESSAGES_INTENT = 1 << 9
   MESSAGE_CONTENT_INTENT = 1 << 15

.. note::
   This can also be stored in binary representation.

   .. code-block:: python3

        GUILD_MESSAGES_INTENT = 0b1000000000
        MESSAGE_CONTENT_INTENT = 0b1000000000000000

If you want to use multiple intents, you can combine them using bitwise or (``|``).

.. code-block:: python3

   INTENTS = GUILD_MESSAGES_INTENT | MESSAGE_CONTENT_INTENT

Now just give it to the :class:`ShardManager`.

.. code-block:: python3
   
   http_client = HTTPClient()
   shard_manager = ShardManager(AUTHENTICATION, INTENTS, http_client)

.. note::
   Discord marks the ``MESSAGE_CONTENT_INTENT`` as "privileged", meaning you have to turn on a switch in the `developer portal <https://discord.com/developers/applications>`__

Creating a listener
^^^^^^^^^^^^^^^^^^^
Lets create a listener for whenever someone sends a message

A list of events can be found on the `Receive events <https://discord.dev/topics/gateway-events#receive-events>`__ page

.. code-block:: python3

    @shard_manager.event_dispatcher.listen("MESSAGE_CREATE")
    async def on_message(message: MessageData):
        # This function will be called every time a message is sent.

Now just check if someone said ``ping`` and respond with ``pong``

.. code-block:: python3

    if message["content"] == "ping":
        # Send a pong message to respond.
        route = Route("POST", "/channels/{channel_id}/messages", channel_id=message["channel_id"])

        await http_client.request(
            route,
            rate_limit_key=AUTHENTICATION.rate_limit_key,
            json={"content": "pong"},
            headers=AUTHENTICATION.headers,
        )

.. hint::
   Confused by this? Check out the :ref:`Making requests` tutorial!

Connecting to Discord
^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python3

    await http_client.setup()
    await shard_manager.connect()

.. need absolute ref for HTTPClient as its in the http module
.. warning::
   :meth:`HTTPClient.setup() <nextcore.http.HTTPClient.setup>` needs to be called before :meth:`ShardManager.connect` 
.. note::
   :meth:`ShardManager.connect` will return once every shard has started to connect

Stopping the script from stopping
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Since the :meth:`ShardManager.connect` function returns once every shard has started to connect, the script closes as the main thread has nothing to do.

We can wait for a critical error before closing to fix this.

.. code-block:: python3

    (error,) = await shard_manager.dispatcher.wait_for(lambda: True, "critical")

    raise cast(Exception, error)

.. note::
   The weird ``(error, )`` thing is to extract the first element out of the tuple.

Continuing
^^^^^^^^^^
We suggest that you look into `interactions & application commands <https://discord.dev/interactions/application-commands>`__ as your next topic.
They allow you to add `buttons <https://discord.dev/interactions/message-components#buttons>`__ and `slash commands <https://discord.dev/interactions/application-commands#slash-commands>`__ and other cool stuff!
    

Gateway reference
-----------------
.. autoclass:: ShardManager
   :members:

.. autoclass:: Shard
   :members:

.. autoclass:: GatewayOpcode
   :members:

.. autoclass:: Decompressor
   :members:

Gateway errors
--------------
.. autoexception:: ReconnectCheckFailedError
   :members:

.. autoexception:: DisconnectError
   :members:

.. autoexception:: InvalidIntentsError
   :members:

.. autoexception:: DisallowedIntentsError
   :members:

.. autoexception:: InvalidTokenError
   :members:

.. autoexception:: InvalidApiVersionError
   :members:

.. autoexception:: InvalidShardCountError
   :members:

.. autoexception:: UnhandledCloseCodeError
   :members:

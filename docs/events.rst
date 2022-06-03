.. currentmodule:: nextcore


Events
======
This is a document showing you the arguments from the different instances of :class:`common.Dispatcher` in the library.

Raw Dispatcher
--------------
Can be found on :attr:`ShardManadger.raw_dispatcher <gateway.ShardManager.raw_dispatcher>` and :attr:`Shard.raw_dispatcher <gateway.Shard.raw_dispatcher>`.
These are the raw dispatchers that just relay raw events from the discord websocket (the gateway).

The event name here is the gateway `opcode <https://discord.dev/docs/topics/gateway#gateway-opcodes>`__.

**Example usage:**

.. code-block:: python

    @shard.listen(GatewayOpcode.HEARTBEAT_ACK)
    async def on_ready(data):
        print("<3")

Event Dispatcher
----------------
Can be found on :attr:`ShardManadger.event_dispatcher <gateway.ShardManager.event_dispatcher>` and :attr:`Shard.event_dispatcher <gateway.Shard.event_dispatcher>`.
These dispatchers dispatch the data inside the ``d`` key of a :attr:`GatewayOpcode.DISPATCH` event.

The event name is the Dispatch `event name <https://discord.dev/topics/gateway#commands-and-events-gateway-events>`__.

**Example usage:**

.. code-block:: python
   
   @shard.listen("READY")
   async def on_ready(data: ReadyData):
      print(f"Logged in as {data.user.username}#{data.user.discriminator}")

Shard dispatcher
----------------
Can be found on :attr:`Shard.dispatcher <gateway.Shard.dispatcher>`.
A dispatcher for shard changes that is not a event sent by Discord.

disconnect
^^^^^^^^^^
Whenever Discord disconnects us from the gateway.

.. note::
   This does not dispatch closes made by the :class:`gateway.Shard` itself.

**Example usage:**

.. code-block:: python

   @shard.listen("disconnect")
   async def on_disconnect(close_code: int):
      print(f"Disconnected with close code {close_code}")

client_disconnect
^^^^^^^^^^^^^^^^^
Whenever we disconnect from the Discord gateway.

**Example usage:**

.. code-block:: python

   @shard.listen("client_disconnect")
   async def on_client_disconnect(close: bool) -> None:
      if close:
         print("We deleted and deleted the session! We should not be able to resume.")
      else:
         print("We disconnected and can still resume!")


sent
^^^^
Whenever we send a message to Discord over the websocket.

**Example usage:**

.. code-block:: python

   @shard.listen("sent")
   async def on_sent(data: dict):
      print(f"Sent {data}")

critical
^^^^^^^^
Whenever a critical event happens, this event is dispatched. The first argument will be a :class:`Exception` object of what happened.

**Example usage:**

.. code-block:: python

    @shard.dispatcher.listen("critical")
    async def on_critical(error):
        print(f"Critical error: {error}")

HTTPClient dispatcher
---------------------
Can be found on :attr:`HTTPClient.dispatcher <http.HTTPClient.dispatcher>`.

The event name is a :class:`str` representing the event name.

request_response
^^^^^^^^^^^^^^^^
Whenever a response to a request to Discord has been received, this event is dispatcher. The first argument will be the :class:`aiohttp.ClientResponse` object.

**Example usage:**

.. code-block:: python

    @http_client.dispatcher.listen("request_response")
    async def on_request_response(response: aiohttp.ClientResponse):
        print(f"Status code: {response.status}")

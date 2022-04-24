Welcome to Nextcore's documentation!
====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   http
   gateway
   common

   events

Quickstart
==========
Basic "hello world" example:

.. code-block:: python

   from __future__ import annotations
   import asyncio
   from os import environ
   from typing import TYPE_CHECKING

   from nextcore.gateway import ShardManager
   from nextcore.http import HTTPClient

   if TYPE_CHECKING:
       # Type hints doesn't exist at runtime, so it is inside a TYPE_CHECKING check.
       from nextcore.typings import MessageCreateData
   
   # Create a HTTPClient and a ShardManager.
   # A ShardManager is just a neat wrapper around Shard objects.
   http_client = HTTPClient()
   shard_manager = ShardManager(environ["TOKEN"], 512, http_client)


   @shard_manager.event_dispatcher.listen("MESSAGE_CREATE")
   async def on_message(message: MessageCreateData):
       # This receives the raw message data.
       if message["content"] == "!ping":
           await http_client.send_message(message["channel_id"], content="Pong!")

   asyncio.run(shard_manager.connect())



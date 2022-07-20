Gateway
=======

Gateway quickstart
------------------

Basic ping-pong example
************************
This will respond with ``pong`` every time someone sends ``ping`` in chat.

.. literalinclude:: ../examples/gateway/ping_pong.py
   :lines: 28-
   :language: python


Gateway reference
-----------------
.. autoclass:: nextcore.gateway.ShardManager
   :members:

.. autoclass:: nextcore.gateway.Shard
   :members:

.. autoclass:: nextcore.gateway.GatewayOpcode
   :members:

Gateway errors
--------------
.. autoexception:: nextcore.gateway.ReconnectCheckFailedError
   :members:

.. autoexception:: nextcore.gateway.DisconnectError
   :members:

.. autoexception:: nextcore.gateway.InvalidIntentsError
   :members:

.. autoexception:: nextcore.gateway.DisallowedIntentsError
   :members:

.. autoexception:: nextcore.gateway.InvalidTokenError
   :members:

.. autoexception:: nextcore.gateway.InvalidApiVersionError
   :members:

.. autoexception:: nextcore.gateway.InvalidShardCountError
   :members:

.. autoexception:: nextcore.gateway.UnhandledCloseCodeError
   :members:

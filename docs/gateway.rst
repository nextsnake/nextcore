.. currentmodule:: nextcore.gateway

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
.. autoclass:: ShardManager
   :members:

.. autoclass:: Shard
   :members:

.. autoclass:: GatewayOpcode
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

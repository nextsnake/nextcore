.. currentmodule:: nextcore.http

HTTP
====

Making requests
---------------

.. hint::
   The finished example can be found `here <https://github.com/nextsnake/nextcore/blob/master/examples/http/get_channel.py>`__
.. note::
   We will use await at the top level here as its easier to explain. For your own code, please use a async function.

   If you want a example of how it can be done in a async function, see the full example.

Setting up
^^^^^^^^^^^
.. code-block:: python3
    
    from os import environ

    from discord_typings import ChannelData
    from nextcore.http import BotAuthentication, HTTPClient, Route

    # Constants
    AUTHENTICATION = BotAuthentication(environ["TOKEN"])
    CHANNEL_ID = environ["CHANNEL_ID"]

    # HTTP Client
    http_client = HTTPClient()
    await http_client.setup()

.. note::
    You will need to set environment variables on your system for this to work.

    .. tab:: Bash

        .. code-block:: bash

            export TOKEN="..."
            export CHANNEL_ID="..."
    .. tab:: PowerShell
        
        .. code-block:: powershell
            
            $env:TOKEN = "..."
            $env:CHANNEL_ID = "..."

Creating a :class:`Route`
^^^^^^^^^^^^^^^^^^^^^^^^^
First you need to find what route you are going to implement. A list can be found on https://discord.dev

For this example we are going to use `Get Channel <https://discord.dev/resources/channel#get-channel>`__

For the first parameter, this will be the HTTP method.

.. code-block:: python3

   route = Route("GET", ...)

The second parameter is the "route". This is the path of the request, without any parameters included.
To get this, you take the path (``/channels/{channel.id}``) and replace ``.`` with ``_``
It will look something like this.

.. code-block:: python3

   route = Route("GET", "/channels/{channel_id}", ...)

.. warning::
   This should not be a f-string!


The kwargs will be parameters to the path.

.. code-block:: python3

    route = Route("GET", "/channels/{channel_id}", channel_id=1234567890)

Doing the request
^^^^^^^^^^^^^^^^^^
To do a request, you will need to use :meth:`HTTPClient.request`.

.. code-block:: python3

   response = await http_client.request(route,
        rate_limit_key=AUTHENTICATION.rate_limit_key,
        headers={"Authorization": str(AUTHENTICATION)}
   )

This will return a :class:`aiohttp.ClientResponse` for you to process.

Getting the response data
^^^^^^^^^^^^^^^^^^^^^^^^^

We can use :meth:`aiohttp.ClientResponse.json` to get the JSON response data.

.. code-block:: python3

   channel = await response.json()

And finally, get the channel name

.. code-block:: python3

   print(channel.get("name"))  # DM channels do not have names

Cleaning up
^^^^^^^^^^^
When you are finished with all requests, you can close the HTTP client gracefully.

.. code-block:: python3

   await http_client.close()

HTTP reference
--------------
.. autoclass:: HTTPClient
   :members:
   :inherited-members:

.. autoclass:: Route
   :members:

.. autoclass:: RateLimitStorage
   :members:

Authentication
^^^^^^^^^^^^^^^
.. autoclass:: BaseAuthentication
   :members:

.. autoclass:: BotAuthentication
   :members:

.. autoclass:: BearerAuthentication
   :members:


Bucket rate limiting
^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: Bucket
   :members:

.. autoclass:: BucketMetadata
   :members:

.. autoclass:: RequestSession
   :members:

Global rate limiting
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: BaseGlobalRateLimiter
   :members:

.. autoclass:: LimitedGlobalRateLimiter
   :members:

.. autoclass:: UnlimitedGlobalRateLimiter
   :members:

HTTP errors
-----------
.. autoexception:: RateLimitingFailedError
   :members:

.. autoexception:: CloudflareBanError
   :members:

.. autoexception:: HTTPRequestStatusError
   :members:

.. autoexception:: BadRequestError
   :members:

.. autoexception:: NotFoundError
   :members:

.. autoexception:: UnauthorizedError
   :members:

.. autoexception:: ForbiddenError
   :members:

.. autoexception:: InternalServerError
   :members:


Optimizing
==========
Heres a few tips to make your bot run a tiny bit faster, from most impact to least. The accuracy of the ordering is more of a guess, and depends on your usage.

.. Adjust the global rate limit
.. ----------------------------
.. TODO: This needs to be properly supported in HTTPClient first imo.

Relative time
-------------
Nextcore uses your computer's time to work with rate limits.

By default this is on, however your clock might not be syncronized.



.. tab:: Ubuntu

    You can check if your clock is synchronized by running the following command:

    .. code-block:: bash

        timedatectl

    If it is synchronized, it will show "System clock synchronized: yes" and "NTP service: running"

    If the system clock is not synchronized but the ntp service is running you will have to wait a few minutes for it to sync.

    To enable the ntp service run the following command:

    .. code-block:: bash

        sudo timedatectl set-ntp on

    This will automatically sync the system clock every once in a while.

.. tab:: Arch

    You can check if your clock is synchronized by running the following command:

    .. code-block:: bash

        timedatectl

    If it is synchronized, it will show "System clock synchronized: yes" and "NTP service: running"

    If the system clock is not synchronized but the ntp service is running you will have to wait a few minutes for it to sync.

    To enable the ntp service run the following command:

    .. code-block:: bash

        sudo timedatectl set-ntp on

    This will automatically sync the system clock every once in a while.

.. tab:: Windows

    This can be turned on by going to ``Settings -> Time & language -> Date & time`` and turning on ``Set time automatically``.

Switch to ORJSON
----------------
Nextcore handles quite a bit of JSON encoding and decoding.
By default, nextcore uses the :mod:`json` module, which is quite a bit slower than :mod:`orjson`

You can switch to ORJSON by installing the speed package and setting it as the global aiohttp default

.. tab:: Pip

   .. code-block:: bash
      
      pip install "nextcore[speed]"

.. tab:: Poetry

   .. code-block:: bash
        
      poetry add "nextcore[speed]"

This will make :mod:`nextcore.gateway` use orjson, if it is installed.

.. TODO: How do we enable it for nextcore.http too?

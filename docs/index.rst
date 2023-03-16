Welcome to Nextcore's documentation!
====================================

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   http
   gateway
   common

   events
   releasenotes

.. toctree::
   :hidden:

   contributing/getting_started


Quickstart
==========
First, you need to install the library.

.. tab:: Pip

   .. code-block:: shell 

      pip install nextcore

.. tab:: Poetry

   .. code-block:: shell

      poetry add nextcore

The documentation will now split into different pages depending on what functionality you need.

- :ref:`http` Sending requests to discord.
- :ref:`gateway` Receiving events from discord.

.. warning::

   Using :data:`logging.DEBUG` logging may include secrets.


Helping out
=============
We would appriciate your help writing nextcore and related libraries.
See :ref:`contributing` for more info

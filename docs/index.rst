Welcome to Nextcore's documentation!
====================================

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   http
   gateway
   common

   events


Quickstart
==========
First, you need to install the library.

.. tab:: Pip

   .. code-block:: shell 

      pip install nextcore

.. tab:: Poetry

   .. code-block:: shell

      poetry add nextcore

Basic ping-pong example
------------------------
This will respond with ``pong`` every time someone sends ``ping`` in chat.

.. literalinclude:: ../examples/ping_pong.py
   :lines: 28-
   :language: python


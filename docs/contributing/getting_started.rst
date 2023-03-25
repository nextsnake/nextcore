Contributing
=============

Setting up a development environment
--------------------------------------
First, you will need to fork the `repository <https://github.com/nextsnake/nextcore>`__.

Then you will need to setup a ssh-key. See `GitHub's tutorial <https://docs.github.com/en/authentication/connecting-to-github-with-ssh>`__.

.. code-block:: sh

    git clone https://github.com/<your-username>/nextcore

    cd nextcore

    poetry install

    git checkout -b <name-of-what-you-are-changing>

    poetry shell # You will need to run this every time you need access to your development version of nextcore.

We recommend making a "development" folder and adding it to your .git/info/exclude file.

This can be done by making a ``.dev`` folder and appending ``.dev`` to the .git/info/exclude file on a new line.
Every file in the ``.dev`` directory will now be invisible to git.

Submitting your changes
-------------------------
Before submitting we recommend checking a few things

1. You have linted your code. This can be done by running ``task lint``
2. You have checked your code for type errors. This can be done by running ``pyright``

.. hint::
    Pyright needs to be installed. This can be done by using ``npm install --global pyright``

3. Did you remember to write a changelog? See :external+towncrier:doc:`the towncrier tutorial <tutorial>`

Do's and Dont's
----------------
- Do keep your PR scope small. We would rather review many small PRs with seperate features than one giant one.
- Make draft PRs.

Project structure
------------------
Nextcore is currently split into 3 main modules

- nextcore.common
- nextcore.http
- nextcore.gateway

Common is for common utilies that needs to be shared between the other modules.
HTTP is for the REST API.
Gateway is for the WebSocket gateway.

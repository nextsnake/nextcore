# The MIT License (MIT)
# Copyright (c) 2021-present nextcore developers
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


class ReconnectCheckFailedError(Exception):
    def __init__(self) -> None:
        super().__init__("Reconnect check failed. This shard should be considered \"dead\".")

class DisconnectError(Exception):
    """A unexpected disconnect from the gateway happened."""

class InvalidIntentsError(DisconnectError):
    """The intents provided are invalid."""
    def __init__(self) -> None:
        super().__init__("The intents provided are invalid.")

class DisallowedIntentsError(DisconnectError):
    """The intents provided are disallowed."""
    def __init__(self) -> None:
        super().__init__("You can't use intents you are not allowed to use. Enable them in the switches in the developer portal or apply for them.")

class InvalidTokenError(DisconnectError):
    """The token provided is invalid."""
    def __init__(self) -> None:
        super().__init__("The token provided is invalid.")

class InvalidApiVersionError(DisconnectError):
    """The api version provided is invalid."""
    def __init__(self) -> None:
        super().__init__("The api version provided is invalid. This can probably be fixed by updating!")

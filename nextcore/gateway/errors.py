# The MIT License (MIT)
# Copyright (c) 2021-present tag-epic
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

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final

__all__: Final[tuple[str, ...]] = (
    "ReconnectCheckFailedError",
    "DisconnectError",
    "InvalidIntentsError",
    "DisallowedIntentsError",
    "InvalidTokenError",
    "InvalidApiVersionError",
    "InvalidShardCountError",
    "UnhandledCloseCodeError",
)


class ReconnectCheckFailedError(Exception):
    """Error for when auto reconnect is set to False and the shard needs to IDENTIFY"""

    def __init__(self) -> None:
        super().__init__('Reconnect check failed. This shard should be considered "dead".')


class DisconnectError(Exception):
    """A unexpected disconnect from the gateway happened."""


class InvalidIntentsError(DisconnectError):
    """The intents provided are invalid."""

    def __init__(self) -> None:
        super().__init__("The intents provided are invalid.")


class DisallowedIntentsError(DisconnectError):
    """The intents provided are disallowed."""

    def __init__(self) -> None:
        super().__init__(
            "You can't use intents you are not allowed to use. Enable them in the switches in the developer portal or apply for them."
        )


class InvalidTokenError(DisconnectError):
    """The token provided is invalid."""

    def __init__(self) -> None:
        super().__init__("The token provided is invalid.")


class InvalidApiVersionError(DisconnectError):
    """The api version provided is invalid."""

    def __init__(self) -> None:
        super().__init__("The api version provided is invalid. This can probably be fixed by updating!")


class InvalidShardCountError(DisconnectError):
    """The shard count provided is invalid."""

    def __init__(self) -> None:
        super().__init__(
            "The shard count provided is invalid."
            "This can be due to specifying a shard_id larger than shard_count or that the bot needs more shards to connect."
        )


class UnhandledCloseCodeError(DisconnectError):
    """The close code provided is unknown to the library and as such it cannot be handled properly.

    Parameters
    ----------
    code: :class:`int`
        The close code.

    Attributes
    ----------
    code: :class:`int`
        The close code.
    """

    def __init__(self, code: int) -> None:
        self.code: int = code
        super().__init__(f"The close code provided is unhandled: {code}")

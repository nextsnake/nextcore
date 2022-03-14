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

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import ClassVar, Literal


class Route:
    """Metadata about a discord API route

    Parameters
    ----------
    method: :class:`str`
        The HTTP method of the route
    path: :class:`str`
        The path of the route. This can include python formatting strings ({var_here}) from kwargs
    use_webhook_global: :class:`bool`
        Whether or not the route uses the webhook global
    **parameters: :class:`str` | :class:`int`
        The parameters of the route. These will be used to format the path.
        If `guild_id` `channel_id` or `webhook_id` is in the parameters,
        they will be used to change the major parameters of the route.
        This will be included in :attr:`Route.bucket`
    """

    __slots__ = ("method", "route", "path", "ignore_global", "bucket")

    API_VERSION: ClassVar[int] = 10
    BASE_URL: ClassVar[str] = f"https://discord.com/api/v{API_VERSION}"

    def __init__(
        self,
        method: Literal[
            "GET",
            "HEAD",
            "POST",
            "PUT",
            "DELETE",
            "CONNECT",
            "OPTIONS",
            "TRACE",
            "PATCH",
        ],
        path: str,
        *,
        use_webhook_global: bool = False,
        **parameters: str | int,
    ) -> None:
        self.method: str = method
        self.route: str = path
        self.path: str = path.format(**parameters)
        self.ignore_global: bool = use_webhook_global

        # Bucket
        guild_id: str | int | None = parameters.get("guild_id")
        channel_id: str | int | None = parameters.get("channel_id")
        webhook_id: str | int | None = parameters.get("webhook_id")

        self.bucket: str = f"{guild_id}{channel_id}{webhook_id}{path}"

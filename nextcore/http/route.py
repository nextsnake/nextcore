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
    from typing import ClassVar, Final, Literal

    from discord_typings import Snowflake
    from typing_extensions import LiteralString

__all__: Final[tuple[str, ...]] = ("Route",)


class Route:
    """Metadata about a discord API route

    **Example usage**

    .. code-block:: python3

        route = Route("GET", "/guilds/{guild_id}", guild_id=1234567890)

    Parameters
    ----------
    method:
        The HTTP method of the route
    path:
        The path of the route. This can include python formatting strings ({var_here}) from kwargs
    ignore_global:
        If this route bypasses the global rate limit.
    guild_id:
        Major parameters which will be included in ``parameters`` and count towards the rate limit.
    channel_id:
        Major parameters which will be included in ``parameters`` and count towards the rate limit.
    webhook_id:
        Major parameters which will be included in ``parameters`` and count towards the rate limit.
    webhook_token:
        Major parameters which will be included in ``parameters`` and count towards the rate limit.
    parameters:
        The parameters of the route. These will be used to format the path.

        This will be included in :attr:`Route.bucket`

    Attributes
    ----------
    method:
        The HTTP method of the route
    route:
        The path of the route. This can include python formatting strings ({var_here}) from kwargs.
    path:
        The formatted version of :attr:`Route.route`
    ignore_global:
        If this route bypasses the global rate limit.

        This is always :data:`True` for unauthenticated routes.
    bucket:
        The rate limit bucket this fits in.

        This is created from :attr:`Route.guild_id`, :attr:`Route.channel_id`, :attr:`Route.webhook_id`, :attr:`Bucket.method` and :attr:`Route.path`
    """

    __slots__ = ("method", "route", "path", "ignore_global", "bucket")

    BASE_URL: ClassVar[str] = "https://discord.com/api/v10"

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
        path: LiteralString,
        *,
        ignore_global: bool = False,
        guild_id: Snowflake | None = None,
        channel_id: Snowflake | None = None,
        webhook_id: Snowflake | None = None,
        webhook_token: str | None = None,
        **parameters: Snowflake,
    ) -> None:
        self.method: str = method
        self.route: str = path
        self.path: str = path.format(
            guild_id=guild_id, channel_id=channel_id, webhook_id=webhook_id, webhook_token=webhook_token, **parameters
        )
        self.ignore_global: bool = ignore_global

        self.bucket: str = f"{guild_id}{channel_id}{webhook_id}{webhook_token}{method}{path}"

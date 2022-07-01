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
    from typing import ClassVar, Final, Literal

    from discord_typings.shared import Snowflake

__all__: Final[tuple[str, ...]] = ("Route",)


class Route:
    """Metadata about a discord API route

    Parameters
    ----------
    method:
        The HTTP method of the route
    path:
        The path of the route. This can include python formatting strings ({var_here}) from kwargs
    ignore_global:
        If this route bypasses the global ratelimit.
    guild_id:
    channel_id:
    webhook_id:
        Major parameters which will be included in ``parameters`` and count towards the ratelimit.
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
        If this route bypasses the global ratelimit.

        This is always :data:`True` for unauthenticated routes.
    bucket:
        The ratelimit bucket this fits in.

        This is created from :attr:`Route.guild_id`, :attr:`Route.channel_id`, :attr:`Route.webhook_id`, :attr:`Bucket.method` and :attr:`Route.path`

        .. note::
            This will be :class:`int` if :data:`__debug__` is :data:`True`
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
        path: str,
        *,
        ignore_global: bool = False,
        guild_id: Snowflake | None = None,
        channel_id: Snowflake | None = None,
        webhook_id: Snowflake | None = None,
        **parameters: Snowflake,
    ) -> None:
        self.method: str = method
        self.route: str = path
        self.path: str = path.format(guild_id=guild_id, channel_id=channel_id, webhook_id=webhook_id, **parameters)
        self.ignore_global: bool = ignore_global

        self.bucket: str | int = f"{guild_id}{channel_id}{webhook_id}{method}{path}"

        if not __debug__:
            self.bucket = hash(self.bucket)

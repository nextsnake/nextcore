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

from abc import ABC
from typing import TYPE_CHECKING, overload

from ....common import UNDEFINED, UndefinedType
from ...route import Route
from ..abstract_client import AbstractHTTPClient

if TYPE_CHECKING:
    from typing import Final

    from discord_typings import AuditLogData, Snowflake
    from discord_typings.resources.audit_log import AuditLogEvents

    from ...authentication import BotAuthentication

__all__: Final[tuple[str, ...]] = ("AuditLogHTTPWrappers",)


class AuditLogHTTPWrappers(AbstractHTTPClient, ABC):
    """HTTP wrappers for audit log API endpoints.

    This is an abstract base class that should not be used directly.
    """

    __slots__ = ()

    @overload
    async def get_guild_audit_log(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        user_id: int | UndefinedType = UNDEFINED,
        action_type: AuditLogEvents | UndefinedType = UNDEFINED,
        before: UndefinedType = UNDEFINED,
        after: int,
        limit: int | UndefinedType = UNDEFINED,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
    ) -> AuditLogData:
        ...

    @overload
    async def get_guild_audit_log(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        user_id: int | UndefinedType = UNDEFINED,
        action_type: AuditLogEvents | UndefinedType = UNDEFINED,
        before: int,
        after: UndefinedType = UNDEFINED,
        limit: int | UndefinedType = UNDEFINED,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
    ) -> AuditLogData:
        ...

    @overload
    async def get_guild_audit_log(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        user_id: int | UndefinedType = UNDEFINED,
        action_type: AuditLogEvents | UndefinedType = UNDEFINED,
        before: UndefinedType = UNDEFINED,
        after: UndefinedType = UNDEFINED,
        limit: int | UndefinedType = UNDEFINED,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
    ) -> AuditLogData:
        ...

    async def get_guild_audit_log(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        user_id: int | UndefinedType = UNDEFINED,
        action_type: AuditLogEvents | UndefinedType = UNDEFINED,
        before: int | UndefinedType = UNDEFINED,
        after: int | UndefinedType = UNDEFINED,
        limit: int | UndefinedType = UNDEFINED,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
    ) -> AuditLogData:
        """Gets the guild audit log.

        Read the `documentation <https://discord.dev/resources/audit-log#get-guild-audit-log>`__

        .. note::
            This requires the ``VIEW_AUDIT_LOG`` permission.

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The guild to query the audit log for.
        user_id:
            The user to filter the audit log by.

            This will be the user that did the action if present, if not it will be the user that got actioned.
        action_type:
            The action type to filter the audit log by.
        before:
            Get entries before this entry.

            .. note::
                This does not have to be a valid entry id.
        after:
            Get entries before after entry.

            .. note::
                This does not have to be a valid entry id.
        limit:
            The amount of entries to get.

            .. note::
                This has a minimum of 1 and a maximum of 100.

            .. note::
                This defaults to 50.
        global_priority:
            The priority of the request for the global rate-limiter.
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`.
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        ForbiddenError
            You do not have the ``VIEW_AUDIT_LOG`` permission

        Returns
        -------
        AuditLogData
            The guild audit log.

            .. hint::
                A list of fields are available in the documentation.
        """
        route = Route("GET", "/guilds/{guild_id}/audit-logs", guild_id=guild_id)
        params: dict[str, str] = {}

        # They are NotRequired but can't be None.
        # This converts None to NotRequired
        if user_id is not UNDEFINED:
            params["user_id"] = str(user_id)
        if action_type is not UNDEFINED:
            params["action_type"] = str(action_type)
        if before is not UNDEFINED:
            params["before"] = str(before)
        if after is not UNDEFINED:
            params["after"] = str(before)
        if limit is not UNDEFINED:
            params["limit"] = str(limit)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            params=params,
            headers={"Authorization": str(authentication)},
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

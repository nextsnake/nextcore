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
from typing import TYPE_CHECKING

from ....common import UNDEFINED, UndefinedType
from ...route import Route
from ..abstract_client import AbstractHTTPClient

if TYPE_CHECKING:
    from typing import Any, Final

    from discord_typings import (
        DMChannelData,
        GuildData,
        GuildMemberData,
        Snowflake,
        UserData,
    )

    from ...authentication import BearerAuthentication, BotAuthentication

__all__: Final[tuple[str, ...]] = ("UserHTTPWrappers",)


class UserHTTPWrappers(AbstractHTTPClient, ABC):
    """HTTP wrappers for user API endpoints.

    This is an abstract base class that should not be used directly.
    """

    __slots__ = ()

    async def get_current_user(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
    ) -> UserData:
        """Gets the current user

        Read the `documentation <https://discord.dev/resources/user#get-current-user>`__

        .. note::
            If you are using :class:`BearerAuthentication` you need the ``IDENTIFY`` scope.

            :attr:`UserData.email` will only be provided if you have the ``EMAIL`` scope.

        Parameters
        ----------
        authentication:
            Authentication info.
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
            You are rate limited, and ``wait`` was set to :data:`False`

        Returns
        -------
        discord_typings.UserData
            The current user
        """
        route = Route("GET", "/users/@me")

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_user(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        user_id: Snowflake,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
    ) -> UserData:
        """Gets a user by id

        Read the `documentation <https://discord.dev/resources/user#get-user>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        user_id:
            The id of the user to fetch
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
            You are rate limited, and ``wait`` was set to :data:`False`
        Returns
        -------
        discord_typings.UserData
            The user you fetched
        """
        route = Route("GET", "/users/{user_id}", user_id=user_id)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_current_user(
        self,
        authentication: BotAuthentication,
        *,
        username: str | UndefinedType = UNDEFINED,
        avatar: str | UndefinedType = UNDEFINED,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
    ) -> UserData:
        """Modifies the current user

        Read the `documentation <https://discord.dev/resources/user#modify-current-user>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        username:
            The username to update to
        avatar:
            Base64 encoded image to change the current users avatar to
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
            You are rate limited, and ``wait`` was set to :data:`False`

        Returns
        -------
        discord_typings.UserData
            The updated user
        """
        route = Route("PATCH", "/users/@me")

        payload: dict[str, Any] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if username is not UNDEFINED:
            payload["username"] = username
        if avatar is not UNDEFINED:
            payload["avatar"] = avatar

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_current_user_guilds(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        *,
        before: Snowflake | UndefinedType = UNDEFINED,
        after: Snowflake | UndefinedType = UNDEFINED,
        limit: int | UndefinedType = UNDEFINED,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
    ) -> list[GuildData]:  # TODO: Replace with partial guild data
        """Gets the guilds the current user is in

        Read the `documentation <https://discord.dev/resources/user#get-current-user-guilds>`__

        .. note::
            If you are using :class:`BearerAuthentication` you need the ``guilds`` scope.

        Parameters
        ----------
        authentication:
            Authentication info.
        before:
            Get guilds before this id

            .. note::
                This does not have to be a valid id.
        after:
            Get guilds after this id

            .. note::
                This does not have to be a valid id.
        limit:
            The max amount of guilds to return

            .. note::
                This has to be between ``1`` and ``200``
            .. note::
                This defaults to ``200``
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
            You are rate limited, and ``wait`` was set to :data:`False`

        Returns
        -------
        list[discord_typings.PartialGuildData]
            The guilds fetched
        """
        route = Route("GET", "/users/@me/guilds")

        params = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if before is not UNDEFINED:
            params["before"] = before
        if after is not UNDEFINED:
            params["after"] = after
        if limit is not UNDEFINED:
            params["limit"] = limit

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            params=params,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_current_user_guild_member(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        guild_id: Snowflake,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
    ) -> GuildMemberData:
        """Gets the current users member in a guild

        Read the `documentation <https://discord.dev/resources/user#get-current-user-guild-member>`__

        .. note::
            This requires the ``guilds.members.read`` scope

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of the guild to get the member in
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
            You are rate limited, and ``wait`` was set to :data:`False`

        Returns
        -------
        discord_typings.GuildMemberData
            The current member
        """
        route = Route("GET", "/users/@me/guilds/{guild_id}/member", guild_id=guild_id)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def leave_guild(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
    ) -> None:
        """Leave a guild

        Read the `documentation <https://discord.dev/resources/user#leave-guild>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of the guild to leave
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
            You are rate limited, and ``wait`` was set to :data:`False`

        Returns
        -------
        discord_typings.UserData
            The current user
        """
        route = Route("DELETE", "/users/@me/guilds/{guild_id}", guild_id=guild_id)

        await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

    async def create_dm(
        self,
        authentication: BotAuthentication,
        recipient_id: Snowflake,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
    ) -> DMChannelData:
        """Creates a DM channel

        Read the `documentation <https://discord.dev/resources/user#create-dm>`__

        .. warning::
            You should not use this endpoint to DM everyone in a server about something. DMs should generally be initiated by a user action.

            If you open a significant amount of DMs too quickly, your bot may be blocked from opening new ones.

        Parameters
        ----------
        authentication:
            Authentication info.
        recipient_id:
            The id of user to DM.
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
            You are rate limited, and ``wait`` was set to :data:`False`

        Returns
        -------
        discord_typings.DMChannelData
            The DM channel created/fetched.
        """
        route = Route("POST", "/users/@me/channels")

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            json={"recipient_id": recipient_id},
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Add Create Group DM

    async def get_user_connections(
        self,
        authentication: BearerAuthentication,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
    ) -> list[dict[str, Any]]:  # TODO: This should be more strict
        """Gets the users connections

        Read the `documentation <https://discord.dev/resources/user#get-user-connections>`__

        .. note::
            This requires the ``connections`` scope

        Parameters
        ----------
        authentication:
            Authentication info.
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
            You are rate limited, and ``wait`` was set to :data:`False`

        Returns
        -------
        discord_typings.GuildMemberData
            The current member
        """
        route = Route("GET", "/users/@me/connections")

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

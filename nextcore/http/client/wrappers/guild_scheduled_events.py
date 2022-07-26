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

from typing import TYPE_CHECKING, overload

from ....common import UNDEFINED, UndefinedType
from ...route import Route
from ..abstract_client import AbstractHTTPClient


if TYPE_CHECKING:
    from typing import Any, Final, Literal

    from discord_typings import (
        GuildScheduledEventData,
        GuildScheduledEventEntityMetadata,
        Snowflake,
    )

    from ...authentication import BearerAuthentication, BotAuthentication

__all__: Final[tuple[str, ...]] = ("GuildScheduledEventHTTPWrappers",)


class GuildScheduledEventHTTPWrappers(AbstractHTTPClient):
    async def list_scheduled_events_for_guild(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        with_user_count: bool | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> list[GuildScheduledEventData]:  # TODO: Narrow type more with a overload with_user_count
        """Gets all scheduled events for a guild

        Read the `documentation <https://discord.dev/resources/guild-scheduled-event#list-scheduled-events-for-guild>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of guild scheduled events from
        with_user_count:
            Include :attr:`discord_typings.GuildScheduledEventData.user_count`
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("GET", "/guilds/{guild_id}/scheduled-events", guild_id=guild_id)

        query = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if with_user_count is not UNDEFINED:
            query["with_user_count"] = with_user_count

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            rate_limit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    @overload
    async def create_guild_scheduled_event(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        name: str,
        privacy_level: Literal[2],
        scheduled_start_time: str,
        entity_type: Literal[3],
        *,
        entity_metadata: GuildScheduledEventEntityMetadata,
        scheduled_end_time: str,
        description: str | UndefinedType = UNDEFINED,
        image: str | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> GuildScheduledEventData:
        ...

    @overload
    async def create_guild_scheduled_event(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        name: str,
        privacy_level: Literal[2],
        scheduled_start_time: str,
        entity_type: Literal[1, 2],
        *,
        channel_id: Snowflake,
        scheduled_end_time: str | UndefinedType = UNDEFINED,
        description: str | UndefinedType = UNDEFINED,
        image: str | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> GuildScheduledEventData:
        ...

    async def create_guild_scheduled_event(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        name: str,
        privacy_level: Literal[2],
        scheduled_start_time: str,
        entity_type: Literal[1, 2, 3],
        *,
        channel_id: Snowflake | None | UndefinedType = UNDEFINED,
        entity_metadata: GuildScheduledEventEntityMetadata | UndefinedType = UNDEFINED,
        scheduled_end_time: str | UndefinedType = UNDEFINED,
        description: str | UndefinedType = UNDEFINED,
        image: str | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> GuildScheduledEventData:
        """Create a scheduled event

        Read the `documentation <https://discord.dev/resources/guild-scheduled-event#create-guild-scheduled-event>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of guild to create the scheduled event in
        name:
            The name of the event
        privacy_level:
            Who can join the event

            .. note::
                This can currently only be ``2``
        scheduled_start_time:
            A ISO8601 timestamp of when the event should start
        entity_type:
            What the event points to.

            **Types:**
            - ``1``: A stage channel
            - ``2`` A voice channnel
            - ``3`` A external link
        channel_id:
            The channel the event is for
        entity_metadata:
            Metadata about the event spesific to what ``entity_type`` you chose.
        scheduled_end_time:
            A ISO8601 timestamp of when the event ends.
        description:
            The description of the event.
        image:
            A base64 encoded image to use as a cover.
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.GuildScheduledEventData
            The scheduled event that was created
        """
        route = Route("POST", "/guilds/{guild_id}/scheduled-events", guild_id=guild_id)

        payload: dict[str, Any] = {
            "name": name,
            "privacy_level": privacy_level,
            "scheduled_start_time": scheduled_start_time,
            "entity_type": entity_type,
        }

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if channel_id is not UNDEFINED:
            payload["channel_id"] = channel_id
        if entity_metadata is not UNDEFINED:
            payload["entity_metadata"] = entity_metadata
        if scheduled_end_time is not UNDEFINED:
            payload["scheduled_end_time"] = scheduled_end_time
        if description is not UNDEFINED:
            payload["description"] = description
        if image is not UNDEFINED:
            payload["image"] = image

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            headers=headers,
            json=payload,
            rate_limit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_scheduled_event(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        guild_scheduled_event_id: Snowflake,
        *,
        with_user_count: bool | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> GuildScheduledEventData:  # TODO: Narrow type more with a overload with_user_count
        """Gets a scheduled event by id

        Read the `documentation <https://discord.dev/resources/guild-scheduled-event#get-guild-scheduled-event>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of guild scheduled events from
        guild_scheduled_event_id:
            The id of the event to get.
        with_user_count:
            Include :attr:`discord_typings.GuildScheduledEventData.user_count`
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "GET",
            "/guilds/{guild_id}/scheduled-events/{guild_scheduled_event_id}",
            guild_id=guild_id,
            guild_scheduled_event_id=guild_scheduled_event_id,
        )

        query = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if with_user_count is not UNDEFINED:
            query["with_user_count"] = with_user_count

        r = await self._request(
            route,
            headers={"Authorization": str(authentication)},
            rate_limit_key=authentication.rate_limit_key,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Add Modify Guild Scheduled Event

    async def delete_guild_scheduled_event(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        guild_id: Snowflake,
        guild_scheduled_event_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Deletes scheduled event.

        Read the `documentation <https://discord.dev/resources/guild-scheduled-event#delete-guild-scheduled-event>`__

        .. note::
            This requires the ``MANAGE_EVENTS`` guild permission.

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of the guild where the scheduled event is in
        guild_scheduled_event_id:
            The id of the event to delete.
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route(
            "DELETE",
            "/guilds/{guild_id}/scheduled-events/{guild_scheduled_event_id}",
            guild_id=guild_id,
            guild_scheduled_event_id=guild_scheduled_event_id,
        )
        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        await self._request(
            route, headers=headers, rate_limit_key=authentication.rate_limit_key, global_priority=global_priority
        )

    # TODO: Add Get Guild Scheduled Event Users

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

from ....common import UNDEFINED, UndefinedType
from ...route import Route
from ..base_client import BaseHTTPClient

if TYPE_CHECKING:
    from typing import Any, Final, Literal

    from discord_typings import Snowflake, StageInstanceData

    from ...authentication import BotAuthentication

__all__: Final[tuple[str, ...]] = ("StageInstanceHTTPWrappers",)


class StageInstanceHTTPWrappers(BaseHTTPClient):
    async def create_stage_instance(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        topic: str,
        *,
        privacy_level: Literal[1, 2] | UndefinedType = UNDEFINED,
        send_start_notification: bool | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> StageInstanceData:
        """Creates a stage instance

        Read the `documentation <https://discord.dev/resources/stage-instance#create-stage-instance>`__

        .. note::
            This requires the ``MANAGE_CHANNELS``, ``MUTE_MEMBERS`` and ``MOVE_MEMBERS`` permission.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the stage channel to create a stage instance in
        topic:
            The topic of the stage instance

            .. note::
                This has to be between ``1`` and ``120`` characters.
        privacy_level:
            The privacy level of the stage instance.

            .. note::
                This will default to ``2``/Guild only if not provided.

            **Possible values**
            - ``1``: Public (deprecated)
            - ``2`` Guild only
        send_start_notification:
            If you should send a notification to all members in the guild

            .. note::
                Setting this to :data:`True` requires the ``MENTION_EVERYONE`` permission.
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.StageInstanceData
            The stage instance that was created.
        """
        route = Route("POST", "/stage-instances")

        payload: dict[str, Any] = {"channel_id": channel_id, "topic": topic}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if privacy_level is not UNDEFINED:
            payload["privacy_level"] = privacy_level
        if send_start_notification is not UNDEFINED:
            payload["send_start_notification"] = send_start_notification

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers=headers,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_stage_instance(
        self, authentication: BotAuthentication, channel_id: Snowflake, *, global_priority: int = 0
    ) -> StageInstanceData:
        """Gets a stage instance from a stage channel id

        Read the `documentation <https://discord.dev/resources/stage-instance#get-stage-instance>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The code of the invite to get
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.StageInstanceData
            The stage instance that was fetched.
        """
        route = Route("GET", "/stage-instances/{channel_id}", channel_id=channel_id)
        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_stage_instance(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        *,
        topic: str | UndefinedType = UNDEFINED,
        privacy_level: Literal[1, 2] | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> StageInstanceData:
        """Modifies a stage instance

        Read the `documentation <https://discord.dev/resources/stage-instance#modify-stage-instance>`__

        .. note::
            This requires the ``MANAGE_CHANNELS``, ``MUTE_MEMBERS`` and ``MOVE_MEMBERS`` permission.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the stage channel to modify a stage instance in
        topic:
            The topic of the stage instance

            .. note::
                This has to be between ``1`` and ``120`` characters.
        privacy_level:
            The privacy level of the stage instance.

            **Possible values**
            - ``1``: Public (deprecated)
            - ``2`` Guild only
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.StageInstanceData
            The updated stage instance
        """
        route = Route("PATCH", "/stage-instances/{channel_id}", channel_id=channel_id)

        payload: dict[str, Any] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if topic is not UNDEFINED:
            payload["topic"] = topic
        if privacy_level is not UNDEFINED:
            payload["privacy_level"] = privacy_level

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers=headers,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_stage_instance(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Modifies a stage instance

        Read the `documentation <https://discord.dev/resources/stage-instance#delete-stage-instance>`__

        .. note::
            This requires the ``MANAGE_CHANNELS``, ``MUTE_MEMBERS`` and ``MOVE_MEMBERS`` permission.

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the stage channel to delete the stage instance for.
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("DELETE", "/stage-instances/{channel_id}", channel_id=channel_id)

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers=headers,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

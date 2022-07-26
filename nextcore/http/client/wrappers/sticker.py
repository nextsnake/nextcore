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
from ..abstract_client import AbstractHTTPClient


if TYPE_CHECKING:
    from typing import Any, Final, Literal

    from discord_typings import Snowflake, StickerData, StickerPackData

    from ...authentication import BotAuthentication

__all__: Final[tuple[str, ...]] = ("StickerHTTPWrappers",)


class StickerHTTPWrappers(AbstractHTTPClient):
    async def get_sticker(
        self, authentication: BotAuthentication, sticker_id: Snowflake, *, global_priority: int = 0
    ) -> StickerData:
        """Gets a sticker from a sticker id.

        Read the `documentation <https://discord.dev/resources/sticker#get-sticker>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        sticker_id:
            The id of the sticker to get.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.StickerData
            The sticker that was fetched
        """
        route = Route("GET", "/stickers/{sticker_id}", sticker_id=sticker_id)
        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def list_nitro_sticker_packs(
        self, *, global_priority: int = 0
    ) -> dict[Literal["sticker_packs"], list[StickerPackData]]:
        """Gets all nitro sticker packs

        Read the `documentation <https://discord.dev/resources/sticker#list-nitro-sticker-packs>`__

        Parameters
        ----------
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("GET", "/sticker-packs")
        r = await self._request(
            route,
            rate_limit_key=None,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def list_guild_stickers(
        self, authentication: BotAuthentication, guild_id: Snowflake, *, global_priority: int = 0
    ) -> list[StickerData]:
        """Gets all custom stickers added by a guild

        Read the `documentation <https://discord.dev/resources/sticker#list-guild-stickers>`__

        .. note::
            The ``user`` field will be provided if you have the ``MANAGE_EMOJIS_AND_STICKERS`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of guild to get stickers from
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[discord_typings.StickerData]
            The stickers in the guild
        """
        route = Route("GET", "/guilds/{guild_id}/stickers", guild_id=guild_id)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_sticker(
        self, authentication: BotAuthentication, guild_id: Snowflake, sticker_id: str | int, *, global_priority: int = 0
    ) -> StickerData:
        """Get a custom sticker

        Read the `documentation <https://discord.dev/resources/sticker#get-guild-sticker>`__

        .. note::
            The ``user`` field will be provided if you have the ``MANAGE_EMOJIS_AND_STICKERS`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of guild to get the sticker from
        sticker_id:
            The sticker to get
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[discord_typings.StickerData]
            The stickers in the guild
        """
        route = Route("GET", "/guilds/{guild_id}/stickers/{sticker_id}", guild_id=guild_id, sticker_id=sticker_id)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Add create guild sticker

    async def modify_guild_sticker(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        sticker_id: Snowflake,
        *,
        name: str | UndefinedType = UNDEFINED,
        description: str | UndefinedType = UNDEFINED,
        tags: list[str] | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> StickerData:  # TODO: Make StickerData always include user
        """Modifies a sticker

        Read the `documentation <https://discord.dev/resources/sticker#modify-guild-sticker>`__

        .. note::
            This requires the ``MANAGE_EMOJIS_AND_STICKERS`` permission.

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of the guild where the sticker is in.
        sticker_id:
            The id of the sticker to update
        name:
            The name of the sticker.

            .. note::
                This has to be between ``2`` and ``30`` characters
        description:
            The description of the sticker

            .. note::
                This has to be between ``2`` and ``100`` characters
        tags:
            Autocomplete/suggestion tags for the sticker (max 200 characters)
        reason:
            The reason to put in audit log
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.StageInstanceData
            The updated stage instance
        """
        route = Route("PATCH", "/guilds/{guild_id}/stickers/{sticker_id}", guild_id=guild_id, sticker_id=sticker_id)

        payload: dict[str, Any] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name
        if description is not UNDEFINED:
            payload["description"] = description
        if tags is not UNDEFINED:
            payload["tags"] = tags

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

    async def delete_guild_sticker(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        sticker_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Modifies a stage instance

        Read the `documentation <https://discord.dev/resources/sticker#delete-guild-sticker>`__

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
        route = Route("DELETE", "/guilds/{guild_id}/stickers/{sticker_id}", guild_id=guild_id, sticker_id=sticker_id)

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

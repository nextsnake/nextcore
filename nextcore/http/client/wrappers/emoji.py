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
    from typing import Any, Final

    from discord_typings import EmojiData, Snowflake

    from ...authentication import BotAuthentication

__all__: Final[tuple[str, ...]] = ("EmojiHTTPWrappers",)


class EmojiHTTPWrappers(AbstractHTTPClient):
    async def list_guild_emojis(
        self, authentication: BotAuthentication, guild_id: Snowflake, *, global_priority: int = 0
    ) -> list[EmojiData]:
        """List all emojis in a guild.

        Read the `documentation <https://discord.dev/resources/emoji#list-guild-emojis>`__

        Parameters
        ----------
        authentication:
            Auth info
        guild_id:
            The guild to list emojis from
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("GET", "/guilds/{guild_id}/emojis", guild_id=guild_id)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_emoji(
        self, authentication: BotAuthentication, guild_id: Snowflake, emoji_id: int | str, *, global_priority: int = 0
    ) -> list[EmojiData]:
        """Get emoji info

        Read the `documentation <https://discord.dev/resources/emoji#get-guild-emoji>`__

        Parameters
        ----------
        authentication:
            Auth info
        guild_id:
            The guild to get the emoji from
        emoji_id:
            The emoji to get
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("GET", "/guilds/{guild_id}/emojis/{emoji_id}", guild_id=guild_id, emoji_id=emoji_id)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Add create guild emoji here

    async def modify_guild_emoji(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        emoji_id: Snowflake,
        *,
        name: str | UndefinedType = UNDEFINED,
        roles: list[Snowflake] | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> EmojiData:
        """Modify a emoji

        Read the `documentation <https://discord.dev/resources/emoji#modify-guild-emoji>`__

        .. note::
            This requires the ``MANAGE_EMOJIS_AND_STICKERS`` permission.
        .. note::
            This dispatches a ``GUILD_EMOJIS_UPDATE`` event.

        Parameters
        ----------
        authentication:
            The auth info
        guild_id:
            The guild where the emoji is in
        emoji_id:
            The emoji to modify
        name:
            The emoji name.
        roles:
            IDs of roles that can use this emoji.
        reason:
            Reason to show in audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """

        route = Route("PATCH", "/guilds/{guild_id}/emojis/{emoji_id}", guild_id=guild_id, emoji_id=emoji_id)

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        payload: dict[str, Any] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name
        if roles is not UNDEFINED:
            payload["roles"] = roles

        r = self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers=headers,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

    async def delete_guild_emoji(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        emoji_id: int | str,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> list[EmojiData]:
        """Delete a emoji

        Read the `documentation <https://discord.dev/resources/emoji#delete-guild-emoji>`__

        .. note::
            This requires the ``MANAGE_EMOJIS_AND_STICKERS`` permission.

        .. note::
            This dispatches a ``GUILD_EMOJIS_UPDATE`` event.

        Parameters
        ----------
        authentication:
            Auth info
        guild_id:
            The guild to get the emoji from
        emoji_id:
            The emoji to get
        reason:
            The reason to put in the audit log
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route("DELETE", "/guilds/{guild_id}/emojis/{emoji_id}", guild_id=guild_id, emoji_id=emoji_id)

        headers = {"Authorization": str(authentication)}

        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the data from Discord
        return await r.json()  # type: ignore [no-any-return]

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
    from typing import Any, Final

    from discord_typings import GuildData, GuildTemplateData, Snowflake

    from ...authentication import BotAuthentication

__all__: Final[tuple[str, ...]] = ("GuildTemplateHTTPWrappers",)


class GuildTemplateHTTPWrappers(BaseHTTPClient):
    async def get_guild_template(
        self, authentication: BotAuthentication, template_code: str, *, global_priority: int = 0
    ) -> GuildTemplateData:
        """Gets a template by code

        Read the `documentation <https://discord.dev/resources/guild-template#get-guild-templates>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        template_code:
            The template code to get the template from
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.GuildTemplateData
            The template you requested
        """
        route = Route("GET", "/guilds/templates/{template_code}", template_code=template_code)
        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def create_guild_from_guild_template(
        self,
        authentication: BotAuthentication,
        template_code: str,
        name: str,
        *,
        icon: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> GuildData:
        """Creates a guild from a template

        Read the `documentation <https://discord.dev/resources/guild-template#create-guild-from-guild-template>`__

        .. warning::
            This will fail if the bot is in more than 10 guilds.

        Parameters
        ----------
        authentication:
            Authentication info.
        template_code:
            The template code to create the guild from
        name:
            The name of the guild
        icon:
            Base64 encoded 128x128px image to set the guild icon to.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.GuildData
            The guild created
        """
        route = Route("POST", "/guilds/templates/{template_code}", template_code=template_code)

        payload: dict[str, Any] = {"name": name}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if icon is not UNDEFINED:
            payload["icon"] = icon

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_templates(
        self, authentication: BotAuthentication, guild_id: Snowflake, *, global_priority: int = 0
    ) -> list[GuildTemplateData]:
        """Gets all templates in a guild

        Read the `documentation <https://discord.dev/resources/guild-template#get-guild-templates>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The guild id to get templates from
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[:class:`discord_typings.GuildTemplateData`]
            The templates in the guild
        """
        route = Route("GET", "/guilds/{guild_id}/templates", guild_id=guild_id)
        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def create_guild_template(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        name: str,
        *,
        description: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> GuildTemplateData:  # TODO: Narrow typing to overload description.
        """Creates a template from a guild

        Read the `documentation <https://discord.dev/resources/guild-template#create-guild-template>`__

        .. note::
            This requires the ``MANAGE_GUILD`` permission


        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The guild to create a template from
        name:
            The name of the template

            .. note::
                This has to be between ``2`` and ``100`` characters long.
        description:
            The description of the template

            .. note::
                This has to be between ``0`` and ``120`` characters long.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.GuildData
            The guild created
        """
        route = Route("POST", "/guilds/{guild_id}/templates", guild_id=guild_id)

        payload: dict[str, Any] = {"name": name}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if description is not UNDEFINED:
            payload["description"] = description

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def sync_guild_template(
        self, authentication: BotAuthentication, guild_id: Snowflake, template_code: str, *, global_priority: int = 0
    ) -> None:
        """Updates a template with the updated-guild.

        Read the `documentation <https://discord.dev/resources/guild-template#sync-guild-templates>`__

        .. note::
            This requires the ``MANAGE_GUILD`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The guild id of the template
        template_code:
            The template to sync
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "PUT", "/guilds/{guild_id}/templates/{template_code}", guild_id=guild_id, template_code=template_code
        )

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_guild_template(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        template_code: str,
        *,
        name: str | UndefinedType = UNDEFINED,
        description: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Updates a template.

        Read the `documentation <https://discord.dev/resources/guild-template#modify-guild-templates>`__

        .. note::
            This requires the ``MANAGE_GUILD`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The guild id of the template
        template_code:
            The code of the template to modify
        name:
            What to change the template name to

            .. note::
                This has to be between ``2`` and ``100`` characters long.
        description:
            What to change the template description to.

            .. note::
                This has to be between ``0`` and ``120`` characters long.
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "PATCH", "/guilds/{guild_id}/templates/{template_code}", guild_id=guild_id, template_code=template_code
        )

        payload: dict[str, Any] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name
        if description is not UNDEFINED:
            payload["description"] = description

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_guild_template(
        self, authentication: BotAuthentication, guild_id: Snowflake, template_code: str, *, global_priority: int = 0
    ) -> GuildTemplateData:
        """Deletes a template

        Read the `documentation <https://discord.dev/resources/guild-template#delete-guild-template>`__

        .. note::
            This requires the ``MANAGE_GUILD`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The guild id where the template is located
        template_code:
            The code of the template to delete
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.GuildTemplateData
            The deleted template
        """
        route = Route(
            "DELETE", "/guilds/{guild_id}/templates/{template_code}", guild_id=guild_id, template_code=template_code
        )

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

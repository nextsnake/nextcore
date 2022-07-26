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
from logging import getLogger
from typing import TYPE_CHECKING

from ....common import UNDEFINED, UndefinedType
from ...route import Route
from ..abstract_client import AbstractHTTPClient

if TYPE_CHECKING:
    from typing import Any, Final, Literal

    from discord_typings import (
        ApplicationCommandData,
        ApplicationCommandOptionData,
        ApplicationCommandPayload,
        GuildApplicationCommandPermissionData,
        MessageData,
        Snowflake,
    )
    from discord_typings.interactions.commands import Locales

    from ...authentication import BearerAuthentication, BotAuthentication

logger = getLogger(__name__)

__all__: Final[tuple[str, ...]] = ("ApplicationCommandsHTTPWrappers",)


class ApplicationCommandsHTTPWrappers(AbstractHTTPClient, ABC):
    """HTTP wrappers for application commands API endpoints.

    This is an abstract base class that should not be used directly.
    """

    __slots__ = ()

    async def get_global_application_commands(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        *,
        with_localizations: bool | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> list[ApplicationCommandData]:  # TODO: Narrow typing to never include guild_id and localization overload
        """Gets all global commands

        Read the `documentation <https://discord.dev/interactions/application-commands#get-global-application-commands>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        global_priority:
            The priority of the request for the global rate-limiter.

        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided

        Returns
        -------
        list[discord_typings.ApplicationCommandData]
            The global commmands registered to the application
        """
        route = Route("GET", "/applications/{application_id}/commands", application_id=application_id)

        query = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if with_localizations is not UNDEFINED:
            query["with_localizations"] = with_localizations

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            query=query,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def create_global_application_command(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        name: str,
        description: str,
        *,
        name_localizations: dict[Locales, str] | None | UndefinedType = UNDEFINED,
        description_localizations: dict[Locales, str] | None | UndefinedType = UNDEFINED,
        options: list[ApplicationCommandOptionData] | UndefinedType = UNDEFINED,
        default_member_permissions: str | None | UndefinedType = UNDEFINED,
        dm_permission: bool | None | UndefinedType = UNDEFINED,
        type: Literal[1, 2, 3] | UndefinedType = UNDEFINED,  # TODO: Replace this with a type alias in discord_typings
        global_priority: int = 0,
    ) -> ApplicationCommandData:  # TODO: Narrow typing to never include guild_id
        """Creates or updates a global application command

        Read the `documentation <https://discord.dev/interactions/application-commands#create-global-application-command>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only update commands for your current application
        name:
            The name of the command

            .. note::
                If the name is already taken by a existing application command with the same name and type
                it will update the exisiting command.
            .. note::
                This has to be between 1-32 characters long and follow the `naming conventions <https://discord.dev/interactions/application-commands#application-command-object-application-command-naming>`__
        description:
            The description of the command

            .. note::
                This has to be between 1-100 characters long

            .. warning::
                Some special characters may be automatically removed from this!
        name_localizations:
            The localizations for the name

            .. note::
                This has to be between 1-32 characters long and follow the `naming conventions <https://discord.dev/interactions/application-commands#application-command-object-application-command-naming>`__
        description_localizations:
            The localizations for the description

            .. note::
                This has to be between 1-100 characters long

            .. warning::
                Some special characters may be automatically removed from this!
        options:
            The parameters or sub-commands of the command

            .. note::
                This should only be provide
        default_member_permissions:
            The default permissions to require to use the command
        dm_permission:
            Whether the command can be used in DMs.

            .. note::
                If this is :data:`UNDEFINED`, it defaults to :data:`True`.
        type:
            The type of the command

            .. note::
                This defaults to ``1`` if it is :data:`UNDEFINED`.

            **Possible values**
            - ``1``: Slash/text command
            - ``2``: User context menu
            - ``3``: Message context menu
        global_priority:
            The priority of the request for the global rate-limiter.

        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        BadRequestError
            You did not follow the requirements for some of the fields.

        Returns
        -------
        discord_typings.ApplicationCommandData
            The command that was created
        """
        route = Route("POST", "/applications/{application_id}/commands", application_id=application_id)

        payload: dict[str, Any] = {"name": name, "description": description}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name_localizations is not UNDEFINED:
            payload["name_localizations"] = name_localizations
        if description_localizations is not UNDEFINED:
            payload["description_localizations"] = description_localizations
        if options is not UNDEFINED:
            payload["options"] = options
        if default_member_permissions is not UNDEFINED:
            payload["default_member_permissions"] = default_member_permissions
        if dm_permission is not UNDEFINED:
            payload["dm_permission"] = dm_permission
        if type is not UNDEFINED:
            payload["type"] = type

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_global_application_command(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        command_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> ApplicationCommandData:  # TODO: Narrow typing to never include guild_id
        """Gets a global command

        Read the `documentation <https://discord.dev/interactions/application-commands#get-global-application-command>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        application_id:
            The id of the command to fetch
        global_priority:
            The priority of the request for the global rate-limiter.


        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            ``command_id`` was not a id of a valid existing command

        Returns
        -------
        discord_typings.ApplicationCommandData
            The global commmand fetched
        """
        route = Route(
            "GET",
            "/applications/{application_id}/commands/{command_id}",
            application_id=application_id,
            command_id=command_id,
        )

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def edit_global_application_command(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        command_id: Snowflake,
        *,
        name: str | UndefinedType = UNDEFINED,
        name_localizations: dict[Locales, str] | None | UndefinedType = UNDEFINED,
        description: str | UndefinedType = UNDEFINED,
        description_localizations: dict[Locales, str] | None | UndefinedType = UNDEFINED,
        options: list[ApplicationCommandOptionData] | UndefinedType = UNDEFINED,
        default_member_permissions: str | None | UndefinedType = UNDEFINED,
        dm_permission: bool | None | UndefinedType = UNDEFINED,
        type: Literal[1, 2, 3] | UndefinedType = UNDEFINED,  # TODO: Replace this with a type alias in discord_typings
        global_priority: int = 0,
    ) -> ApplicationCommandData:  # TODO: Narrow typing to never include guild_id
        """Updates a global application command

        Read the `documentation <https://discord.dev/interactions/application-commands#edit-global-application-command>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only update commands for your current application
        name:
            The name of the command

            .. note::
                If the name is already taken by a existing application command with the same name and type
                it will update the exisiting command.
            .. note::
                This has to be between 1-32 characters long and follow the `naming conventions <https://discord.dev/interactions/application-commands#application-command-object-application-command-naming>`__
        name_localizations:
            The localizations for the name

            .. note::
                This has to be between 1-32 characters long and follow the `naming conventions <https://discord.dev/interactions/application-commands#application-command-object-application-command-naming>`__
        description:
            The description of the command

            .. note::
                This has to be between 1-100 characters long

            .. warning::
                Some special characters may be automatically removed from this!
        description_localizations:
            The localizations for the description

            .. note::
                This has to be between 1-100 characters long

            .. warning::
                Some special characters may be automatically removed from this!
        options:
            The parameters or sub-commands of the command

            .. note::
                This should only be provide
        default_member_permissions:
            The default permissions to require to use the command
        dm_permission:
            Whether the command can be used in DMs.

            .. note::
                If this is :data:`UNDEFINED`, it defaults to :data:`True`.
        type:
            The type of the command

            .. note::
                This defaults to ``1`` if it is :data:`UNDEFINED`.

            **Possible values**
            - ``1``: Slash/text command
            - ``2``: User context menu
            - ``3``: Message context menu
        global_priority:
            The priority of the request for the global rate-limiter.


        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            ``command_id`` was not a id of a valid exiting command

        Returns
        -------
        discord_typings.ApplicationCommandData
            The command that was edited
        """
        route = Route(
            "PATCH",
            "/applications/{application_id}/commands/{command_id}",
            application_id=application_id,
            command_id=command_id,
        )

        payload: dict[str, Any] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name
        if name_localizations is not UNDEFINED:
            payload["name_localizations"] = name_localizations
        if description is not UNDEFINED:
            payload["description"] = description
        if description_localizations is not UNDEFINED:
            payload["description_localizations"] = description_localizations
        if options is not UNDEFINED:
            payload["options"] = options
        if default_member_permissions is not UNDEFINED:
            payload["default_member_permissions"] = default_member_permissions
        if dm_permission is not UNDEFINED:
            payload["dm_permission"] = dm_permission
        if type is not UNDEFINED:
            payload["type"] = type

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_global_application_command(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        command_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> None:
        """Deletes a global command

        Read the `documentation <https://discord.dev/interactions/application-commands#delete-global-application-command>`__

        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            The ``command_id`` was not a id of a valid existing command

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        application_id:
            The id of the command to fetch
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "GET",
            "/applications/{application_id}/commands/{command_id}",
            application_id=application_id,
            command_id=command_id,
        )

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def bulk_overwrite_global_application_commands(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        *commands: ApplicationCommandPayload,
        global_priority: int = 0,
    ) -> list[ApplicationCommandData]:  # TODO: Narrow typing to never include guild_id
        """Creates or updates a global application command

        Read the `documentation <https://discord.dev/interactions/application-commands#bulk-overwrite-global-application-commands>`__

        .. warning::
            This will replace all your global commands. Include the old commands to keep them

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only update commands for your current application
        commands:
            The global commands to overwrite the current global commands with

            .. note::
                Some fields have additional restrictions. See :meth:`HTTPClient.create_global_application_command`'s arguments for more information.
        global_priority:
            The priority of the request for the global rate-limiter.


        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        BadRequestError
            You did not follow the requirements for commands to be valid.

        Returns
        -------
        list[discord_typings.ApplicationCommandData]
            The global commands
        """
        route = Route("PUT", "/applications/{application_id}/commands", application_id=application_id)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            json=commands,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_application_commands(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        guild_id: Snowflake,
        *,
        with_localizations: bool | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> list[
        ApplicationCommandData
    ]:  # TODO: Narrow typing to always include guild_id and localization overload and never dm_permission
        """Gets all commands in a guild

        Read the `documentation <https://discord.dev/interactions/application-commands#get-guild-application-commands>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        guild_id:
            The guild to get commands from.
        global_priority:
            The priority of the request for the global rate-limiter.


        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided

        Returns
        -------
        list[discord_typings.ApplicationCommandData]
            The commmands registered to the guild
        """
        route = Route(
            "GET",
            "/applications/{application_id}/guilds/{guild_id}commands",
            application_id=application_id,
            guild_id=guild_id,
        )

        query = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if with_localizations is not UNDEFINED:
            query["with_localizations"] = with_localizations

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            query=query,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def create_guild_application_command(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        guild_id: Snowflake,
        name: str,
        description: str,
        *,
        name_localizations: dict[Locales, str] | None | UndefinedType = UNDEFINED,
        description_localizations: dict[Locales, str] | None | UndefinedType = UNDEFINED,
        options: list[ApplicationCommandOptionData] | UndefinedType = UNDEFINED,
        default_member_permissions: str | None | UndefinedType = UNDEFINED,
        type: Literal[1, 2, 3] | UndefinedType = UNDEFINED,  # TODO: Replace this with a type alias in discord_typings
        global_priority: int = 0,
    ) -> ApplicationCommandData:  # TODO: Narrow typing to never include guild_id
        """Creates or updates a guild command

        Read the `documentation <https://discord.dev/interactions/application-commands#create-guild-application-command>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only update commands for your current application
        guild_id:
            The guild to add the command to
        name:
            The name of the command

            .. note::
                If the name is already taken by a existing application command with the same name and type
                it will update the exisiting command.
            .. note::
                This has to be between 1-32 characters long and follow the `naming conventions <https://discord.dev/interactions/application-commands#application-command-object-application-command-naming>`__
        description:
            The description of the command

            .. note::
                This has to be between 1-100 characters long

            .. warning::
                Some special characters may be automatically removed from this!
        name_localizations:
            The localizations for the name

            .. note::
                This has to be between 1-32 characters long and follow the `naming conventions <https://discord.dev/interactions/application-commands#application-command-object-application-command-naming>`__
        description_localizations:
            The localizations for the description

            .. note::
                This has to be between 1-100 characters long

            .. warning::
                Some special characters may be automatically removed from this!
        options:
            The parameters or sub-commands of the command

            .. note::
                This should only be provide
        default_member_permissions:
            The default permissions to require to use the command
        type:
            The type of the command

            .. note::
                This defaults to ``1`` if it is :data:`UNDEFINED`.

            **Possible values**
            - ``1``: Slash/text command
            - ``2``: User context menu
            - ``3``: Message context menu
        global_priority:
            The priority of the request for the global rate-limiter.

        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            The guild was not found

        Returns
        -------
        discord_typings.ApplicationCommandData
            The command that was created
        """
        route = Route(
            "POST",
            "/applications/{application_id}/guilds/{guild_id}/commands",
            application_id=application_id,
            guild_id=guild_id,
        )

        payload: dict[str, Any] = {"name": name, "description": description}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name_localizations is not UNDEFINED:
            payload["name_localizations"] = name_localizations
        if description_localizations is not UNDEFINED:
            payload["description_localizations"] = description_localizations
        if options is not UNDEFINED:
            payload["options"] = options
        if default_member_permissions is not UNDEFINED:
            payload["default_member_permissions"] = default_member_permissions
        if type is not UNDEFINED:
            payload["type"] = type

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_application_command(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        guild_id: Snowflake,
        command_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> ApplicationCommandData:  # TODO: Narrow typing to never include guild_id
        """Gets a guild command

        Read the `documentation <https://discord.dev/interactions/application-commands#get-guild-application-command>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        guild_id:
            The guild to get the command from
        application_id:
            The id of the command to fetch
        global_priority:
            The priority of the request for the global rate-limiter.

        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            The guild or the command was not found

        Returns
        -------
        discord_typings.ApplicationCommandData
            The global commmand fetched
        """
        route = Route(
            "GET",
            "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
            application_id=application_id,
            guild_id=guild_id,
            command_id=command_id,
        )

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def edit_guild_application_command(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        guild_id: Snowflake,
        command_id: Snowflake,
        *,
        name: str | UndefinedType = UNDEFINED,
        name_localizations: dict[Locales, str] | None | UndefinedType = UNDEFINED,
        description: str | UndefinedType = UNDEFINED,
        description_localizations: dict[Locales, str] | None | UndefinedType = UNDEFINED,
        options: list[ApplicationCommandOptionData] | UndefinedType = UNDEFINED,
        default_member_permissions: str | None | UndefinedType = UNDEFINED,
        type: Literal[1, 2, 3] | UndefinedType = UNDEFINED,  # TODO: Replace this with a type alias in discord_typings
        global_priority: int = 0,
    ) -> ApplicationCommandData:  # TODO: Narrow typing
        """Updates a guild application command

        Read the `documentation <https://discord.dev/interactions/application-commands#edit-guild-application-command>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only update commands for your current application
        guild_id:
            The id of the guild where the command is located in
        name:
            The name of the command

            .. note::
                If the name is already taken by a existing application command with the same name and type
                it will update the exisiting command.
            .. note::
                This has to be between 1-32 characters long and follow the `naming conventions <https://discord.dev/interactions/application-commands#application-command-object-application-command-naming>`__
        name_localizations:
            The localizations for the name

            .. note::
                This has to be between 1-32 characters long and follow the `naming conventions <https://discord.dev/interactions/application-commands#application-command-object-application-command-naming>`__
        description:
            The description of the command

            .. note::
                This has to be between 1-100 characters long

            .. warning::
                Some special characters may be automatically removed from this!
        description_localizations:
            The localizations for the description

            .. note::
                This has to be between 1-100 characters long

            .. warning::
                Some special characters may be automatically removed from this!
        options:
            The parameters or sub-commands of the command

            .. note::
                This should only be provide
        default_member_permissions:
            The default permissions to require to use the command
        type:
            The type of the command

            .. note::
                This defaults to ``1`` if it is :data:`UNDEFINED`.

            **Possible values**
            - ``1``: Slash/text command
            - ``2``: User context menu
            - ``3``: Message context menu
        global_priority:
            The priority of the request for the global rate-limiter.

        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            The guild or the command was not found
        BadRequestError
            You did not follow the restrictions for some fields.

        Returns
        -------
        discord_typings.ApplicationCommandData
            The command that was edited
        """
        route = Route(
            "PATCH",
            "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
            application_id=application_id,
            guild_id=guild_id,
            command_id=command_id,
        )

        payload: dict[str, Any] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name
        if name_localizations is not UNDEFINED:
            payload["name_localizations"] = name_localizations
        if description is not UNDEFINED:
            payload["description"] = description
        if description_localizations is not UNDEFINED:
            payload["description_localizations"] = description_localizations
        if options is not UNDEFINED:
            payload["options"] = options
        if default_member_permissions is not UNDEFINED:
            payload["default_member_permissions"] = default_member_permissions
        if type is not UNDEFINED:
            payload["type"] = type

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_guild_application_command(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        guild_id: Snowflake,
        command_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> None:
        """Deletes a guild command

        Read the `documentation <https://discord.dev/interactions/application-commands#delete-guild-application-command>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        application_id:
            The id of the command to fetch
        guild_id:
            The guild where the command is located in
        command_id:
            The command to delete
        global_priority:
            The priority of the request for the global rate-limiter.

        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            The command or guild was not found
        """
        route = Route(
            "GET",
            "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
            application_id=application_id,
            guild_id=guild_id,
            command_id=command_id,
        )

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def bulk_overwrite_guild_application_commands(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        guild_id: Snowflake,
        *commands: ApplicationCommandPayload,
        global_priority: int = 0,
    ) -> list[ApplicationCommandData]:  # TODO: Narrow typing to always include guild_id
        """Bulk overwrite guild commands

        Read the `documentation <https://discord.dev/interactions/application-commands#bulk-overwrite-guild-application-commands>`__

        .. warning::
            This will replace all your global commands. Include the old commands to keep them

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only update commands for your current application
        guild_id:
            The guild to overwrite commands in
        commands:
            The commands to overwrite the current commands with

            .. note::
                There is some extra limits. See the params of :meth:`HTTPClient.edit_guild_application_command` for more info.
        global_priority:
            The priority of the request for the global rate-limiter.

        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            The guild was not found
        BadRequestError
            You did not follow the restrictions

        Returns
        -------
        list[discord_typings.ApplicationCommandData]
            The new commands
        """
        route = Route(
            "PUT",
            "/applications/{application_id}/guilds/{guild_id}/commands",
            application_id=application_id,
            guild_id=guild_id,
        )

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            json=commands,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_application_command_permissions(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        guild_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> list[GuildApplicationCommandPermissionData]:
        """Gets all application command permissions in a guild

        Read the `documentation <https://discord.dev/interactions/application-commands#get-guild-application-command-permissions>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        application_id:
            The id of the command to fetch
        guild_id:
            The guild to get permissions from
        global_priority:
            The priority of the request for the global rate-limiter.

        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            The guild was not found

        Returns
        -------
        list[discord_typings.GuildApplicationCommandPermissionData]
            The application command permissions overwrites in the guild
        """
        route = Route(
            "GET",
            "/applications/{application_id}/guilds/{guild_id}/commands/permissions",
            application_id=application_id,
            guild_id=guild_id,
        )

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_application_command_permissions(
        self,
        authentication: BotAuthentication | BearerAuthentication,
        application_id: Snowflake,
        guild_id: Snowflake,
        command_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> GuildApplicationCommandPermissionData:
        """Gets permissions for a command in a guild

        Read the `documentation <https://discord.dev/interactions/application-commands#get-application-command-permissions>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        command_id:
            The id of the command to fetch
        guild_id:
            The guild to get permissions from
        global_priority:
            The priority of the request for the global rate-limiter.

        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            The guild or command was not found

        Returns
        -------
        discord_typings.GuildApplicationCommandPermissionData
            The application command permissions overwrites for the command
        """
        route = Route(
            "GET",
            "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions",
            application_id=application_id,
            guild_id=guild_id,
            command_id=command_id,
        )

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Add Edit Application Command Permissions

    # Responding to application commands (Receiving and responding)
    # TODO: Add Create Interaction Response
    async def get_original_interaction_response(
        self,
        application_id: Snowflake,
        interaction_token: str,
        *,
        global_priority: int = 0,
    ) -> MessageData:
        """Gets the first response sent to a interaction

        Read the `documentation <https://discord.dev/interactions/receiving-and-responding#get-original-interaction-response>`__

        Parameters
        ----------
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        interaction_token:
            The token of the interaction
        global_priority:
            The priority of the request for the global rate-limiter.

        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            You have not responded or the response was ephemeral or a defer that has not been completed yet.

        Returns
        -------
        discord_typings.MessageData
            The message
        """
        route = Route(
            "GET",
            "/webhooks/{application_id}/{interaction_token}/messages/@original",
            application_id=application_id,
            interaction_token=interaction_token,
        )

        r = await self._request(
            route,
            rate_limit_key=None,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Add Edit Original Interaction Response

    async def delete_original_interaction_response(
        self,
        application_id: Snowflake,
        interaction_token: str,
        *,
        global_priority: int = 0,
    ) -> None:
        """Deletes the first response sent to a interaction

        Read the `documentation <https://discord.dev/interactions/receiving-and-responding#delete-original-interaction-response>`__

        .. note::
            You can not delete ephemeral responses

        Parameters
        ----------
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        interaction_token:
            The token of the interaction
        global_priority:
            The priority of the request for the global rate-limiter.

        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            No response has been sent or a ephemeral response was sent.
        """
        route = Route(
            "DELETE",
            "/webhooks/{application_id}/{interaction_token}/messages/@original",
            application_id=application_id,
            interaction_token=interaction_token,
        )

        await self._request(
            route,
            rate_limit_key=None,
            global_priority=global_priority,
        )

    # TODO: Add Create Followup Message

    async def get_followup_message(
        self,
        application_id: Snowflake,
        interaction_token: str,
        message_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> MessageData:
        """Gets a response sent to a interaction by message id

        Read the `documentation <https://discord.dev/interactions/receiving-and-responding#get-followup-message>`__

        Parameters
        ----------
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        interaction_token:
            The token of the interaction
        message_id:
            The id of the message to fetch
        global_priority:
            The priority of the request for the global rate-limiter.

        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            A invalid ``message_id`` was provided or it was not a follow-up from this interaction.

        Returns
        -------
        discord_typings.MessageData
            The message that was fetched
        """
        route = Route(
            "GET",
            "/webhooks/{application_id}/{interaction_token}/messages/{message_id}",
            application_id=application_id,
            interaction_token=interaction_token,
            message_id=message_id,
        )

        r = await self._request(
            route,
            rate_limit_key=None,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # TODO: Add Edit Followup Message
    async def delete_followup_message(
        self,
        application_id: Snowflake,
        interaction_token: str,
        message_id: Snowflake,
        *,
        global_priority: int = 0,
    ) -> MessageData:
        """Deletes a response sent to a interaction by message id

        Read the `documentation <https://discord.dev/interactions/receiving-and-responding#delete-followup-message>`__

        Parameters
        ----------
        application_id:
            The application id/client id of the current application

            .. note::
                You can only get commands for your current application
        interaction_token:
            The token of the interaction
        message_id:
            The id of the message to delete
        global_priority:
            The priority of the request for the global rate-limiter.


        Raises
        ------
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection
        UnauthorizedError
            A invalid token was provided
        NotFoundError
            A invalid ``message_id`` was provided or it was not a follow-up from this interaction.
        """
        route = Route(
            "DELETE",
            "/webhooks/{application_id}/{interaction_token}/messages/{message_id}",
            application_id=application_id,
            interaction_token=interaction_token,
            message_id=message_id,
        )

        r = await self._request(
            route,
            rate_limit_key=None,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

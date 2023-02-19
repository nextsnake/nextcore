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
from abc import ABC
from ..abstract_client import AbstractHTTPClient
from ...route import Route
from ....common import UndefinedType, UNDEFINED
if TYPE_CHECKING:
    from ...authentication import BotAuthentication
    from typing import Any
    from discord_typings import (
        AutoModerationRuleData,
        AutoModerationEventTypes,
        AutoModerationTriggerTypes,
        AutoModerationTriggerMetadataData,
        AutoModerationActionData,
        Snowflake, 
    )


class AutoModerationHTTPWrappers(AbstractHTTPClient, ABC):
    """HTTP wrappers for Auto Moderation API endpoints.

    This is an abstract base class that should not be used directly.
    """

    __sltos__ = ()

    async def list_auto_moderation_rules_for_guild(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        wait: bool = True,
        global_priority: int = 0,
        bucket_priority: int = 0,
    ) -> list[AutoModerationRuleData]:
        """List all auto moderation rules for a guild.

        Read the `documentation  <https://discord.dev/resources/auto-moderation#list-auto-moderation-rules-for-guild>`__

        Parameters
        ----------
        authentication: BotAuthenticaA
        guild_id: Snowflake
            The guild to list the auto moderation rules for.
        wait: bool
            Whether to wait when getting rate limited.
        global_priority:
            The priority of the request for the global rate-limiter.
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        
        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`.
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection.
        UnauthorizedError
            An invalid token was provided.
        NotFoundError
            The guild was not found.
        BadRequestError
            You did not follow the requirements for some of the parameters.
        """
        route = Route(
            "GET",
            "/guilds/{guild_id}/auto-moderation/rules",
            guild_id=guild_id,
        )
        r = await self._request(
            route=route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait
        )
        return await r.json()  # type: ignore [no-type-return]
    
    async def get_auto_moderation_rule(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        rule_id: Snowflake,
        *,
        global_priority: int = 0,
        bucket_priority: int = 0,
        wait: bool = True,
    ) -> AutoModerationRuleData:
        """List all auto moderation rules for a guild.

        .. note::

            This requires the ``MANAGE_GUILD`` permission.

        Parameters
        ----------
        authentication: BotAuthentication
            Authentication info.
        guild_id: Snowflake
            The guild that the auto moderation rule is in.
        rule_id: Snowflake
            The auto moderation rule id.
        wait: bool
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.
        global_priority:
            The priority of the request for the global rate-limiter.
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        
        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`.
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection.
        UnauthorizedError
            An invalid token was provided.
        NotFoundError
            The guild was not found.
        BadRequestError
            You did not follow the requirements for some of the parameters.
        """
        route = Route(
            method="GET",
            path="/guilds/{guild_id}/auto-moderation/rules/{rule_id}",
            guild_id=guild_id,
            rule_id=rule_id,
        )
        r = await self._request(
            route=route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait
        )
        return await r.json()  # type: ignore [no-any-return]
    
    async def create_auto_moderation_rule(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        name: str,
        event_type: AutoModerationEventTypes,
        trigger_type: AutoModerationTriggerTypes,
        trigger_metadata: AutoModerationTriggerMetadataData | UndefinedType = UNDEFINED,
        actions: list[AutoModerationActionData],
        enabled: bool | UndefinedType = UNDEFINED,
        exempt_roles: list[Snowflake] | UndefinedType = UNDEFINED,
        exempt_channels: list[Snowflake] | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
        bucket_priority: int = 0,
        wait: bool = True,
    ):
        """
        Create a new auto moderation rule.

        Read the `documentation <https://discord.dev/resources/auto-moderation#create-auto-moderation-rule>`__

        .. note::

            This requires the ``MANAGE_GUILD`` permission.

        Parameters
        ----------
        authentication: BotAuthentication
            Authentication info.
        guild_id: Snowflake
            The guild to create the auto moderation rule in.
        name: str
            The name of the auto moderation rule.
        event_type: discord_typings.AutoModerationEventTypes
            The event type of the auto moderation rule.
        trigger_type: discord_typings.AutoModerationTriggerTypes
            The trigger type of the auto moderation rule.
        trigger_metadata: discord_typings.AutoModerationTriggerMetadataData | UndefinedType
            The trigger metadata of the auto moderation rule.
        actions: list[AutoModerationActionData]
            The actions to do when this rule got triggered.
        enabled: bool | UndefinedType
            Whether the rule is enabled.
        exempt_roles: list[Snowflake] | UndefinedType
            The roles that are exempt from this rule.
        exempt_channels: list[Snowflake] | UndefinedType
            The channels that are exempt from this rule.
        wait: bool
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.
        global_priority:
            The priority of the request for the global rate-limiter.
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        
        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`.
        aiohttp.ClientConnectorError
            Could not connect due to a problem with your connection.
        UnauthorizedError
            An invalid token was provided.
        NotFoundError
            The guild was not found.
        BadRequestError
            You did not follow the requirements for some of the parameters.
        """
        route = Route(
            "POST",
            "/guilds/{guild_id}/auto-moderation/rules",
            guild_id=guild_id,
        )
        payload: dict[str, Any] = {
            "name": name,
            "event_type": event_type,
            "trigger_type": trigger_type,
            "actions": actions,
        } # TODO: Use a typehint for payload
        headers = {"Authorization": str(authentication)}
        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason
        if trigger_metadata is not UNDEFINED:
            payload["trigger_metadata"] = trigger_metadata
        if enabled is not UNDEFINED:
            payload["enabled"] = enabled
        if exempt_roles is not UNDEFINED:
            payload["exempt_roles"] = exempt_roles
        if exempt_channels is not UNDEFINED:
            payload["exempt_channels"] = exempt_channels
        r = await self._request(
            route=route,
            rate_limit_key=authentication.rate_limit_key,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            headers=headers,
            wait=wait,
            json=payload,
        )
        return await r.json()  # typing: ignore [no-any-return]
    
    async def update_auto_moderation_rule(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        rule_id: Snowflake,
        *,
        name: str | UndefinedType = UNDEFINED,
        event_type: AutoModerationEventTypes | UndefinedType = UNDEFINED,
        trigger_type: AutoModerationTriggerTypes | UndefinedType = UNDEFINED,
        trigger_metadata: AutoModerationTriggerMetadataData | UndefinedType = UNDEFINED,
        actions: list[AutoModerationActionData] | UndefinedType = UNDEFINED,
        enabled: bool | UndefinedType = UNDEFINED,
        exempt_roles: list[Snowflake] | UndefinedType = UNDEFINED,
        exempt_channels: list[Snowflake] | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
        bucket_priority: int = 0,
        wait: bool = True,
    ) -> AutoModerationRuleData:
        """
        Update an auto moderation rule.

        Read the `documentation <https://discord.dev/resources/auto-moderation#update-auto-moderation-rule>`__

        .. note::

            This requires the ``MANAGE_GUILD`` permission.

        Parameters
        ----------
        authentication: BotAuthentication
            Authentication info.
        guild_id: Snowflake
            The guild that the auto moderation rule is in.
        rule_id: Snowflake
            The auto moderation rule id.
        name: str | UndefinedType
            The name of the auto moderation rule.
        event_type: discord_typings.AutoModerationEventTypes | UndefinedType
            The event type of the auto moderation rule.
        trigger_type: discord_typings.AutoModerationTriggerTypes | UndefinedType
            The trigger type of the auto moderation rule.
        trigger_metadata: discord_typings.AutoModerationTriggerMetadataData | UndefinedType
            The trigger metadata of the auto moderation rule.
        actions: list[AutoModerationActionData] | UndefinedType
            The actions to do when this rule got triggered.
        enabled: bool | UndefinedType
            Whether the rule is enabled.
        exempt_roles: list[Snowflake] | UndefinedType
            The roles that are exempt from this rule.
        exempt_channels: list[Snowflake] | UndefinedType
            The channels that are exempt from this rule.
        reason: str
            A reason for the audit log.

            .. note::
                
                This must be in 1 and 512 characters.
        wait: bool 
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.
        global_priority:
            The priority of the request for the global rate-limiter.
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        """
        route = Route(
            "PATCH",
            "/guilds/{guild_id}/auto-moderation/rules/{rule_id}",
            guild_id=guild_id,
            rule_id=rule_id,
        )
        payload: dict[str, Any] = {} # TODO: Use a typehint for payload

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)

        if name is not UNDEFINED:
            payload['name'] = name
        if event_type is not UNDEFINED:
            payload['event_type'] = event_type
        if trigger_type is not UNDEFINED:
            payload['trigger_type'] = trigger_type
        if trigger_metadata is not UNDEFINED:
            payload['trigger_metadata'] = trigger_metadata
        if actions is not UNDEFINED:
            payload['actions'] = actions
        if enabled is not UNDEFINED:
            payload['enabled'] = enabled
        if exempt_roles is not UNDEFINED:
            payload['exempt_roles'] = exempt_roles
        if exempt_channels is not UNDEFINED:
            payload['exempt_channels'] = exempt_channels
        headers = {"Authorization": str(authentication)}
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason
        r = await self._request(
            route=route,
            rate_limit_key=authentication.rate_limit_key,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            headers=headers,
            wait=wait,
            json=payload,
        )
        return await r.json()  # typing: ignore [no-any-return]
    
    async def delete_auto_moderation_rule(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        rule_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
        bucket_priority: int = 0,
        wait: bool = True,
    ):
        """
        Delete an auto moderation rule.

        Read the `documentation <https://discord.dev/resources/auto-moderation#delete-auto-moderation-rule>`__

        .. note::

            This requires the ``MANAGE_GUILD`` permission.

        Parameters
        ----------
        authentication: BotAuthentication
            Authentication info.
        guild_id: Snowflake
            The guild that the auto moderation rule is in.
        rule_id: Snowflake
            The auto moderation rule id.
        reason: str
            A reason for the audit log.

            .. note::
                
                This must be in 1 and 512 characters.
        wait: bool 
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.
        global_priority:
            The priority of the request for the global rate-limiter.
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        """
        route = Route(
            "DELETE",
            "/guilds/{guild_id}/auto-moderation/rules/{rule_id}",
            guild_id=guild_id,
            rule_id=rule_id,
        )
        headers = {"Authorization": str(authentication)}
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason
        await self._request(
            route=route,
            rate_limit_key=authentication.rate_limit_key,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            headers=headers,
            wait=wait,
        )


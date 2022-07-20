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

from logging import getLogger
from typing import TYPE_CHECKING

from ...common import UNDEFINED, UndefinedType
from ..route import Route
from .base_client import BaseHTTPClient
from .wrappers import (
    ApplicationCommandsHTTPWrappers,
    AuditLogHTTPWrappers,
    ChannelHTTPWrappers,
    EmojiHTTPWrappers,
    GuildHTTPWrappers,
    GuildScheduledEventHTTPWrappers,
    GuildTemplateHTTPWrappers,
    InviteHTTPWrappers,
    StageInstanceHTTPWrappers,
    StickerHTTPWrappers,
    UserHTTPWrappers,
    VoiceHTTPWrappers,
)

if TYPE_CHECKING:
    from typing import Any, Final

    from discord_typings import (
        ApplicationData,
        GetGatewayBotData,
        GetGatewayData,
        MessageData,
        Snowflake,
        WebhookData,
    )

    from ..authentication import BearerAuthentication, BotAuthentication

logger = getLogger(__name__)

__all__: Final[tuple[str, ...]] = ("HTTPClient",)


class HTTPClient(
    ApplicationCommandsHTTPWrappers,
    AuditLogHTTPWrappers,
    ChannelHTTPWrappers,
    EmojiHTTPWrappers,
    GuildHTTPWrappers,
    GuildScheduledEventHTTPWrappers,
    GuildTemplateHTTPWrappers,
    InviteHTTPWrappers,
    StageInstanceHTTPWrappers,
    StickerHTTPWrappers,
    UserHTTPWrappers,
    VoiceHTTPWrappers,
    BaseHTTPClient,
):
    """The HTTP client to interface with the Discord API.

    **Example usage**

    .. code-block:: python3

        http_client = HTTPClient()
        await http_client.setup()

        gateway = await http_client.get_gateway()

        print(gateway["url"])

        await http_client.close()

    Parameters
    ----------
    trust_local_time:
        Whether to trust local time.
        If this is not set HTTP rate limiting will be a bit slower but may be a bit more accurate on systems where the local time is off.
    timeout:
        The default request timeout in seconds.
    max_rate_limit_retries:
        How many times to attempt to retry a request after rate limiting failed.

    Attributes
    ----------
    trust_local_time:
        If this is enabled, the rate limiter will use the local time instead of the discord provided time. This may improve your bot's speed slightly.

        .. warning::
            If your time is not correct, and this is set to :data:`True`, this may result in more rate limits being hit.

            .. tab:: Ubuntu

                You can check if your clock is synchronized by running the following command:

                .. code-block:: bash

                    timedatectl

                If it is synchronized, it will show "System clock synchronized: yes" and "NTP service: running"

                If the system clock is not synchronized but the ntp service is running you will have to wait a few minutes for it to sync.

                To enable the ntp service run the following command:

                .. code-block:: bash

                    sudo timedatectl set-ntp on

                This will automatically sync the system clock every once in a while.

            .. tab:: Arch

                You can check if your clock is synchronized by running the following command:

                .. code-block:: bash

                    timedatectl

                If it is synchronized, it will show "System clock synchronized: yes" and "NTP service: running"

                If the system clock is not synchronized but the ntp service is running you will have to wait a few minutes for it to sync.

                To enable the ntp service run the following command:

                .. code-block:: bash

                    sudo timedatectl set-ntp on

                This will automatically sync the system clock every once in a while.

            .. tab:: Windows

                This can be turned on by going to ``Settings -> Time & language -> Date & time`` and turning on ``Set time automatically``.
    timeout:
        The default request timeout in seconds.
    default_headers:
        The default headers to pass to every request.
    max_retries:
        How many times to attempt to retry a request after rate limiting failed.

        .. note::
            This does not retry server errors.
    rate_limit_storages:
        Classes to store rate limit information.

        The key here is the rate_limit_key (often a user ID).
    dispatcher:
        Events from the HTTPClient. See the :ref:`events<HTTPClient dispatcher>`
    """

    # Wrapper functions for requests
    # Application commands
    # Audit log
    # Channel
    # Emoji
    # Guild
    # Guild Scheduled events
    # Guild Template
    # Invite
    # Stage instance
    # Sticker
    # User
    # Voice
    # Webhook
    async def create_webhook(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        name: str,
        *,
        avatar: str | None | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> WebhookData:
        """Creates a webhook

        Read the `documentation <https://discord.dev/resources/webhook#create-webhook>`__

        .. note::
            This requires the ``MANAGE_WEBHOOKS`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to create a webhook in
        name:
            The name of the webhook

            .. note::
                This has to be between ``1`` and ``80`` characters.

                It has to follow the `Discord nickname restrictions <https://discord.dev/resources/user#usernames-and-nicknames>`__ (with the exception of the length limit.)
        avatar:
            Base64 encoded image avatar to use as the default avatar
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.WebhookData
            The webhook that was created
        """
        route = Route("POST", "/channels/{channel_id}/webhooks", channel_id=channel_id)

        payload: dict[str, Any] = {"name": name}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if avatar is not UNDEFINED:
            payload["avatar"] = avatar

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

    async def get_channel_webhooks(
        self, authentication: BotAuthentication, channel_id: Snowflake, *, global_priority: int = 0
    ) -> list[WebhookData]:
        """Gets all webhooks in a channel

        Read the `documentation <https://discord.dev/resources/webhook#get-channel-webhooks>`__

        .. note::
            This requires the ``MANAGE_WEBHOOKS`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        channel_id:
            The id of the channel to get webhooks from
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[discord_typings.WebhookData]
            The webhooks in the channel
        """
        route = Route("GET", "/channels/{channel_id}/webhooks", channel_id=channel_id)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_guild_webhooks(
        self, authentication: BotAuthentication, guild_id: Snowflake, *, global_priority: int = 0
    ) -> list[WebhookData]:
        """Gets all webhooks in a guild

        Read the `documentation <https://discord.dev/resources/webhook#get-guild-webhooks>`__

        .. note::
            This requires the ``MANAGE_WEBHOOKS`` permission

        Parameters
        ----------
        authentication:
            Authentication info.
        guild_id:
            The id of the guild to get webhooks from
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        list[discord_typings.WebhookData]
            The webhooks in the channel
        """
        route = Route("GET", "/guilds/{guild_id}/webhooks", guild_id=guild_id)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_webhook(
        self, authentication: BotAuthentication, webhook_id: Snowflake, *, global_priority: int = 0
    ) -> WebhookData:
        """Gets a webhook by webhook id

        Read the `documentation <https://discord.dev/resources/webhook#get-webhook>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        webhook_id:
            The id of the webhook to fetch
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.WebhookData
            The webhook that was fetched
        """
        route = Route("GET", "/webhooks/{webhook_id}", webhook_id=webhook_id)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_webhook_with_token(
        self, webhook_id: Snowflake, webhook_token: str, *, global_priority: int = 0
    ) -> WebhookData:
        """Gets a webhook by webhook id and token

        Read the `documentation <https://discord.dev/resources/webhook#get-webhook-with-token>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        webhook_id:
            The id of the webhook to fetch
        webhook_token:
            The token of the webhook
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.WebhookData
            The webhook that was fetched
        """
        route = Route(
            "GET", "/webhooks/{webhook_id}/{webhook_token}", webhook_id=webhook_id, webhook_token=webhook_token
        )

        r = await self._request(
            route,
            rate_limit_key=None,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_webhook(
        self,
        authentication: BotAuthentication,
        webhook_id: Snowflake,
        *,
        name: str | UndefinedType = UNDEFINED,
        avatar: str | None | UndefinedType = UNDEFINED,
        channel_id: Snowflake | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> WebhookData:
        """Modifies a webhook

        Read the `documentation <https://discord.dev/resources/webhook#modify-webhook>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        webhook_id:
            The id of the webhook to modify
        name:
            The new name of the webhook
        avatar:
            Base64 encoded avatar of the webhook
        channel_id:
            The id of a channel to move the webhook to.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.WebhookData
            The updated webhook
        """
        route = Route("PATCH", "/webhooks/{webhook_id}", webhook_id=webhook_id)

        payload: dict[str, Any] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name
        if avatar is not UNDEFINED:
            payload["avatar"] = avatar
        if channel_id is not UNDEFINED:
            payload["channel_id"] = channel_id

        headers = {"Authorization": str(authentication)}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            headers=headers,
            rate_limit_key=authentication.rate_limit_key,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def modify_webhook_with_token(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        *,
        name: str | UndefinedType = UNDEFINED,
        avatar: str | None | UndefinedType = UNDEFINED,
        channel_id: Snowflake | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> WebhookData:
        """Modifies a webhook

        Read the `documentation <https://discord.dev/resources/webhook#modify-webhook-with-token>`__

        Parameters
        ----------
        webhook_id:
            The id of the webhook to modify
        webhook_token:
            The token of the webhook to use for authentication
        name:
            The new name of the webhook
        avatar:
            Base64 encoded avatar of the webhook
        channel_id:
            The id of a channel to move the webhook to.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.WebhookData
            The updated webhook
        """
        route = Route(
            "PATCH", "/webhooks/{webhook_id}/{webhook_token}", webhook_id=webhook_id, webhook_token=webhook_token
        )

        payload: dict[str, Any] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if name is not UNDEFINED:
            payload["name"] = name
        if avatar is not UNDEFINED:
            payload["avatar"] = avatar
        if channel_id is not UNDEFINED:
            payload["channel_id"] = channel_id

        headers = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            headers=headers,
            rate_limit_key=None,
            json=payload,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_webhook(
        self,
        authentication: BotAuthentication,
        webhook_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Deletes a webhook

        Read the `documentation <https://discord.dev/resources/webhook#delete-webhook>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        webhook_id:
            The id of the webhook to delete
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.WebhookData
            The webhook that was deleted
        """
        route = Route("DELETE", "/webhooks/{webhook_id}", webhook_id=webhook_id)

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

    async def delete_webhook_with_token(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        *,
        reason: str | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Deletes a webhook

        Read the `documentation <https://discord.dev/resources/webhook#delete-webhook-with-token>`__

        Parameters
        ----------
        webhook_id:
            The id of the webhook to delete
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.WebhookData
            The webhook that was fetched
        """
        route = Route(
            "DELETE", "/webhooks/{webhook_id}/{webhook_token}", webhook_id=webhook_id, webhook_token=webhook_token
        )

        headers = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if reason is not UNDEFINED:
            headers["X-Audit-Log-Reason"] = reason

        r = await self._request(
            route,
            rate_limit_key=None,
            headers=headers,
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # TODO: @ooliver1 should implement execute webhook
    # TODO: @ooliver1 should implement execute slack-compatible webhook
    # TODO: @ooliver1 should implement execute github-compatible webhook

    async def get_webhook_message(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        message_id: Snowflake,
        *,
        thread_id: Snowflake | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> MessageData:
        """Gets a message sent by the webhook

        Read the `documentation <https://discord.dev/resources/webhook#get-webhook-message>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        webhook_id:
            The id of the webhook to fetch a message from
        webhook_token:
            The token of the webhook
        message_id:
            The id of the message to fetch
        thread_id:
            The id of the thread to fetch the message from

            .. note::
                This has to be a thread in the channel the webhook is in
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.MessageData
            The message that was fetched
        """
        route = Route(
            "GET",
            "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}",
            webhook_id=webhook_id,
            webhook_token=webhook_token,
            message_id=message_id,
        )

        query = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if thread_id is not UNDEFINED:
            query["thread_id"] = thread_id

        r = await self._request(route, rate_limit_key=None, global_priority=global_priority, query=query)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # TODO: @ooliver1 should implement edit webhook message

    async def delete_webhook_message(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        message_id: Snowflake,
        *,
        thread_id: Snowflake | UndefinedType = UNDEFINED,
        global_priority: int = 0,
    ) -> None:
        """Deletes a message sent by the webhook

        Read the `documentation <https://discord.dev/resources/webhook#delete-webhook-message>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        webhook_id:
            The id of the webhook to fetch a message from
        webhook_token:
            The token of the webhook
        message_id:
            The id of the message to fetch
        thread_id:
            The id of the thread to fetch the message from

            .. note::
                This has to be a thread in the channel the webhook is in
        global_priority:
            The priority of the request for the global rate-limiter.
        """
        route = Route(
            "DELETE",
            "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}",
            webhook_id=webhook_id,
            webhook_token=webhook_token,
            message_id=message_id,
        )

        query = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if thread_id is not UNDEFINED:
            query["thread_id"] = thread_id

        r = await self._request(route, rate_limit_key=None, global_priority=global_priority, query=query)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # Gateway
    async def get_gateway(self) -> GetGatewayData:
        """Gets gateway connection info.

        Read the `documentation <https://discord.dev/topics/gateway#get-gateway>`__ for more info.

        **Example usage:**

        .. code-block:: python

            gateway_info = await http_client.get_gateway()

        Returns
        -------
        discord_typings.GetGatewayData
            The gateway info.
        """
        route = Route("GET", "/gateway", ignore_global=True)
        r = await self._request(route, rate_limit_key=None)

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_gateway_bot(
        self, authentication: BotAuthentication, *, global_priority: int = 0
    ) -> GetGatewayBotData:
        """Gets gateway connection information.

        Read the `documentation <https://discord.dev/topics/gateway#gateway-get-gateway-bot>`__

        **Example usage:**

        .. code-block:: python

            bot_info = await http_client.get_gateway_bot(token)

        Parameters
        ----------
        authentication:
            Authentication info.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.GetGatewayBotData
            Gateway connection info.
        """
        route = Route("GET", "/gateway/bot")
        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # OAuth2
    async def get_current_bot_application_information(
        self, authentication: BotAuthentication, *, global_priority: int = 0
    ) -> ApplicationData:
        """Gets the bots application

        Read the `documentation <https://discord.dev/topics/oauth2#get-current-bot-application-information>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.ApplicationData
            The application the bot is connected to
        """
        route = Route("GET", "/oauth2/applications/@me")

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_current_authorization_information(
        self, authentication: BotAuthentication | BearerAuthentication, *, global_priority: int = 0
    ) -> dict[str, Any]:  # TODO: Narrow typing
        """Gets the bots application

        Read the `documentation <https://discord.dev/topics/oauth2#get-current-authorization-information>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.???
            Info about the current logged in user/bot
        """
        route = Route("GET", "/oauth2/@me")

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

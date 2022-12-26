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

from aiohttp import FormData

from ....common import UNDEFINED, UndefinedType, json_dumps
from ...route import Route
from ..abstract_client import AbstractHTTPClient

if TYPE_CHECKING:
    from typing import Any, Final, Iterable

    from discord_typings import (
        ActionRowData,
        AllowedMentionsData,
        AttachmentData,
        EmbedData,
        MessageData,
        MessageReferenceData,
        Snowflake,
        WebhookData,
    )

    from ...authentication import BotAuthentication
    from ...file import File

logger = getLogger(__name__)

__all__: Final[tuple[str, ...]] = ("WebhookHTTPWrappers",)


class WebhookHTTPWrappers(AbstractHTTPClient, ABC):
    """HTTP wrappers for webhook API endpoints.

    This is an abstract base class that should not be used directly.
    """

    __slots__ = ()

    async def create_webhook(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        name: str,
        *,
        avatar: str | None | UndefinedType = UNDEFINED,
        reason: str | UndefinedType = UNDEFINED,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def get_channel_webhooks(
        self,
        authentication: BotAuthentication,
        channel_id: Snowflake,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        list[discord_typings.WebhookData]
            The webhooks in the channel
        """
        route = Route("GET", "/channels/{channel_id}/webhooks", channel_id=channel_id)

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

    async def get_guild_webhooks(
        self,
        authentication: BotAuthentication,
        guild_id: Snowflake,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        list[discord_typings.WebhookData]
            The webhooks in the channel
        """
        route = Route("GET", "/guilds/{guild_id}/webhooks", guild_id=guild_id)

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

    async def get_webhook(
        self,
        authentication: BotAuthentication,
        webhook_id: Snowflake,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        discord_typings.WebhookData
            The webhook that was fetched
        """
        route = Route("GET", "/webhooks/{webhook_id}", webhook_id=webhook_id)

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

    async def get_webhook_with_token(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        *,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        discord_typings.WebhookData
            The webhook that was fetched
        """
        route = Route(
            "GET", "/webhooks/{webhook_id}/{webhook_token}", webhook_id=webhook_id, webhook_token=webhook_token
        )

        r = await self._request(
            route,
            rate_limit_key=None,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_webhook(
        self,
        authentication: BotAuthentication,
        webhook_id: Snowflake,
        *,
        reason: str | UndefinedType = UNDEFINED,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_webhook_with_token(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        *,
        reason: str | UndefinedType = UNDEFINED,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
    ) -> None:
        """Deletes a webhook

        Read the `documentation <https://discord.dev/resources/webhook#delete-webhook-with-token>`__

        Parameters
        ----------
        webhook_id:
            The id of the webhook to delete
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
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def execute_webhook(
        self,
        authentication: BotAuthentication,
        webhook_id: Snowflake,
        webhook_token: str,
        *,
        discord_wait: bool | UndefinedType = UNDEFINED,
        thread_id: Snowflake | UndefinedType = UNDEFINED,
        content: str | UndefinedType = UNDEFINED,
        username: str | UndefinedType = UNDEFINED,
        avatar_url: str | UndefinedType = UNDEFINED,
        tts: bool | UndefinedType = UNDEFINED,
        embeds: list[EmbedData] | UndefinedType = UNDEFINED,
        allowed_mentions: AllowedMentionsData | UndefinedType = UNDEFINED,
        message_reference: MessageReferenceData | UndefinedType = UNDEFINED,
        componenets: list[ActionRowData] | UndefinedType = UNDEFINED,
        sticker_ids: list[int] | UndefinedType = UNDEFINED,
        files: Iterable[File] | UndefinedType = UNDEFINED,
        attachments: list[AttachmentData] | UndefinedType = UNDEFINED,  # TODO: Partial
        flags: int | UndefinedType = UNDEFINED,
        thread_name: str | UndefinedType = UNDEFINED,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
    ) -> MessageData:
        """Sends a message to a webhook

        Read the `documentation <https://discord.dev/resources/webhook#execute-webhook>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        webhook_id:
            The id of the webhook.
        webhook_token:
            The token of the webhook.

            .. warning::
                You should keep this private!
        discord_wait:
            Whether to wait for the message to be fully sent on Discord's end.
        thread_id:
            The id of the thread to post the message in.

            .. warning::
                This will unarchive any thread
        content:
            The content of the message.
        username:
            The name of the user. If not provided this will use the webhook default
        avatar_url:
            The url of the avatar. If not provided this will use the webhook default.
        tts:
            Whether the ``content`` should be spoken out by the Discord client upon send.

            .. note::
                This will still set ``Message.tts`` to :data:`True` even if ``content`` is not provided.
        embeds:
            The embeds to send with the message.

            .. hint::
                The fields are in the `Embed <https://discord.dev/resources/channel#embed-object>`__ documentation.

            .. note::
                There is a maximum 6,000 character limit across all embeds.

                Read the `embed limits documentation <https://discord.dev/resources/channel#embed-object-embed-limits>`__ for more info.
        allowed_mentions:
            The allowed mentions for the message.
        message_reference:
            The message to reply to.
        componenets:
            The components to send with the message.

            .. note::
                The webhook must have been created by a bot for this to work.
        sticker_ids:
            A list of sticker ids to attach to the message.

            .. note::
                This has a max of 3 stickers.
        files:
            The files to send with the message.
        attachments:
            Metadata about the ``files`` parameter.

            .. note::
                This only includes the ``filename`` and ``description`` fields.
        flags:
            Bitwise flags to send with the message.

            .. note::
                Only the ``SUPRESS_EMBEDS`` flag can be set.
        thread_name:
            The name of the thread to create.

            .. warning::
                This can only be provided when the webhook is for a forum channel.
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
            Could not connect due to a problem with your connection.
        UnauthorizedError
            A invalid token was provided.
        NotFoundError
            The channel was not found.
        ForbiddenError
            Missing permissions.
        BadRequestError
            You did not follow the requirements for some parameters.

        Returns
        -------
        discord_typings.MessageData
            The message that was sent.
        """
        route = Route(
            "POST", "/webhooks/{webhook_id}/{webhook_token}", webhook_id=webhook_id, webhook_token=webhook_token
        )
        headers = {"Authorization": str(authentication)}

        params: dict[str, str] = {}
        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if discord_wait is not UNDEFINED:
            params["wait"] = str(discord_wait)
        if thread_id is not UNDEFINED:
            params["thread_id"] = str(thread_id)

        # We use payload_json here as the format is more strictly defined than form data.
        # This means we don't have to manually format the data.
        payload: dict[str, Any] = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if content is not UNDEFINED:
            payload["content"] = content
        if username is not UNDEFINED:
            payload["username"] = username
        if avatar_url is not UNDEFINED:
            payload["avatar_url"] = avatar_url
        if tts is not UNDEFINED:
            payload["tts"] = tts
        if embeds is not UNDEFINED:
            payload["embeds"] = embeds
        if allowed_mentions is not UNDEFINED:
            payload["allowed_mentions"] = allowed_mentions
        if message_reference is not UNDEFINED:
            payload["message_reference"] = message_reference
        if componenets is not UNDEFINED:
            payload["componenets"] = componenets
        if sticker_ids is not UNDEFINED:
            payload["sticker_ids"] = sticker_ids
        if attachments is not UNDEFINED:
            payload["attachments"] = attachments
        if flags is not UNDEFINED:
            payload["flags"] = flags
        if thread_name is not UNDEFINED:
            payload["thread_name"] = thread_name

        # Create a form data response as files cannot be uploaded via json.
        form = FormData()
        form.add_field("payload_json", json_dumps(payload))

        # Add files
        if files is not UNDEFINED:
            for file_id, file in enumerate(files):
                # Content type seems to have no effect here.
                form.add_field(f"file[{file_id}]", file.contents, filename=file.name)

        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers=headers,
            data=form,
            params=params,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    # TODO: @ooliver1 should implement execute slack-compatible webhook
    # TODO: @ooliver1 should implement execute github-compatible webhook

    async def get_webhook_message(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        message_id: Snowflake,
        *,
        thread_id: Snowflake | UndefinedType = UNDEFINED,
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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

        params = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if thread_id is not UNDEFINED:
            params["thread_id"] = thread_id

        r = await self._request(
            route,
            rate_limit_key=None,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
            params=params,
        )

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
        bucket_priority: int = 0,
        global_priority: int = 0,
        wait: bool = True,
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
        bucket_priority:
            The priority of the request for the bucket rate-limiter.
        wait:
            Wait when rate limited.

            This will raise :exc:`RateLimitedError` if set to :data:`False` and you are rate limited.

        Raises
        ------
        RateLimitedError
            You are rate limited, and ``wait`` was set to :data:`False`
        """
        route = Route(
            "DELETE",
            "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}",
            webhook_id=webhook_id,
            webhook_token=webhook_token,
            message_id=message_id,
        )

        params = {}

        # These have different behaviour when not provided and set to None.
        # This only adds them if they are provided (not Undefined)
        if thread_id is not UNDEFINED:
            params["thread_id"] = thread_id

        r = await self._request(
            route,
            rate_limit_key=None,
            bucket_priority=bucket_priority,
            global_priority=global_priority,
            wait=wait,
            params=params,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

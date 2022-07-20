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

from ..route import Route
from .base_client import BaseHTTPClient
from .wrappers import (
    ApplicationCommandsHTTPWrappers,
    AuditLogHTTPWrappers,
    ChannelHTTPWrappers,
    EmojiHTTPWrappers,
    GatewayHTTPWrappers,
    GuildHTTPWrappers,
    GuildScheduledEventHTTPWrappers,
    GuildTemplateHTTPWrappers,
    InviteHTTPWrappers,
    StageInstanceHTTPWrappers,
    StickerHTTPWrappers,
    UserHTTPWrappers,
    VoiceHTTPWrappers,
    WebhookHTTPWrappers,
)

if TYPE_CHECKING:
    from typing import Any, Final

    from discord_typings import ApplicationData

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
    WebhookHTTPWrappers,
    GatewayHTTPWrappers,
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
    # Gateway
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

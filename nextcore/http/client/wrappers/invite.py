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

from ...route import Route
from ..abstract_client import AbstractHTTPClient

if TYPE_CHECKING:
    from typing import Final

    from discord_typings import InviteData

    from ...authentication import BotAuthentication

__all__: Final[tuple[str, ...]] = ("InviteHTTPWrappers",)


class InviteHTTPWrappers(AbstractHTTPClient):
    async def get_invite(
        self, authentication: BotAuthentication, invite_code: str, *, global_priority: int = 0
    ) -> InviteData:
        """Gets a invite from a invite code

        Read the `documentation <https://discord.dev/resources/invite#get-invite>`__

        Parameters
        ----------
        authentication:
            Authentication info.
        invite_code:
            The code of the invite to get
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.InviteData
            The invite that was fetched
        """
        route = Route("GET", "/invites/{invite_code}", invite_code=invite_code)
        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

    async def delete_invite(
        self, authentication: BotAuthentication, invite_code: str, *, global_priority: int = 0
    ) -> InviteData:
        """Gets a invite from a invite code

        Read the `documentation <https://discord.dev/resources/invite#delete-invite>`__

        .. note::
            This requires the ``MANAGE_CHANNELS`` permission in the channel the invite is from or the ``MANAGE_GUILD`` permission.

        .. note::
            This will dispatch a ``INVITE_DELETE`` event.

        Parameters
        ----------
        authentication:
            Authentication info.
        invite_code:
            The code of the invite to delete
        global_priority:
            The priority of the request for the global rate-limiter.

        Returns
        -------
        discord_typings.InviteData
            The invite that was deleted
        """
        route = Route("DELETE", "/invites/{invite_code}", invite_code=invite_code)
        r = await self._request(
            route,
            rate_limit_key=authentication.rate_limit_key,
            headers={"Authorization": str(authentication)},
            global_priority=global_priority,
        )

        # TODO: Make this verify the payload from discord?
        return await r.json()  # type: ignore [no-any-return]

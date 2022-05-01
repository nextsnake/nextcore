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

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from typing_extensions import NotRequired

    from ..common.snowflake import Snowflake
    from ..team import Team
    from .install_params import InstallParams

__all__ = ("Application",)


class Application(TypedDict):
    """An `Application <https://discord.dev/resources/application#application-object-application-structure>`__ object.

    Example payload:

    .. code-block:: json

        {
            "bot_public": true,
            "bot_require_code_grant": false,
            "cover_image": "31deabb7e45b6c8ecfef77d2f99c81a5",
            "description": "Test",
            "guild_id": "290926798626357260",
            "icon": null,
            "id": "172150183260323840",
            "name": "Baba O-Riley",
            "owner": {
                "avatar": null,
                "discriminator": "1738",
                "flags": 1024,
                "id": "172150183260323840",
                "username": "i own a bot"
            },
            "primary_sku_id": "172150183260323840",
            "slug": "test",
            "summary": "This is a game",
            "team": {
                "icon": "dd9b7dcfdf5351b9c3de0fe167bacbe1",
                "id": "531992624043786253",
                "members": [
                    {
                        "membership_state": 2,
                        "permissions": ["*"],
                        "team_id": "531992624043786253",
                        "user": {
                            "avatar": "d9e261cd35999608eb7e3de1fae3688b",
                            "discriminator": "0001",
                            "id": "511972282709709995",
                            "username": "Mr Owner"
                        }
                    }
                ]
            },
            "verify_key": "1e0a356058d627ca38a5c8c9648818061d49e49bd9da9e3ab17d98ad4d6bg2u8"
        }

    Attributes
    ----------
    id: :class:`Snowflake`
        The application's ID.
    name: :class:`str`
        The application's name.
    icon: :class:`str` | :data:`None`
        The application's icon hash.
    description: :class:`str`
        The application's description.
    rpc_origins: list[:class:`str`]
        The application's RPC origin urls if RPC is enabled.
    bot_public: :class:`bool`
        Whether the app's bot can be invited by non-application owners.
    bot_require_code_grant: :class:`bool`
        Whether he app's bot will only join upon completion of the full oauth2 code grant flow
    terms_of_service_url: NotRequired[:class:`str`]
        The application's terms of service.
    privacy_policy_url: NotRequired[:class:`str`]
        The application's privacy policy.
    owner: NotRequired[:class:`PartialUser`]
        The application's owner.
    verify_key: :class:`str`
        The hex encoded key for verification in interactions and the GameSDK's `GetTicket <https://discord.dev/game-sdk/applications#getticket>`__ endpoint.
    team: NotRequired[:class:`Team`]
        The application's team.
    guild_id: NotRequired[:class:`Snowflake`]
        If this application is a game sold on Discord, this field will be the guild to which it has been linked to.
    primary_sku_id: NotRequired[:class:`Snowflake`]
        If this application is a game sold on Discord, this field will be the id of the "Game SKU" that is created, if exists
    slug: NotRequired[:class:`str`]
        If this application is a game sold on Discord, this field will be the URL slug that links to the store page
    cover_image: NotRequired[:class:`str`]
        The application's default rich presence invite cover image hash
    flags: NotRequired[:class:`int`]
        The application's public flags.
    tags: NotRequired[list[:class:`str`]]
        Up to 5 tags describing the content and functionality of the application
    install_params: :class:`InstallParams`
        Settings for the application's default in-app authorization link, if enabled
    custom_install_url: NotRequired[:class:`str`]
        The application's default custom authorization link, if enabled
    """

    # TODO: Link to icon hash fetching docs
    id: Snowflake
    name: str
    icon: str | None
    description: str
    rpc_origins: list[str]
    bot_public: bool
    bot_require_code_grant: bool
    terms_of_service_url: NotRequired[str]
    privacy_policy_url: NotRequired[str]
    owner: NotRequired[PartialUser]  # TODO: Implement PartialUser
    verify_key: str
    team: Team | None  # TODO: Implement Team
    guild_id: NotRequired[Snowflake]
    primary_sku_id: NotRequired[Snowflake]
    slug: NotRequired[str]
    cover_image: NotRequired[str]
    flags: NotRequired[int]  # TODO: Implement bitshift literals for ApplicationFlags
    tags: NotRequired[list[str]]
    install_params: NotRequired[InstallParams]
    custom_install_url: NotRequired[str]

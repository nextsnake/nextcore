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
    from ...common.snowflake import Snowflake
    from .team_member import TeamMember

__all__ = ("Team",)


class Team(TypedDict):
    """A `Team <https://discord.dev/topics/teams#data-models-team-object>`__ object.

    Example payload:

    .. code-block:: json

        {
            "icon": null,
            "id": "881251406189854730",
            "members": [
                {
                    "membership_state": 2,
                    "permissions": ["*"],
                    "team_id": "881251406189854730",
                    "user": {
                        "id": "297045071457681409",
                        "username": "vcokltfre",
                        "discriminator": "6868",
                        "avatar": null
                    }
                }
            ],
            "name": "Nextcord",
            "owner_user_id": "297045071457681409"
        }

    Attributes
    ----------
    icon: :class:`str` | :data:`None`
        The team's icon hash.
    id: :class:`Snowflake`
        The team's ID.
    members: list[:class:`TeamMember`]
        The team's members.
    name: :class:`str`
        The team's name.
    owner_user_id: :class:`Snowflake`
        The team's owner's ID.
    """

    icon: str | None
    id: Snowflake
    members: list[TeamMember]
    name: str
    owner_user_id: Snowflake

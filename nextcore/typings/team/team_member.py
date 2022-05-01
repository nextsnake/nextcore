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
    from .membership_state import MembershipState
    from .team_permission import TeamPermission

__all__ = ("TeamMember",)


class TeamMember(TypedDict):
    """A `Team <https://discord.dev/topics/teams#data-models-team-object>`__ object.

    Attributes
    ----------
    membership_state: :class:`MembershipState`
        The membership state of the user in the :class:`Team`.
    permissions: list[:class:`TeamPermission`]
        The permissions of the user in the :class:`Team`.
    team_id: :class:`Snowflake`
        The ID of the :class:`Team` this :class:`TeamMember` is a member of.
    """

    membership_state: MembershipState
    permissions: list[TeamPermission]
    team_id: Snowflake
    user: TeamPartialUser  # TODO: Make TeamPartialUser

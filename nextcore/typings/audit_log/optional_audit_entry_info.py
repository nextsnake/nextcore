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
    from typing import Literal

    from typing_extensions import NotRequired

    from ..common import Snowflake


class OptionalAuditEntryInfo(TypedDict):
    """A `optional audit entry info <https://discord.com/developers/docs/resources/audit-log#audit-log-entry-object-optional-audit-entry-info>`__ object.

    Attributes
    ----------
    channel_id: NotRequired[:class:`Snowflake`]
        The ID of the channel in which the entities were targeted

        .. note::
            This is only present in ``MEMBER_MOVE``, ``MESSAGE_PIN``, ``MESSAGE_UNPIN``, ``MESSAGE_DELETE``, ``STAGE_INSTANCE_CREATE``, ``STAGE_INSTANCE_UPDATE`` and ``STAGE_INSTANCE_DELETE`` :class:`AuditLogChangeKey's <AuditLogChangeKey>`.
    count: NotRequired[:class:`str`]
        A :class:`str` representation of a :class:`int` of the number of entities that were targeted.

        .. note::
            This is only present in ``MESSAGE_DELETE``, ``MESSAGE_BULK_DELETE``, ``MEMBER_DISCONNECT`` and ``MEMBER_MOVE`` :class:`AuditLogChangeKey's <AuditLogChangeKey>`.
    delete_member_days: NotRequired[:class:`str`]
        A :class:`str` representation of a :class:`int` of the number of days after which inactive members were kicked.

        .. note::
            This is only present in ``MEMBER_PRUNE`` :class:`AuditLogChangeKey's <AuditLogChangeKey>`.
    id: NotRequired[:class:`Snowflake`]
        The ID of the entity that was modified.

        .. note::
            This is only present in ``CHANNEL_OVERWRITE_CREATE``, ``CHANNEL_OVERWRITE_UPDATE`` and ``CHANNEL_OVERWRITE_DELETE`` :class:`AuditLogChangeKey's <AuditLogChangeKey>`.
    members_removed: NotRequired[:class:`str`]
        A :class:`str` representation of a :class:`int` of the number of members that were removed.

        .. note::
            This is only present in ``MEMBER_PRUNE`` :class:`AuditLogChangeKey's <AuditLogChangeKey>`.
    message_id: NotRequired[:class:`Snowflake`]
        The ID of the message that was targeted.

        .. note::
            This is only present in ``MESSAGE_PIN`` and ``MESSAGE_UNPIN`` :class:`AuditLogChangeKey's <AuditLogChangeKey>`.
    role_name: NotRequired[:class:`str`]
        The name of the role that was targeted.

        .. note::
            This is only present in ``CHANNEL_OVERWRITE_CREATE``, ``CHANNEL_OVERWRITE_UPDATE`` and ``CHANNEL_OVERWRITE_DELETE`` :class:`AuditLogChangeKey's <AuditLogChangeKey>`.

            This also required :attr:`OptionalAuditEntryInfo.type` to be ``0``.
    type: NotRequired[Literal["0", "1"]]
        The type of overwritten entity.

        Possible values
            - ``0`` :class:`Role`
            - ``1`` :class:`GuildMember`
    """

    channel_id: NotRequired[Snowflake]
    count: NotRequired[str]
    delete_member_days: NotRequired[str]
    id: Snowflake
    members_removed: NotRequired[str]
    message_id: NotRequired[Snowflake]
    role_name: NotRequired[str]
    type: NotRequired[Literal["0", "1"]]

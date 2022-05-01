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

    from ..common import Snowflake
    from .audit_log_change import AuditLogChange
    from .audit_log_event import AuditLogEvent
    from .optional_audit_entry_info import OptionalAuditEntryInfo

__all__ = ("AuditLogEntry",)


class AuditLogEntry(TypedDict):
    """A `Audit log entry <https://discord.dev/resources/audit-log#audit-log-entry-object-audit-log-entry-structure>`__ object

    Attributes
    ----------
    target_id: :class:`Snowflake` | :data:`None`
        The ID this entry is affecting.

        This can either be a :attr:`Webhook.id`, :attr:`Channel.id`, :attr:`Guild.id`, :attr:`User.id`, or :attr:`Role.id` etc.
    changes: NotRequired[list[:class:`AuditLogChange`]]
        A list of changes made to the target.
    user_id: :class:`Snowflake` | :data:`None`
        The ID of the user who made the change.
    id: :class:`Snowflake`
        The ID of the audit log entry.
    action_type: :class:`AuditLogEvent`
        The type of action that was taken.
    options: NotRequired[:class:`AuditLogEntryInfo`]
        Additional information about the action.
    reason: :class:`str` | :data:`None`
        The reason for the action.

        This is a 0-512 character string.
    """

    target_id: Snowflake | None
    changes: NotRequired[list[AuditLogChange]]
    user_id: Snowflake | None
    id: Snowflake
    action_type: AuditLogEvent
    options: NotRequired[OptionalAuditEntryInfo]
    reason: NotRequired[str]

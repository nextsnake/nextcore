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
    from .audit_log_entry import AuditLogEntry

__all__ = ("AuditLog",)


class AuditLog(TypedDict):
    """A `Audit Log <https://discord.dev/resources/audit-log>`__ object.

    Attributes
    ----------
    audit_log_entries: list[:class:`AuditLogEntry`]
        The entries in the audit log.
    guild_scheduled_events: list[:class:`GuildScheduledEvent`]
        A list of scheduled events referenced in the :attr:`AuditLog.audit_log_entries` entries.
    integrations: list[:class:`Integration`]
        A list of integrations referenced in the :attr:`AuditLog.audit_log_entries` entries.
    threads: list[:class:`Channel`]
        A list of threads referenced in the :attr:`AuditLog.audit_log_entries` entries.
    users: list[:class:`User`]
        A list of users referenced in the :attr:`AuditLog.audit_log_entries` entries.
    webhooks: list[:class:`Webhook`]
        A list of webhooks referenced in the :attr:`AuditLog.audit_log_entries` entries.
    """

    audit_log_entries: list[AuditLogEntry]
    guild_scheduled_events: list[GuildScheduledEvent]  # TODO: Implement GuildScheduledEvent
    integrations: list[Integration]  # TODO: Implement Integration
    threads: list[Channel]  # TODO: Implement Channel TODO: Maybe implement Thread?
    users: list[User]  # TODO: Implement User
    webhooks: list[Webhook]  # TODO: Implement Webhook

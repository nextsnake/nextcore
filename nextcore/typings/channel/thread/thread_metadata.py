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

    from .auto_archive_duration import AutoArchiveDuration

__all__ = ("ThreadMetadata",)


class ThreadMetadata(TypedDict):
    """A `Thread Metadata <https://discord.dev/resources/channel#thread-metadata-object-thread-metadata-structure>`__ object

    Attributes
    ----------
    archived: :class:`bool`
        Whether the thread is archived
    auto_archive_duration: :class:`AutoArchiveDuration`
        The duration after which the thread will be automatically archived after no activity
    archive_timestamp: :class:`str`
        The ISO 8601 timestamp of when the archive status was last changed. This is used by Discord to determine when to archive the thread automatically.
    locked: :class:`bool`
        Whether the thread is locked. This will restrict members without the ``MANAGE_THREADS`` permission from unarchiving the thread.
    invitable: NotRequired[:class:`bool`]
        Whether members without the ``MANAGE_THREADS`` permission can invite other members without the ``MANAGE_CHANNELS`` permission to the thread.

        .. note::
            This only affects private threads.
        .. note::
            This should not be present in public threads.
    create_timestamp: NotRequired[:class:`str` | :data:`None`]
        The ISO 8601 timestamp of when the thread was created.

        .. note::
            This will be :data:`None` for any thread created before 2022-01-09.
    """

    archived: bool
    auto_archived_duration: AutoArchiveDuration
    archive_timestamp: str
    locked: bool
    invitable: NotRequired[bool]
    create_timestamp: NotRequired[str | None]

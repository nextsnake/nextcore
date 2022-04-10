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

if TYPE_CHECKING:
    from typing import TypedDict

    from typing_extensions import NotRequired

    from .auto_archive_duration import AutoArchiveDuration

    class ThreadMember(TypedDict):
        """Typings for the `ThreadMember <https://discord.dev/resources/channel#thread-metadata-object>`__ object.

        Attributes
        ----------
        archived: :class:`bool`
            Whether the thread is archived.
        auto_archive_duration: :class:`AutoArchiveDuration`
            How long it takes for the thread to be archived automatically by the API after the last message is sent.
        archive_timestamp: :class:`str`
                ISO8601 timestamp of when the thread's archive status was last changed.
        locked: :class:`bool`
            Whether the thread is locked. This means only members with the :attr:`Permission.manage_threads` can unarchive the thread.

            .. note::
                A thread can be locked even if it is not archived. This will result in the thread being properly locked once it gets archived.
        invitable: NotRequired[:class:`bool` | :data:`None`]
            Whether members without :attr:`Permission.manage_threads` can invite other users to the thread.

            .. note::
                This is only available for private threads.
        create_timestamp: NotRequired[:class:`str` | :data:`None`]
            ISO8601 timestamp of when the thread was created.

            .. note::
                If the thread was created before 2022-01-09, this will be :data:`None`.
        """

        archived: bool
        auto_archive_duration: AutoArchiveDuration
        archive_timestamp: str
        locked: bool
        invitable: NotRequired[bool]
        create_timestamp: NotRequired[str | None]

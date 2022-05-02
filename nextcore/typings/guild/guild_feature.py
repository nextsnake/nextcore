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

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

__all__ = ("GuildFeature",)

# Not documented here due to Sphinx.
# This is documented manually in the docs/typings.rst file.
GuildFeature: TypeAlias = Literal[
    "ANIMATED_BANNER",  # guild has access to set an animated guild banner image
    "ANIMATED_ICON",  # guild has access to set an animated guild icon
    "BANNER",  # guild has access to set a guild banner image
    "COMMERCE",  # guild has access to use commerce features (i.e. create store channels)
    "COMMUNITY",  # guild can enable welcome screen, Membership Screening, stage channels and discovery, and receives community updates
    "DISCOVERABLE",  # guild is able to be discovered in the directory
    "FEATURABLE",  # guild is able to be featured in the directory
    "INVITE_SPLASH",  # guild has access to set an invite splash background
    "MEMBER_VERIFICATION_GATE_ENABLED",  # guild has enabled Membership Screening
    "MONETIZATION_ENABLED",  # guild has enabled monetization
    "MORE_STICKERS",  # guild has increased custom sticker slots
    "NEWS",  # guild has access to create news channels
    "PARTNERED",  # guild is partnered
    "PREVIEW_ENABLED",  # guild can be previewed before joining via Membership Screening or the directory
    "PRIVATE_THREADS",  # guild has access to create private threads
    "ROLE_ICONS",  # guild is able to set role icons
    "SEVEN_DAY_THREAD_ARCHIVE",  # guild has access to the seven day archive time for threads
    "THREE_DAY_THREAD_ARCHIVE",  # guild has access to the three day archive time for threads
    "TICKETED_EVENTS_ENABLED",  # guild has enabled ticketed events
    "VANITY_URL",  # guild has access to set a vanity URL
    "VERIFIED",  # guild is verified
    "VIP_REGIONS",  # guild has access to set 384kbps bitrate in voice (previously VIP voice servers)
    "WELCOME_SCREEN_ENABLED",  # guild has enabled the welcome screen
]

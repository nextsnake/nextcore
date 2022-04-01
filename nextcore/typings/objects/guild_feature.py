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
    from typing import Literal

    GuildFeature = Literal[
        "ANIMATED_ICON",  # Guild has access to set a custom animated icon.
        "BANNER",  # Guild has access to set a custom banner.
        "COMMERCE",  # Guild has access to use commerce features. (create store channels)
        "COMMUNITY",  # Guild can enable welcome screen, Membership Screening, stage channels and discovery, and receives community updates
        "DISCOVERABLE",  # Guild can be discovered by users in discovery
        "FEATURABLE",  # Guild can be featured in discovery
        "INVITE_SPLASH",  # Guild can set an invite splash.
        "MEMBER_VERIFICATION_GATE_ENABLED",  # Guild has enabled Membership screening
        "MONETIZATION_ENABLED",  # Guild has enabled monetization
        "MORE_STICKERS",  # Guild has increased custom sticker slots
        "NEWS",  # Guild has access to create news channels
        "PARTNERED",  # Guild is partnered
        "PREVIEW_ENABLED",  # guild can be previewed before joining via Membership Screening or the directory
        "PRIVATE_THREADS",  # Guild has access to create private threads
        "ROLE_ICONS",  # Guild has access to set custom role icons
        "SEVEN_DAY_THREAD_ARCHIVE",  # Guild can set a 7-day thread archive
        "THREE_DAY_THREAD_ARCHIVE",  # Guild can set a 3-day thread archive
        "TICKETED_EVENTS_ENABLED",  # Guild has enabled ticketed events
        "VANITY_URL",  # Guild has access to set a vanity URL
        "VERIFIED",  # Guild is verified
        "VIP_REGIONS",  # Guild can set 384kbps voice bitrate
        "WELCOME_SCREEN_ENABLED",  # Guild has enabled welcome screen
    ]

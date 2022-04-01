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

    class ActivityAssets(TypedDict):
        """Typings for the `ActivityAssets <https://discord.dev/topics/gateway#activity-object-activity-assets>`__ object.

        Attributes
        ----------
        large_image: :class:`str`
            The large image asset id. This can be served from https://cdn.discordapp.com/app-assets/:attr`Application.id`/asset_id.png
        large_text: :class:`str`
            The large alt/hover text.
        small_image: :class:`str`
            The small image asset id. This can be served from https://cdn.discordapp.com/app-assets/:attr`Application.id`/asset_id.png
        small_text: :class:`str`
            The small alt/hover text.
        """

        large_image: NotRequired[str]
        large_text: NotRequired[str]
        small_image: NotRequired[str]
        small_text: NotRequired[str]

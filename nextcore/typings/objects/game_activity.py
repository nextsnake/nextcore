# The MIT License (MIT)
# Copyright (c) 2021-present nextsnake developers

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

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
    from typing_extensions import NotRequired

    from .activity import Activity
    from .activity_assets import ActivityAssets
    from .activity_button import ActivityButton
    from .activity_party import ActivityParty
    from .activity_secrets import ActivitySecrets

    class GameActivty(Activity):
        application_id: str
        """The application ID of the game."""
        details: str
        """What the player is currently doing."""
        state: str | None
        """The current party status."""
        party: ActivityParty
        """Information about the party."""
        assets: ActivityAssets
        """Asset IDs"""
        secrets: ActivitySecrets
        """Secrets for joining the party/game"""
        instance: NotRequired[bool]
        """Whether the activity is a instanced game session."""
        flags: NotRequired[int]  # TODO: Is this actually required?
        """Flags for the activity."""
        buttons: list[ActivityButton] | list[str]
        """A list of button labels if received, a list of buttons if sending"""

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
    from typing import Literal, TypedDict

    from typing_extensions import NotRequired

    from .locale import Locale

    class User(TypedDict):
        """A Discord user.

        Attributes
        ----------
        id: :class:`int`
            The user's ID.
        username: :class:`str`
            The user's username.
        discriminator: :class:`str`
            The user's discriminator.
        avatar: :class:`str`
            The user's avatar hash.
        bot: NotRequired[:class:`bool`]
            Whether the user is a bot.
        system: NotRequired[:class:`bool`]
            Whether the user is a system user.
        mfa_enabled: NotRequired[:class:`bool`]
            Whether the user has two factor enabled on their account.
        banner: NotRequired[:class:`str`]
            The user's banner hash.
        accent_color: NotRequired[:class:`str`]
            The user's default banner color encoded as a hex string.
        locale: NotRequired[:class:`str`]
            The user's chosen language.
        verified: NotRequired[:class:`bool`]
            Whether the email on this account has been verified.
        email: NotRequired[:class:`str`]
            The user's email.
        flags: NotRequired[:class:`int`]
            The user's flags.
        premium_type: NotRequired[:data:`typing.Literal[0, 1, 2]`]
            The user's type of Nitro subscription.
        public_flags: NotRequired[:class:`int`]
            The user's public flags.
        """

        id: int
        username: str
        discriminator: str
        avatar: str
        bot: NotRequired[bool]
        system: NotRequired[bool]
        mfa_enabled: NotRequired[bool]
        banner: NotRequired[str]
        accent_color: NotRequired[str]
        locale: NotRequired[Locale]
        verified: NotRequired[bool]
        email: NotRequired[str]
        flags: NotRequired[int]
        premium_type: NotRequired[Literal[0, 1, 2]]
        public_flags: NotRequired[int]

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

from base64 import b64decode

from .time_utils import DISCORD_TOKEN_EPOCH


def extract_token_info(token: str) -> tuple[int, int, str]:
    """Extract metadata from a Discord token.

    Parameters
    ----------
    token: :class:`str`
        The Discord token to extract metadata from.

    Returns
    -------
    tuple[:class:`int`, :class:`int`, :class:`str`]
        A tuple containing the bots ID,
        the UNIX timestamp of when token was created
        and a cryptographic signature from Discord confirming this is a valid token.
    """
    token_info = token.split(".")

    if len(token_info) != 3:
        raise ValueError("Invalid token format")

    bot_id = int(b64decode(token_info[0]).decode("utf-8"))
    created_at = DISCORD_TOKEN_EPOCH + int(b64decode(token_info[1]).decode("utf-8"))
    hmac_signature = token_info[2]

    return bot_id, created_at, hmac_signature

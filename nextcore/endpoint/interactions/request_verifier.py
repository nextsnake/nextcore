# The MIT License (MIT)
# Copyright (c) 2021-present tag-epic
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

from logging import getLogger
from typing import TYPE_CHECKING

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

if TYPE_CHECKING:
    from typing import Final

logger = getLogger(__name__)


class RequestVerifier:
    """Helper class to verify requests from Discord

    Parameters
    ----------
    public_key:
        The public key from the developer portal. This can be a hex :class:`str`, or the hex :class:`str` converted to bytes.

        This will be converted to :class:`bytes` under the hood.
    """

    __slots__: Final[tuple[str, ...]] = ("verify_key",)

    def __init__(self, public_key: str | bytes) -> None:
        if isinstance(public_key, str):
            public_key = bytes.fromhex(public_key)

        self.verify_key: Final[VerifyKey] = VerifyKey(public_key)

    def is_valid(self, signature: str | bytes, timestamp: str, body: str) -> bool:
        """Check if a request was made by Discord

        Parameters
        ----------
        signature:
            The signature from the ``X-Signature-Ed25519`` header. This can either be the raw header (a hex encoded :class:`str`) or it converted to :class:`bytes`.

        Returns
        -------
        bool
            If the signature was made from Discord.

            If this is :data:`False` you should reject the request with a ``401`` status code.
        """

        if isinstance(signature, str):
            try:
                signature = bytes.fromhex(signature)
            except ValueError:
                logger.debug("Request did not pass check because of signature not being valid HEX")
                return False

        payload = f"{timestamp}{body}".encode()
        try:
            self.verify_key.verify(payload, signature)
        except BadSignatureError:
            logger.debug("Request did not pass check because of verify_key.verify")
            return False
        except ValueError:
            logger.debug("Request did not pass check because of ValueError. This is probably due to wrong length")
            return False

        return True

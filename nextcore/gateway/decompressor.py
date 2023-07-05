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

from typing import TYPE_CHECKING
from zlib import decompressobj
from zlib import error as zlib_error

if TYPE_CHECKING:
    from typing import ClassVar, Final

__all__: Final[tuple[str, ...]] = ("Decompressor",)


class Decompressor:
    """A wrapper around zlib to handle partial payloads

    **Example usage**

    .. code-block::

        from nextcore.gateway import Decompressor

        decompressor = Decompressor()

        data = decompressor.decompress(zlib_data) # bytes from the Discord gateway

        print(data.decode("utf-8"))
    """

    ZLIB_SUFFIX: ClassVar[bytes] = b"\x00\x00\xff\xff"

    __slots__ = ("_decompressor", "_buffer")

    def __init__(self) -> None:
        self._decompressor = decompressobj()
        self._buffer: bytearray = bytearray()

    def decompress(self, data: bytes) -> bytes | None:
        """Decompress zlib data.

        **Example usage:**

        .. code-block::
            :emphasize-lines: 5

            from nextcore.gateway import Decompressor

            decompressor = Decompressor()

            data = decompressor.decompress(zlib_data) # bytes from the Discord gateway

            print(data.decode("utf-8"))


        Parameters
        ----------
        data:
            The zlib compressed bytes.

        Returns
        -------
        :class:`bytes` | :data:`None`:
            The decompressed data.

            This is :data:`None` if this is a partial payload.

        Raises
        ------
        :exc:`ValueError`:
            This is not zlib compressed data. The data could also be corrupted.
        """
        self._buffer.extend(data)

        if len(data) < 4 or data[-4:] != Decompressor.ZLIB_SUFFIX:
            # Not a full payload, try again next time
            return None

        try:
            data = self._decompressor.decompress(data)
        except zlib_error:
            raise ValueError("Data is corrupted. Please void all zlib context.") from None

        # If successful, clear the pending data.
        self._buffer.clear()
        return data

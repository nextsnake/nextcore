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
    from typing import BinaryIO, Final, TextIO
    from typing import Union # pylint: disable=outdated-typing-union
    from typing_extensions import TypeAlias

    Contents: TypeAlias = Final[Union[str, bytes, bytearray, BinaryIO, TextIO]]

__all__ = ("File",)

# This is not a attr.dataclass because it does not support slots.
class File:
    """A utility class for uploading files to the API.

    Parameters
    ----------
    name:
        The name of the file.

        .. warning::
            Only files ending with a `supported file extension <https://discord.dev/reference#image-formatting-image-formats>`__ can be included in embeds.
    contents:
        The contents of the file.

    Attributes
    ----------
    name:
        The name of the file.

        .. warning::
            Only files ending with a `supported file extension <https://discord.dev/reference#image-formatting-image-formats>`__ can be included in embeds.
    contents:
        The contents of the file.
    """

    __slots__ = ("name", "contents")

    def __init__(self, name: str, contents: Contents):
        self.name: Final[str] = name
        self.contents: Contents = contents

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

if TYPE_CHECKING:
    from typing import Final

__all__: Final[tuple[str, ...]] = ("BucketMetadata",)


class BucketMetadata:
    """Metadata about a discord bucket.

    **Example usage**

    .. code-block:: python3

        bucket_metadata = BucketMetadata()
        bucket = Bucket(bucket_metadata)

        async with bucket.acquire():
            ...

            bucket_metadata.limit = 5 # This can be found in the response headers from discord.
            bucket_metadata.unlimited = False

    Parameters
    ----------
    limit:
        The maximum number of requests that can be made in the given time period.
    unlimited:
        Whether the bucket has an unlimited number of requests. If this is :class:`True`,
        limit has to be None.

    Attributes
    ----------
    limit:
        The maximum number of requests that can be made in the given time period.

        .. note::
            This will be :data:`None` if :attr:`BucketMetadata.unlimited` is :data:`True`.

            This will also be :data:`None` if no limit has been fetched yet.
    unlimited:
        Wheter the bucket has no rate limiting enabled.
    """

    __slots__ = ("limit", "unlimited")

    def __init__(self, limit: int | None = None, *, unlimited: bool = False) -> None:
        self.limit: int | None = limit
        self.unlimited: bool = unlimited

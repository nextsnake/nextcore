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

    from ..http.json_error import JSONError

    # TODO: These names really suck however I can't see any "official" names discord calls them by?
    # Would really like some better ideas.

    class InnerError(TypedDict):
        """Error contained inside :class:`ErrorOverview` containing one spesific error.

        Attributes
        ----------
        code: :class:`str`
            The error code. This is not the status code.
        """

        code: str  # TODO: If discord decides to change their mind and document this
        message: str

    class ErrorOverview(TypedDict):
        # TODO: Docstring
        """ """

        _errors: list[InnerError]

    class HTTPError(TypedDict):
        """A discord HTTP error

        See the `documentation <https://discord.dev/topics/reference#error-messages>`__

        Attributes
        ----------
        code: :class:`int`
            The error code. This is not the status code. See the `list <https://discord.dev/topics/opcodes-and-status-codes#json-json-error-codes>`__
        """

        code: JSONError
        message: str
        errors: ErrorOverview | dict[str, ErrorOverview | dict[str, ErrorOverview]]

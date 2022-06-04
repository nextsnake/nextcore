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
    from typing import Dict  # pylint: disable=outdated-typing-dict
    from typing import List  # pylint: disable=outdated-typing-list
    from typing import Union  # pylint: disable=outdated-typing-union

    from typing_extensions import TypeAlias

    JsonCompatible: TypeAlias = Union[
        str, int, float, None, Dict[Union[str, int, float, None], "JsonCompatible"], List["JsonCompatible"]
    ]

try:
    import orjson

    _has_orjson: bool = True
except ImportError:
    import json

    _has_orjson = False


__all__ = ("json_loads", "json_dumps")


def json_loads(data: str) -> JsonCompatible:
    """Loads a json string into a python object.

    Parameters
    ----------
    data:
        The json string to load.

    Raises
    ------
    :exc:`ValueError`
        The text provided is not valid json
    :exc:`TypeError`
        data must be a :class:`str`
    """
    if _has_orjson:
        return orjson.loads(data)
    return json.loads(data)


def json_dumps(to_dump: JsonCompatible) -> str:
    """Dumps a python object into a json string.

    Parameters
    ----------
    to_dump:
        The python object to dump.
    """
    if _has_orjson:
        return orjson.dumps(to_dump).decode("utf-8")
    return json.dumps(to_dump)

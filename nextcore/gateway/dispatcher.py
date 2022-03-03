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

from asyncio import get_event_loop
from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable

    async_coro = Callable[..., Awaitable[Any]]


class Dispatcher:
    __slots__ = ("_global_listeners", "_listeners")

    def __init__(self) -> None:
        self._global_listeners: list[async_coro] = []
        self._listeners: defaultdict[Any, list[async_coro]] = defaultdict(list)

    def dispatch(self, event_name: Any, *event_args: Any) -> None:
        loop = get_event_loop()
        for listener in self._global_listeners:
            loop.create_task(self._dispatch_maybe_predicate(listener, event_name, *event_args))
        for listener in self._listeners[event_name]:
            loop.create_task(self._dispatch_maybe_predicate(listener, *event_args))

    async def _dispatch_maybe_predicate(
        self, listener: async_coro | tuple[Callable[..., Awaitable[bool]], async_coro], *args: Any
    ) -> None:
        if isinstance(listener, tuple):
            predicate, listener = listener
            if not await predicate(*args):
                # Condition was not met, try again next time
                return
            self.remove_listener(listener)
            await listener(*args)
        else:
            await listener(*args)

    def add_listener(self, listener: async_coro, event_name: Any = None) -> None:
        if event_name is None:
            self._global_listeners.append(listener)
        else:
            self._listeners[event_name].append(listener)

    def remove_listener(self, listener: async_coro) -> None:
        if listener in self._global_listeners:
            self._global_listeners.remove(listener)
            return
        for listeners in self._listeners.values():
            if listener in listeners:
                listeners.remove(listener)
                return

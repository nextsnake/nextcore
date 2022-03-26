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

from asyncio import Future
from asyncio import TimeoutError as AsyncioTimeoutError
from asyncio import create_task, wait_for
from collections import defaultdict
from logging import getLogger
from typing import TYPE_CHECKING

from ..utils import maybe_coro

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable

logger = getLogger(__name__)

__all__ = ("Dispatcher",)


class Dispatcher:
    """A event dispatcher"""

    __slots__ = (
        "_exception_handlers",
        "_listeners",
        "_global_listeners",
        "_wait_for_listeners",
        "_wait_for_global_listeners",
    )

    def __init__(self) -> None:
        # Exception handler
        self._exception_handlers: list[Callable[[Exception], Any]] = []

        self._listeners: defaultdict[Any, list[Callable[..., Any]]] = defaultdict(list)
        self._global_listeners: list[Callable[[Any, *Any], Any]] = []

        # Conditional listeners are listeners which can only be called once and that also has a check.
        self._wait_for_listeners: defaultdict[
            Any, list[tuple[Callable[..., Awaitable[bool] | bool], Future[list[Any]]]]
        ] = defaultdict(list)
        self._wait_for_global_listeners: list[
            tuple[Callable[[Any, *Any], Awaitable[bool] | bool], Future[list[Any]]]
        ] = []

    def add_listener(self, callback: Callable[..., Any], event_name: Any = None) -> None:
        """Adds a listener to the dispatcher.

        Parameters
        ----------
        callback: typing.Callable[..., :data:`typing.Any`]
            The callback to be added.
        event_name: :data:`typing.Any`
            The event name to listen to. If:class:`None`, the callback will receive all events. Global listeners will also receive the event name as the first param.
        """
        logger.debug("Adding listener for event %s", event_name)
        if event_name is None:
            self._global_listeners.append(callback)
        else:
            self._listeners[event_name].append(callback)

    async def wait_for(
        self, check: Callable[..., Awaitable[bool] | bool], event_name: Any = None, *, timeout: float | None = None
    ) -> list[Any]:
        """Waits for an event to be dispatched and returns it if it matches a check.

        Parameters
        ----------
        check: typing.Callable[..., typing.Awaitable[:class:`bool`] | :class:`bool`]
            The check to check if it should return the event.
        event_name: :data:`typing.Any`
            The event name to wait for. If :class:`None`, the check will be called for all events. The check will receive the event name as the first param.
        timeout: :class:`float` | :data:`None`
            The timeout in seconds. If :class:`None`, there is no timeout.

        Returns
        -------
        list[:data:`typing.Any`]
            The event arguments.
        """

        future: Future[list[Any]] = Future()

        if event_name is None:
            self._wait_for_global_listeners.append((check, future))
        else:
            self._wait_for_listeners[event_name].append((check, future))
        try:
            result: list[Any] = await wait_for(future, timeout)
        except AsyncioTimeoutError:
            # Timeout reached, remove the listener
            if event_name is None:
                self._wait_for_global_listeners.remove((check, future))
            else:
                self._wait_for_listeners[event_name].remove((check, future))
            raise

        # Success!
        return result

    def remove_listener(self, callback: Callable[..., Any]) -> None:
        """Removes a listener from the dispatcher.

        Parameters
        ----------
        callback: Callable[..., :data:`typing.Any`]
            The callback to be removed.

        Raises
        ------
        :class:`ValueError`
            The callback was not registered on this dispatcher.
        """
        for listeners in self._listeners.values():
            if callback in listeners:
                listeners.remove(callback)
                return
        if callback in self._global_listeners:
            self._global_listeners.remove(callback)
            return
        raise ValueError("There is no such listener in this dispatcher")

    def dispatch(self, event_name: Any, *event_args: Any) -> None:
        """Dispatches an event to all listeners watching that event.

        Parameters
        ----------
        event_name: :data:`typing.Any`
            The event name to dispatch.
        event_args: :data:`typing.Any`
            The event arguments.
        """
        logger.debug("Dispatching event %s", event_name)

        # Regular listeners
        for listener in self._global_listeners:
            # Global listeners
            create_task(
                self._dispatch_event_wrapper(listener, event_name, *event_args),
                name=f"nextcord:Dispatch listener {event_name} (global)",
            )
        for listener in self._listeners.get(event_name, []):
            # Per event listeners
            create_task(
                self._dispatch_event_wrapper(listener, *event_args), name=f"nextcord:Dispatch listener {event_name}"
            )

        # Wait for listeners
        for info in self._wait_for_global_listeners:
            # Global wait for listeners
            create_task(
                self._dispatch_wait_for(*info, event_name, *event_args),
                name=f"nextcord:Dispatch wait_for listener {event_name} (global)",
            )
        for info in self._wait_for_listeners.get(event_name, []):
            # Per event wait for listeners
            create_task(
                self._dispatch_wait_for(*info, *event_args), name=f"nextcord:Dispatch wait_for listener {event_name}"
            )

    async def _dispatch_event_wrapper(self, listener: Callable[..., Any], *event_args: Any) -> None:
        try:
            await maybe_coro(listener, *event_args)
        except Exception as e:
            for exception_handler in self._exception_handlers:
                try:
                    await maybe_coro(exception_handler, e)
                except:
                    logger.error("Exception handler failed", exc_info=True)

    async def _dispatch_wait_for(
        self, check: Callable[..., Awaitable[bool] | bool], future: Future[list[Any]], event_name: Any, *event_args: Any
    ) -> None:
        try:
            check_success = await maybe_coro(check)
        except:
            logger.error("Exception in wait_for check", exc_info=True)
            return
        if not check_success:
            # Check failed, try again on next event.
            return

        # Check succeeded, resolve and remove the listener.
        # Release future
        future.set_result([event_name, *event_args])
        logger.debug(future)

        # Remove listener
        # TODO: Could this be simplified?
        for info in self._wait_for_listeners.get(event_name, []):
            if info[1] is future:
                # 0th is the check, 1st is the future
                self._wait_for_listeners[event_name].remove(info)
                return
        for info in self._wait_for_global_listeners:
            if info[1] is future:
                # 0th is the check, 1st is the future
                self._wait_for_global_listeners.remove(info)

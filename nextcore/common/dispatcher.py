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

from asyncio import CancelledError, Future, create_task
from collections import defaultdict
from logging import getLogger
from typing import (  # pylint: disable=outdated-typing-any
    TYPE_CHECKING,
    Generic,
    Hashable,
    TypeVar,
    cast,
    overload,
)

from ..utils import maybe_coro

# Types
EventNameT = TypeVar("EventNameT", bound=Hashable)

if TYPE_CHECKING:
    from typing import (  # pylint: disable=outdated-typing-union
        Any,
        Awaitable,
        Callable,
        Union,
        Tuple
    )
    from typing_extensions import Unpack

    T = TypeVar("T")

    ManyT = Tuple[T, ...]

    EventCallback = Callable[[Unpack[ManyT[Any]]], Any]
    GlobalEventCallback = Callable[[EventNameT, Unpack[ManyT[Any]]], Any]

    WaitForCheck = Callable[[Unpack[ManyT[Any]]], Union[Awaitable[bool], bool]]
    GlobalWaitForCheck = Callable[[EventNameT, Unpack[ManyT[Any]]], Union[Awaitable[bool], bool]]
    WaitForReturn = Union[Tuple[EventNameT, Unpack[ManyT[Any]]], Tuple[Unpack[ManyT[Any]]]]

    ExceptionHandler = Callable[[Exception], Any]
    GlobalExceptionHandler = Callable[[EventNameT, Exception], Any]

logger = getLogger(__name__)

__all__ = ("Dispatcher",)


class Dispatcher(Generic[EventNameT]):
    """A event dispatcher

    Example usage:

    .. code-block:: python

        dispatcher: Dispatcher[str] = Dispatcher()

        @dispatcher.listen("join")
        async def join_handler(username: str) -> None:
            print(f"Welcome {username}")

        await dispatcher.dispatch("join", "John")
    """

    def __init__(self):
        self._event_handlers: defaultdict[EventNameT, list[EventCallback]] = defaultdict(list)
        self._global_event_handlers: list[GlobalEventCallback[EventNameT]] = []

        self._wait_for_handlers: dict[EventNameT, list[tuple[WaitForCheck, Future[tuple[Any, ...]]]]] = defaultdict(
            list
        )
        self._global_wait_for_handlers: list[tuple[GlobalWaitForCheck[EventNameT], Future[tuple[Any, ...]]]] = []

        self._global_exception_handlers: list[GlobalExceptionHandler[EventNameT]] = []
        self._exception_handlers: defaultdict[EventNameT, list[ExceptionHandler]] = defaultdict(list)

    # Registration
    @overload
    def listen(self, event_name: EventNameT) -> Callable[[EventCallback], EventCallback]:
        ...

    @overload
    def listen(self, event_name: None = None) -> Callable[[GlobalEventCallback[EventNameT]], GlobalEventCallback[EventNameT]]:
        ...

    def listen(
        self, event_name: EventNameT | None = None
    ) -> Callable[[EventCallback], EventCallback] | Callable[
        [GlobalEventCallback[EventNameT]], GlobalEventCallback[EventNameT]
    ]:
        """Decorator to register a event listener.

        Example usage:

        .. code-block:: python
            
            @dispatcher.listen("join")
            async def join_handler(username: str) -> None:
                print(f"Welcome {username}")

        Parameters
        ----------
        event_name: :class:`EventNameT` | :data:`None`
            The event name to register the listener to. If this is :data:`None`, the listener is considered a global event.
        """
        @overload
        def decorator(callback: EventCallback) -> EventCallback:
            ...

        @overload
        def decorator(callback: GlobalEventCallback[EventNameT]) -> GlobalEventCallback[EventNameT]:
            ...

        def decorator(
            callback: EventCallback | GlobalEventCallback[EventNameT],
        ) -> EventCallback | GlobalEventCallback[EventNameT]:
            # This is fine due to @overload's
            self.add_listener(callback, event_name)  # type: ignore
            return callback

        return decorator

    @overload
    def add_listener(self, callback: EventCallback, event_name: EventNameT) -> None:
        ...

    @overload
    def add_listener(self, callback: GlobalEventCallback[EventNameT], event_name: None = None) -> None:
        ...

    def add_listener(
        self, callback: EventCallback | GlobalEventCallback[EventNameT], event_name: EventNameT | None = None
    ) -> None:
        """Add a event listener.

        Example usage:

        .. code-block:: python

            async def join_handler(username: str) -> None:
                print(f"Welcome {username}")

            dispatcher.add_listener(welcome_handler, "join")

        Parameters
        ----------
        callback: :class:`EventCallback` | :class:`GlobalEventCallback`
            The event callback to register.
        event_name: :class:`EventNameT` | :data:`None`
            The event name to listen to. If this is :data:`None`,
            this is considered a global event and all events will be sent to the callback.
        """
        if event_name is None:
            if TYPE_CHECKING:
                callback = cast(GlobalEventCallback[EventNameT], callback)
            self._global_event_handlers.append(callback)
        else:
            if TYPE_CHECKING:
                callback = cast(EventCallback, callback)
            self._event_handlers[event_name].append(callback)

    @overload
    def remove_listener(self, callback: EventCallback, event_name: EventNameT) -> None:
        ...

    @overload
    def remove_listener(self, callback: GlobalEventCallback[EventNameT], event_name: None = None) -> None:
        ...

    def remove_listener(
        self, callback: EventCallback | GlobalEventCallback[EventNameT], event_name: EventNameT | None = None
    ) -> None:
        """Removes a event listener.

        Example usage:

        .. code-block:: python

            dispatcher.remove_listener(welcome_handler, "join")

        Parameters
        ----------
        callback: :class:`EventCallback` | :class:`GlobalEventCallback`
            The event callback to remove.
        event_name: :class:`EventNameT` | :data:`None`
            The event name to remove. If this is :data:`None`, the listener is considered a global event.

            .. warning::
                If the event_name does not match the event name it was registered with,
                the removal will fail with a :class:`ValueError` as the listener was not found.

        Raises
        ------
        :class:`ValueError`
            The callback was not registered to this event.
        """
        if event_name is None:
            if TYPE_CHECKING:
                callback = cast(GlobalEventCallback[EventNameT], callback)
            try:
                self._global_event_handlers.remove(callback)
            except ValueError:
                raise ValueError("Listener not registered globally.")
        else:
            if TYPE_CHECKING:
                callback = cast(EventCallback, callback)
            try:
                self._event_handlers[event_name].remove(callback)
            except ValueError:
                raise ValueError(f"Listener not registered for event {event_name}")

    @overload
    def add_error_handler(self, callback: ExceptionHandler, event_name: EventNameT) -> None:
        ...

    @overload
    def add_error_handler(self, callback: GlobalExceptionHandler[EventNameT], event_name: None = None) -> None:
        ...

    def add_error_handler(
        self, callback: ExceptionHandler | GlobalExceptionHandler[EventNameT], event_name: EventNameT | None = None
    ) -> None:
        """Add an error handler for listeners.

        The callback will be called when an exception is raised in a listener.

        .. note::
            If no listener is registered, the error will be logged.

        Example usage:

        .. code-block:: python

            async def error(exception: Exception) -> None:
                print("Oops!")

            dispatcher.add_error_handler(error_handler, "join")
        """
        if event_name is None:
            if TYPE_CHECKING:
                callback = cast(GlobalExceptionHandler[EventNameT], callback)
            self._global_exception_handlers.append(callback)
        else:
            if TYPE_CHECKING:
                callback = cast(ExceptionHandler, callback)
            self._exception_handlers[event_name].append(callback)

    @overload
    def remove_error_handler(self, callback: ExceptionHandler, event_name: EventNameT) -> None:
        ...

    @overload
    def remove_error_handler(self, callback: GlobalExceptionHandler[EventNameT], event_name: None = None) -> None:
        ...

    def remove_error_handler(
        self, callback: ExceptionHandler | GlobalExceptionHandler[EventNameT], event_name: EventNameT | None = None
    ) -> None:
        """Removes an error handler.

        Example usage:

        .. code-block:: python

            dispatcher.remove_error_handler(error_handler, "join")

        Parameters
        ----------
        callback: :class:`ExceptionHandler` | :class:`GlobalExceptionHandler`
            The error handler to remove.
        event_name: :class:`EventNameT` | :data:`None`
            The event name to remove. If this is :data:`None`, the listener is considered a global event.

            .. warning::
                If the event_name does not match the event name it was registered with,
                the removal will fail with a :class:`ValueError` as the listener was not found.

        Raises
        ------
        :class:`ValueError`
            The callback was not registered to this event.
        """
        if event_name is None:
            if TYPE_CHECKING:
                callback = cast(GlobalExceptionHandler[EventNameT], callback)
            try:
                self._global_exception_handlers.remove(callback)
            except ValueError:
                raise ValueError("Exception handler not registered globally.")
        else:
            if TYPE_CHECKING:
                callback = cast(ExceptionHandler, callback)
            try:
                self._exception_handlers[event_name].remove(callback)
            except ValueError:
                raise ValueError(f"Exception handler not registered for event {event_name}")

    @overload
    def wait_for(self, check: WaitForCheck, event_name: EventNameT) -> WaitForReturn[EventNameT]:
        ...

    @overload
    def wait_for(self, check: GlobalWaitForCheck[EventNameT], event_name: None = None) -> WaitForReturn[EventNameT]:
        ...

    async def wait_for(
        self, check: WaitForCheck | GlobalWaitForCheck[EventNameT], event_name: EventNameT | None = None
    ) -> WaitForReturn[EventNameT]:
        """Wait for an event to occur.

        Example usage:

        .. code-block:: python

            username = await dispatcher.wait_for(
                lambda username: username.startswith("h"),
                "join"
            )
            print(f"{username}'s username starts with h")

        Parameters
        ----------
        check: :class:`WaitForCheck` | :class:`GlobalWaitForCheck`
            Check for it to return.
        event_name: :class:`EventNameT` | :data:`None`
            The event name to wait for. If this is :data:`None`,
            it is considered global and will return when any event is received and include a :class:`EventNameT` as the first event argument.

        Returns
        -------
        :class:`EventNameT`, * :data:`typing.Any`
            The event name and the event arguments. This is only returned if the event is global.
        * :data:`typing.Any`
            The event arguments.
        """
        # TODO: Return type needs to be fixed
        # TODO: I don't like this. Typings makes everything look awful.
        if event_name is None:
            if TYPE_CHECKING:
                check = cast(GlobalWaitForCheck[EventNameT], check)
            # Bug in pyright considering this is a string... TODO: Get this fixed
            future: "Future[EventNameT, *Any]" = Future()  # type: ignore

            self._global_wait_for_handlers.append((check, future))
            logger.debug("Added _global_wait_for_handler")
            logger.debug(self._global_wait_for_handlers)
        else:
            if TYPE_CHECKING:
                check = cast(WaitForCheck, check)
            future: "Future[*Any]" = Future()  # pyright: ignore

            self._wait_for_handlers[event_name].append((check, future))
            logger.debug("Added _wait_for_handlers")
            logger.debug(self._wait_for_handlers)
        try:
            result = await future
        except CancelledError:
            # Cancelled, cleanup!
            if event_name is None:
                if TYPE_CHECKING:
                    check = cast(GlobalWaitForCheck[EventNameT], check)
                self._global_wait_for_handlers.remove((check, future))
            else:
                if TYPE_CHECKING:
                    check = cast(WaitForCheck, check)
                self._wait_for_handlers[event_name].remove((check, future))
            # Properly cancel the task
            raise
        return result

    # Dispatching
    async def dispatch(self, event_name: EventNameT, *args: Any) -> None:
        """Dispatch a event

        Example usage:

        .. code-block:: python

            dispatcher.dispatch("join", "John")

        Parameters
        ----------
        event_name: :class:`EventNameT`
            The event name to dispatch to.
        args: :data:`typing.Any`
            The event arguments. This will be passed to the listeners.
        """
        logger.debug("Dispatching event %s", event_name)

        # Event handlers
        # Tasks are used here as some event handler/check might take a long time.
        for handler in self._global_event_handlers:
            logger.debug("Dispatching to a global handler")
            create_task(self._run_global_event_handler(handler, event_name, *args))
        for handler in self._event_handlers.get(event_name, []):
            logger.debug("Dispatching to a local handler")
            create_task(self._run_event_handler(handler, event_name, *args))

        # Wait for handlers
        for check, future in self._wait_for_handlers.get(event_name, []):
            logger.debug("Dispatching to a wait_for handler")
            create_task(self._run_wait_for_handler(check, future, event_name, *args))
        for check, future in self._global_wait_for_handlers:
            logger.debug("Dispatching to a global wait_for handler")
            create_task(self._run_global_wait_for_handler(check, future, event_name, *args))

    async def _run_event_handler(self, callback: EventCallback, event_name: EventNameT, *args: Any) -> None:
        """Run event with exception handlers"""
        try:
            await maybe_coro(callback, *args)
        except Exception as exc:
            if not (self._exception_handlers.get(event_name) or self._global_exception_handlers):
                # No exception handlers for this event.
                # Raise a default exception
                logger.exception("Exception occured in event handler")
                return
            for handler in self._exception_handlers.get(event_name, []):
                try:
                    await maybe_coro(handler, exc)
                except Exception:
                    logger.exception("Exception occured in exception handler")
            for handler in self._global_exception_handlers:
                try:
                    await maybe_coro(handler, event_name, exc)
                except Exception:
                    logger.exception("Exception occured in exception handler")

    async def _run_global_event_handler(
        self, callback: GlobalEventCallback[EventNameT], event_name: EventNameT, *args: Any
    ) -> None:
        """Run global event with exception handlers"""
        try:
            await maybe_coro(callback, event_name, *args)
            logger.debug("Inside global event handler")
        except Exception as exc:
            if len(self._global_exception_handlers) == 0:
                # No exception handlers.
                # Raise a default exception
                logger.exception("Exception occured in global event handler")
                return
            for handler in self._global_exception_handlers:
                logger.debug("Calling exception handler")
                try:
                    await maybe_coro(handler, event_name, exc)
                except Exception:
                    logger.exception("Exception occured in exception handler")

    async def _run_wait_for_handler(
        self, check: WaitForCheck, future: "Future[tuple[*Any]]", event_name: EventNameT, *args: Any  # pyright: ignore
    ) -> None:
        try:
            result = await maybe_coro(check, *args)
        except:
            logger.exception("Exception occured in wait for check")
            return
        if not result:
            return

        future.set_result(args)

        self._wait_for_handlers[event_name].remove((check, future))

    async def _run_global_wait_for_handler(
        self,
        check: GlobalWaitForCheck[EventNameT],
        future: "Future[tuple[EventNameT, *Any]]",  # pyright: ignore
        event_name: EventNameT,
        *args: Any,
    ) -> None:
        try:
            result = await maybe_coro(check, event_name, *args)
        except:
            logger.exception("Exception occured in wait for check")
            return
        if not result:
            return

        future.set_result((event_name, *args))

        self._global_wait_for_handlers.remove((check, future))

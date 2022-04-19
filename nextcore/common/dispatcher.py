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
    )

    EventCallback = Callable[[*Any], Any]
    GlobalEventCallback = Callable[[EventNameT, *Any], Any]

    WaitForCheck = Callable[[*Any], Union[Awaitable[bool], bool]]
    GlobalWaitForCheck = Callable[[EventNameT, *Any], Union[Awaitable[bool], bool]]

    ExceptionHandler = Callable[[Exception], Any]
    GlobalExceptionHandler = Callable[[EventNameT, Exception], Any]

logger = getLogger(__name__)

__all__ = ("Dispatcher",)


class Dispatcher(Generic[EventNameT]):
    """A event dispatcher"""

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
    def add_listener(self, callback: GlobalEventCallback[EventNameT], event_name: None = None) -> None:
        ...

    @overload
    def add_listener(self, callback: EventCallback, event_name: EventNameT) -> None:
        ...

    def add_listener(
        self, callback: EventCallback | GlobalEventCallback[EventNameT], event_name: EventNameT | None = None
    ) -> None:
        if event_name is None:
            if TYPE_CHECKING:
                callback = cast(GlobalEventCallback[EventNameT], callback)
            self._global_event_handlers.append(callback)
        else:
            if TYPE_CHECKING:
                callback = cast(EventCallback, callback)
            self._event_handlers[event_name].append(callback)

    def remove_listener(
        self, callback: EventCallback | GlobalEventCallback[EventNameT], event_name: EventNameT | None = None
    ) -> None:
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

    def add_error_handler(
        self, callback: ExceptionHandler | GlobalExceptionHandler[EventNameT], event_name: EventNameT | None = None
    ) -> None:
        if event_name is None:
            if TYPE_CHECKING:
                callback = cast(GlobalExceptionHandler[EventNameT], callback)
            self._global_exception_handlers.append(callback)
        else:
            if TYPE_CHECKING:
                callback = cast(ExceptionHandler, callback)
            self._exception_handlers[event_name].append(callback)

    def remove_error_handler(
        self, callback: ExceptionHandler | GlobalExceptionHandler[EventNameT], event_name: EventNameT | None = None
    ) -> None:
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

    async def wait_for(
        self, check: WaitForCheck | GlobalWaitForCheck[EventNameT], event_name: EventNameT | None = None
    ):
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
        """Dispatch event"""
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

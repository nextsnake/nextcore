from __future__ import annotations

from asyncio import Future
from asyncio import TimeoutError as AsyncioTimeoutError
from asyncio import create_task, get_running_loop, wait_for
from typing import TYPE_CHECKING

from pytest import mark, raises

from nextcore.common.dispatcher import Dispatcher

if TYPE_CHECKING:
    from typing import Any


@mark.asyncio
@mark.parametrize("event_name", [None, "test"])
@mark.parametrize("func_sync", [True, False])
async def test_listeners(event_name: str | None, func_sync: bool) -> None:
    dispatcher: Dispatcher[str] = Dispatcher()

    got_response: Future[None] = Future()

    def sync_response_callback(event: str | None = None) -> None:
        if event_name is None:
            assert event is not None
        else:
            assert event is None
        got_response.set_result(None)

    async def async_response_callback(event: str | None = None) -> None:
        sync_response_callback(event)

    if func_sync:
        callback = sync_response_callback
    else:
        callback = async_response_callback

    dispatcher.add_listener(callback, event_name)
    await dispatcher.dispatch("test")
    await wait_for(got_response, timeout=1)

    got_response = Future()
    dispatcher.remove_listener(callback, event_name)
    await dispatcher.dispatch("test")

    with raises(AsyncioTimeoutError):
        await wait_for(got_response, timeout=0.1)

    dispatcher.close()


@mark.asyncio
@mark.parametrize("event_name", [None, "test"])
@mark.parametrize("func_sync", [True, False])
async def test_listen(event_name: str | None, func_sync: bool) -> None:
    dispatcher: Dispatcher[str] = Dispatcher()

    got_response: Future[None] = Future()

    def response_callback(event: str | None = None) -> None:
        if event_name is None:
            assert event is not None
        else:
            assert event is None
        got_response.set_result(None)

    if func_sync:

        @dispatcher.listen(event_name)
        def sync_response_callback(event_name: str | None = None) -> None:
            response_callback(event_name)

    else:

        @dispatcher.listen(event_name)
        async def async_response_callback(event_name: str | None = None) -> None:
            response_callback(event_name)

    await dispatcher.dispatch("test")
    await wait_for(got_response, timeout=1)

    dispatcher.close()


@mark.asyncio
@mark.parametrize("event_name", [None, "test"])
async def test_error_handler(event_name: str | None) -> None:
    dispatcher: Dispatcher[str] = Dispatcher()

    got_response: Future[None] = Future()

    def error_causer() -> None:
        raise RuntimeError("Dummy error")

    def error_handler(*args: Any) -> None:
        if event_name is None:
            assert isinstance(args[0], str), "Event name was not passed to error handler"
            assert isinstance(args[1], RuntimeError), "Error was not passed to error handler"
        else:
            assert isinstance(args[0], RuntimeError), "Error was not passed to error handler"

        got_response.set_result(None)

    dispatcher.add_listener(error_causer, "test")
    dispatcher.add_error_handler(error_handler, event_name)
    await dispatcher.dispatch("test")
    await wait_for(got_response, timeout=1)

    got_response = Future()
    dispatcher.remove_listener(error_causer, "test")
    await dispatcher.dispatch("test")

    with raises(AsyncioTimeoutError):
        await wait_for(got_response, timeout=0.1)

    dispatcher.close()


@mark.asyncio
@mark.parametrize("event_name", [None, "test"])
async def test_default_error_handler(caplog, event_name: str | None) -> None:
    dispatcher: Dispatcher[str] = Dispatcher()

    errored: Future[None] = Future()

    def error_causer(event: str | None = None) -> None:
        if event_name is None:
            assert event is not None
        else:
            assert event is None
        errored.set_result(None)
        raise RuntimeError("Dummy error")

    dispatcher.add_listener(error_causer, event_name)

    loop = get_running_loop()

    # Delay the execution so wait_for gets time to run.
    # TODO: This workaround is bad.
    loop.call_later(0.01, create_task, dispatcher.dispatch("test"))

    await wait_for(errored, timeout=1)

    error_count = len([record for record in caplog.records if record.levelname == "ERROR"])
    assert error_count == 1

    dispatcher.close()


def test_remove_nonexistant_listener() -> None:
    dispatcher: Dispatcher[str] = Dispatcher()

    def sync_callback() -> None:
        pass

    with raises(ValueError):
        dispatcher.remove_listener(sync_callback, "test")

    dispatcher.close()


@mark.asyncio
@mark.parametrize("event_name", [None, "test"])
async def test_wait_for_handler(event_name: str | None, caplog) -> None:
    dispatcher: Dispatcher[str] = Dispatcher()

    def event_name_check(event: str | None) -> None:
        if event_name is None:
            assert event is not None
        else:
            assert event is None

    def true_callback(event: str | None = None) -> bool:
        event_name_check(event)
        return True

    def false_callback(event: str | None = None) -> bool:
        event_name_check(event)
        return False

    loop = get_running_loop()
    loop.call_later(0.01, create_task, dispatcher.dispatch("test"))
    await wait_for(dispatcher.wait_for(true_callback, event_name), timeout=0.1)

    loop.call_later(0.01, create_task, dispatcher.dispatch("test"))
    with raises(AsyncioTimeoutError):
        await wait_for(dispatcher.wait_for(false_callback, event_name), timeout=0.1)

    # Check for logging errors.
    error_count = len([record for record in caplog.records if record.levelname == "ERROR"])
    assert error_count == 0, "Logged errors where present"

    dispatcher.close()

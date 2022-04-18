from asyncio import TimeoutError as AsyncioTimeoutError
from asyncio import create_task, get_running_loop, sleep, wait_for, Future

from pytest import mark, raises

from nextcore.common.dispatcher import Dispatcher


def test_sync_add_remove_listener():
    dispatcher: Dispatcher[str] = Dispatcher()

    def sync_callback():
        pass

    dispatcher.add_listener(sync_callback, "test")
    assert len(dispatcher._event_handlers["test"]) == 1, "Sync listener not added"  # type: ignore
    dispatcher.remove_listener(sync_callback, "test")
    assert len(dispatcher._event_handlers["test"]) == 0, "Sync listener not removed"  # type: ignore


def test_sync_add_remove_global_listener():
    dispatcher: Dispatcher[str] = Dispatcher()

    def sync_callback():
        pass

    dispatcher.add_listener(sync_callback)
    assert len(dispatcher._global_event_handlers) == 1, "Sync listener not added"  # type: ignore
    dispatcher.remove_listener(sync_callback)
    assert len(dispatcher._global_event_handlers) == 0, "Sync listener not removed"  # type: ignore


def test_remove_listener():
    dispatcher: Dispatcher[str] = Dispatcher()

    def sync_callback():
        pass

    with raises(ValueError):
        dispatcher.remove_listener(sync_callback, "test")


@mark.asyncio
async def test_async_add_remove_listener():
    dispatcher: Dispatcher[str] = Dispatcher()

    async def async_callback():
        pass

    dispatcher.add_listener(async_callback, "test")
    assert len(dispatcher._event_handlers["test"]) == 1, "Async listener not added"  # type: ignore
    dispatcher.remove_listener(async_callback, "test")
    assert len(dispatcher._event_handlers["test"]) == 0, "Async listener not removed"  # type: ignore


@mark.asyncio
async def test_async_add_remove_global_listener():
    dispatcher: Dispatcher[str] = Dispatcher()

    async def async_callback():
        pass

    dispatcher.add_listener(async_callback)
    assert len(dispatcher._global_event_handlers) == 1, "Async listener not added"  # type: ignore
    dispatcher.remove_listener(async_callback)
    assert len(dispatcher._global_event_handlers) == 0, "Async listener not removed"  # type: ignore


@mark.asyncio
async def test_sync_wait_for_no_event():
    dispatcher: Dispatcher[str] = Dispatcher()

    with raises(AsyncioTimeoutError):
        await wait_for(dispatcher.wait_for(lambda: False), timeout=0.1)


@mark.asyncio
async def test_async_wait_for_no_event():
    dispatcher: Dispatcher[str] = Dispatcher()

    async def blank_check():
        return False

    with raises(AsyncioTimeoutError):
        await wait_for(dispatcher.wait_for(blank_check), timeout=0.1)


@mark.asyncio
async def test_sync_wait_for_event():
    dispatcher: Dispatcher[str] = Dispatcher()

    task = create_task(dispatcher.wait_for(lambda: True, "test"))
    await sleep(0)  # This switches control to the dispatcher to dispatch the event.
    await dispatcher.dispatch("test")
    await sleep(0.01)

    assert task.done(), "Task never finished"
    if exception := task.exception():
        raise exception
    assert task.result, "Task finished but no result available"


@mark.asyncio
async def test_async_wait_for_event():
    dispatcher: Dispatcher[str] = Dispatcher()

    async def blank_check():
        return True

    task = create_task(dispatcher.wait_for(blank_check, "test"))
    await sleep(0)  # This switches control to the dispatcher to dispatch the event.
    await dispatcher.dispatch("test")
    await sleep(0.01)

    assert task.done(), "Task never finished"
    if exception := task.exception():
        raise exception
    assert task.result, "Task finished but no result available"


@mark.asyncio
async def test_error_handler():
    dispatcher: Dispatcher[str] = Dispatcher()

    did_error: Future[None] = Future()

    def error_handler(_: Exception) -> None:
        did_error.set_result(None)

    def error_causer() -> None:
        raise RuntimeError("Test error!")

    dispatcher.add_exception_handler(error_handler, "test")
    dispatcher.add_listener(error_causer, "test")

    # Dispatch the event. This is done via call_later as we want to wait for the error handler to run.
    await dispatcher.dispatch("test")

    await did_error

    assert did_error, "Error flag was not set"

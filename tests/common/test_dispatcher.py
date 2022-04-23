from asyncio import Future
from asyncio import TimeoutError as AsyncioTimeoutError
from asyncio import create_task, get_running_loop, wait_for

from pytest import mark, raises

from nextcore.common.dispatcher import Dispatcher


@mark.asyncio
async def test_local_sync_listeners() -> None:
    dispatcher: Dispatcher[str] = Dispatcher()

    got_response: Future[None] = Future()

    def sync_response_callback() -> None:
        got_response.set_result(None)

    dispatcher.add_listener(sync_response_callback, "test")
    await dispatcher.dispatch("test")
    await wait_for(got_response, timeout=1)

    got_response = Future()
    dispatcher.remove_listener(sync_response_callback, "test")
    await dispatcher.dispatch("test")

    with raises(AsyncioTimeoutError):
        await wait_for(got_response, timeout=0.1)


@mark.asyncio
async def test_global_sync_listeners() -> None:
    dispatcher: Dispatcher[str] = Dispatcher()

    got_response: Future[None] = Future()

    def sync_response_callback(event_name: str) -> None:
        del event_name
        got_response.set_result(None)

    dispatcher.add_listener(sync_response_callback)
    await dispatcher.dispatch("test")
    await wait_for(got_response, timeout=1)

    got_response = Future()
    dispatcher.remove_listener(sync_response_callback)
    await dispatcher.dispatch("test")

    with raises(AsyncioTimeoutError):
        await wait_for(got_response, timeout=0.1)


@mark.asyncio
async def test_local_async_listeners() -> None:
    dispatcher: Dispatcher[str] = Dispatcher()

    got_response: Future[None] = Future()

    async def sync_response_callback() -> None:
        got_response.set_result(None)

    dispatcher.add_listener(sync_response_callback, "test")
    await dispatcher.dispatch("test")
    await wait_for(got_response, timeout=1)

    got_response = Future()
    dispatcher.remove_listener(sync_response_callback, "test")
    await dispatcher.dispatch("test")

    with raises(AsyncioTimeoutError):
        await wait_for(got_response, timeout=0.1)


@mark.asyncio
async def test_global_async_listeners() -> None:
    dispatcher: Dispatcher[str] = Dispatcher()

    got_response: Future[None] = Future()

    async def sync_response_callback(event_name: str) -> None:
        del event_name
        got_response.set_result(None)

    dispatcher.add_listener(sync_response_callback)
    await dispatcher.dispatch("test")
    await wait_for(got_response, timeout=1)

    got_response = Future()
    dispatcher.remove_listener(sync_response_callback)
    await dispatcher.dispatch("test")

    with raises(AsyncioTimeoutError):
        await wait_for(got_response, timeout=0.1)

@mark.asyncio
async def test_listen() -> None:
    dispatcher: Dispatcher[str] = Dispatcher()

    got_response: Future[None] = Future()
    
    @dispatcher.listen("test")
    async def sync_response_callback() -> None:
        got_response.set_result(None)

    await dispatcher.dispatch("test")
    await wait_for(got_response, timeout=1)

@mark.asyncio
async def test_local_error_handler() -> None:
    dispatcher: Dispatcher[str] = Dispatcher()

    got_response: Future[None] = Future()

    def error_causer() -> None:
        raise RuntimeError("Dummy error")

    def error_handler(exception: Exception) -> None:
        del exception
        got_response.set_result(None)

    dispatcher.add_listener(error_causer, "test")
    dispatcher.add_error_handler(error_handler, "test")
    await dispatcher.dispatch("test")
    await wait_for(got_response, timeout=1)

    got_response = Future()
    dispatcher.remove_listener(error_causer, "test")
    await dispatcher.dispatch("test")

    with raises(AsyncioTimeoutError):
        await wait_for(got_response, timeout=0.1)


@mark.asyncio
async def test_global_error_handler() -> None:
    dispatcher: Dispatcher[str] = Dispatcher()

    got_response: Future[None] = Future()

    def error_causer(event_name: str) -> None:
        del event_name # Not used
        raise RuntimeError("Dummy error")

    def error_handler(event_name: str, exception: Exception) -> None:
        del event_name, exception
        got_response.set_result(None)

    dispatcher.add_listener(error_causer)
    dispatcher.add_error_handler(error_handler)

    loop = get_running_loop()

    # Delay the execution so wait_for gets time to run.
    # TODO: This workaround is bad.
    loop.call_later(0.01, create_task, dispatcher.dispatch("test"))

    await wait_for(got_response, timeout=1)

    got_response = Future()
    dispatcher.remove_listener(error_causer)
    loop.call_later(0.01, create_task, dispatcher.dispatch("test"))

    with raises(AsyncioTimeoutError):
        await wait_for(got_response, timeout=0.1)


def test_remove_nonexistant_listener() -> None:
    dispatcher: Dispatcher[str] = Dispatcher()

    def sync_callback() -> None:
        pass

    with raises(ValueError):
        dispatcher.remove_listener(sync_callback, "test")


@mark.asyncio
async def test_local_wait_for_handler() -> None:
    dispatcher: Dispatcher[str] = Dispatcher()

    loop = get_running_loop()
    loop.call_later(0.01, create_task, dispatcher.dispatch("test"))
    await wait_for(dispatcher.wait_for(lambda: True, "test"), timeout=0.1)

    loop.call_later(0.01, create_task, dispatcher.dispatch("test"))
    with raises(AsyncioTimeoutError):
        await wait_for(dispatcher.wait_for(lambda: False, "test"), timeout=0.1)


@mark.asyncio
async def test_global_wait_for_handler() -> None:
    dispatcher: Dispatcher[str] = Dispatcher()

    loop = get_running_loop()
    loop.call_later(0.01, create_task, dispatcher.dispatch("test"))
    await wait_for(dispatcher.wait_for(lambda _: True), timeout=0.1)

    loop.call_later(0.01, create_task, dispatcher.dispatch("test"))
    with raises(AsyncioTimeoutError):
        await wait_for(dispatcher.wait_for(lambda _: False), timeout=0.1)

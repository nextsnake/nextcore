from nextcore.gateway.dispatcher import Dispatcher
from pytest import mark, raises
from asyncio import TimeoutError as AsyncioTimeoutError, create_task, sleep


def test_sync_add_remove_listener():
    dispatcher = Dispatcher()
    
    def sync_callback():
        pass

    dispatcher.add_listener(sync_callback, "test")
    assert len(dispatcher._listeners["test"]) == 1, "Sync listener not added" # type: ignore
    dispatcher.remove_listener(sync_callback)
    assert len(dispatcher._listeners["test"]) == 0, "Sync listener not removed" # type: ignore

def test_sync_add_remove_global_listener():
    dispatcher = Dispatcher()
    
    def sync_callback():
        pass

    dispatcher.add_listener(sync_callback)
    assert len(dispatcher._global_listeners) == 1, "Sync listener not added" # type: ignore
    dispatcher.remove_listener(sync_callback)
    assert len(dispatcher._global_listeners) == 0, "Sync listener not removed" # type: ignore


@mark.asyncio
async def test_async_add_remove_listener():
    dispatcher = Dispatcher()
    
    async def async_callback():
        pass
    
    dispatcher.add_listener(async_callback, "test")
    assert len(dispatcher._listeners["test"]) == 1, "Async listener not added" # type: ignore
    dispatcher.remove_listener(async_callback)
    assert len(dispatcher._listeners["test"]) == 0, "Async listener not removed" # type: ignore

@mark.asyncio
async def test_async_add_remove_global_listener():
    dispatcher = Dispatcher()
    
    async def async_callback():
        pass

    dispatcher.add_listener(async_callback)
    assert len(dispatcher._global_listeners) == 1, "Async listener not added" # type: ignore
    dispatcher.remove_listener(async_callback)
    assert len(dispatcher._global_listeners) == 0, "Async listener not removed" # type: ignore

@mark.asyncio
async def test_sync_wait_for_no_event():
    dispatcher = Dispatcher()
    
    with raises(AsyncioTimeoutError):
        await dispatcher.wait_for(lambda: False, timeout=0.01)
@mark.asyncio
async def test_async_wait_for_no_event():
    dispatcher = Dispatcher()

    async def blank_check():
        return False
    
    with raises(AsyncioTimeoutError):
        await dispatcher.wait_for(blank_check, timeout=0.01)


@mark.asyncio
async def test_sync_wait_for_event():
    dispatcher = Dispatcher()
    
    task = create_task(dispatcher.wait_for(lambda: True))
    await sleep(0) # This switches control to the dispatcher to dispatch the event.
    dispatcher.dispatch("test")
    await sleep(0) # We need to switch control twice here. Yes this sucks, please PR if you know a better way. TODO: Fix this.
    await sleep(0)

    assert task.done(), "Task never finished"
    if (exception := task.exception()):
        raise exception
    assert task.result, "Task finished but no result available"


@mark.asyncio
async def test_async_wait_for_event():
    dispatcher = Dispatcher()

    async def blank_check():
        return True
    
    task = create_task(dispatcher.wait_for(blank_check))
    await sleep(0) # This switches control to the dispatcher to dispatch the event.
    dispatcher.dispatch("test")
    await sleep(0) # We need to switch control twice here. Yes this sucks, please PR if you know a better way. TODO: Fix this.
    await sleep(0)

    assert task.done(), "Task never finished"
    if (exception := task.exception()):
        raise exception
    assert task.result, "Task finished but no result available"

from pytest import mark

from nextcore.utils import *


def test_loads():
    assert json_loads('{"a": 1}') == {"a": 1}


def test_dumps():
    assert json_dumps({"a": 1}) in ['{"a":1}', '{"a": 1}']


@mark.asyncio
async def test_sync_maybe_coro():
    result = await maybe_coro(lambda: 1)

    assert result == 1


@mark.asyncio
async def test_async_maybe_coro():
    async def test():
        return 1

    result = await maybe_coro(test)

    assert result == 1

from pytest import mark

from nextcore.common import maybe_coro


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

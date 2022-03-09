from asyncio import TimeoutError as AsyncioTimeoutError
from asyncio import wait_for

from pytest import mark, raises

from nextcore.http.flood_gate import FloodGate


@mark.asyncio
async def test_should_wait_forever():
    gate = FloodGate()

    with raises(AsyncioTimeoutError):
        await wait_for(gate.acquire(), timeout=0.1)


@mark.asyncio
async def test_should_error_on_double_pop():
    gate = FloodGate()

    gate.pop()

    with raises(ValueError):
        gate.pop()


@mark.asyncio
async def test_pop_should_reset():
    gate = FloodGate()

    gate.pop()

    await gate.acquire()

    gate.pop()


@mark.asyncio
async def test_should_error_pop_after_drain():
    gate = FloodGate()

    gate.drain()

    with raises(ValueError):
        gate.pop()


@mark.asyncio
async def test_always_returns_after_drain():
    gate = FloodGate()

    gate.drain()

    for _ in range(5):
        await gate.acquire()

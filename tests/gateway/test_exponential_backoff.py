from pytest import mark

from nextcore.gateway.exponential_backoff import ExponentialBackoff
from tests.utils import match_time


@mark.asyncio
@match_time(0.06, 0.01)
async def test_basic() -> None:
    backoff = ExponentialBackoff(0.001, 2, 0.3)

    # Do 5 iterations
    # TODO: Can this be abstracted into a test util?
    i = 0
    async for _ in backoff:
        if i == 5:
            break
        i += 1


@mark.asyncio
@match_time(0.04, 0.01)
async def test_max() -> None:
    backoff = ExponentialBackoff(0.02, 2, 0.02)

    # Do 2 iterations
    # TODO: Can this be abstracted into a test util?
    i = 0
    async for _ in backoff:
        if i == 2:
            break
        i += 1

from asyncio import TimeoutError, wait_for
from time import time


def match_time(estimated, max_offset):
    """Errror if the estimated time is off"""

    def outer(func):
        async def inner(*args, **kwargs):
            start = time()
            try:
                await wait_for(func(*args, **kwargs), timeout=estimated + max_offset)
            except TimeoutError:
                raise TimeoutError(
                    f"Function returned too slowly (terminated). Expected {estimated}s, got {estimated + max_offset}s"
                ) from None
            end = time()
            time_used = end - start
            assert (
                time_used >= estimated - max_offset
            ), f"Function returned too quickly. Expected {estimated}s, got {time_used}s"
            assert (
                time_used <= estimated + max_offset
            ), f"Function returned too slowly. Expected {estimated}s, got {time_used}s"

        return inner

    return outer

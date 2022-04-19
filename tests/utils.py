from __future__ import annotations

from asyncio import TimeoutError, wait_for
from time import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable

    from typing_extensions import ParamSpec

    P = ParamSpec("P")


def match_time(estimated: float, max_offset: float):
    """Errror if the estimated time is off"""

    def outer(func: Callable[P, Any]):
        async def inner(*args: P.args, **kwargs: P.kwargs) -> None:
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

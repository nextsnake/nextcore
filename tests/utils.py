from time import time


def match_time(estimated, max_offset):
    """Errror if the estimated time is off"""

    def outer(func):
        async def inner(*args, **kwargs):
            start = time()
            await func(*args, **kwargs)
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

class HTTPError(Exception):
    ...


class RatelimitingFailedError(HTTPError):
    def __init__(self, times: int) -> None:
        self.times = times
        super().__init__(
            "Ratelimiting failed %s times. This should only happen if there is a library issue", self.times
        )


class HTTPStatusError(HTTPError):
    def __init__(self, discord_error_code: int, message: str) -> None:
        super().__init__(f"({discord_error_code}) {message}")


class BadRequestError(HTTPStatusError):
    ...


class ForbiddenError(HTTPStatusError):
    ...


class NotFoundError(HTTPStatusError):
    ...

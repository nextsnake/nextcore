# The MIT License (MIT)
# Copyright (c) 2021-present nextcore developers
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

"""Do requests to Discord over the HTTP API.

This module includes a HTTP client that handles rate limits for you,
and gives you convinient methods around the API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .authentication import *
from .bucket import Bucket
from .bucket_metadata import BucketMetadata
from .client import HTTPClient
from .errors import *
from .file import File
from .ratelimit_storage import RatelimitStorage
from .request_session import RequestSession
from .route import Route
from .global_rate_limiter import *

if TYPE_CHECKING:
    from typing import Final

__all__: Final[tuple[str, ...]] = (
    "Bucket",
    "BucketMetadata",
    "HTTPClient",
    "RateLimitingFailedError",
    "HTTPRequestStatusError",
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "InternalServerError",
    "CloudflareBanError",
    "RatelimitStorage",
    "RequestSession",
    "Route",
    "File",
    "BaseAuthentication",
    "BotAuthentication",
    "BearerAuthentication",
    "BaseGlobalRateLimiter",
    "UnlimitedGlobalRateLimiter",
    "LimitedGlobalRateLimiter",
)

# The MIT License (MIT)
#
# Copyright (c) 2022-present nextcore developers
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
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

from nextcore.http import HTTPClient, Route
import asyncio
from discord_typings import GetGatewayData

async def main():
    http_client = HTTPClient()
    await http_client.setup()

    # This can be found on https://discord.dev/topics/gateway#get-gateway
    route = Route("GET", "/gateway")
    
    # No authentication is used, so rate_limit_key None here is equivilent of your IP.
    response = await http_client.request(route, rate_limit_key=None)
    gateway: GetGatewayData = await response.json()

    print(gateway["url"])

    await http_client.close()

asyncio.run(main())

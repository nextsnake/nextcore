from __future__ import annotations
from pytest_harmony import TreeTests
import pytest
import typing
import os
from nextcore.http import BotAuthentication, HTTPClient
from nextcore.gateway import ShardManager, GatewayOpcode
from discord_typings import GuildData, ReadyData

tree = TreeTests()

@pytest.mark.asyncio
async def test_discord_api():
    await tree.run_tests()


# Get token
@tree.append()
async def get_token(state: dict[str, typing.Any]):
    token = os.environ.get("TOKEN")

    if token is None:
        pytest.skip("No TOKEN env var")

    state["token"] = token
    state["authentication"] = BotAuthentication(token)

    http_client = HTTPClient()
    await http_client.setup()
    state["http_client"] = http_client

@get_token.cleanup()
async def cleanup_get_token(state: dict[str, typing.Any]):
    del state["token"]
    del state["authentication"]

    http_client: HTTPClient = state["http_client"]

    await http_client.close()
    del state["http_client"]


# Get gateway
@get_token.append()
async def get_gateway(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]

    await http_client.get_gateway()


# Get token / create guild
@get_token.append()
async def create_guild(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]

    guild = await http_client.create_guild(authentication, name="Test guild")

    state["guild"] = guild

@create_guild.cleanup()
async def cleanup_create_guild(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]
    guild: GuildData = state["guild"]

    await http_client.delete_guild(authentication, guild["id"])

    del state["guild"]


# Get token / create guild / get audit logs
@create_guild.append()
async def get_audit_logs(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]
    guild: GuildData = state["guild"]

    logs = await http_client.get_guild_audit_log(authentication, guild["id"], limit=10)


    assert logs["audit_log_entries"] == []

# Get token / connect to gateway
@get_token.append()
async def connect_to_gateway(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]

    intents = 3276799 # Everything. TODO: Do this using a intents helper?

    gateway = ShardManager(authentication, intents, http_client)

    state["gateway"] = gateway

    await gateway.connect()

    ready_data: ReadyData = (await gateway.event_dispatcher.wait_for(lambda _: True, "READY"))[0]
    state["bot_user"] = ready_data["user"]

@connect_to_gateway.cleanup()
async def cleanup_connect_to_gateway(state: dict[str, typing.Any]):
    gateway: ShardManager = state["gateway"]

    await gateway.close()

    del state["gateway"]
    del state["bot_user"]

# Get token / connect to gateway / get latency
@connect_to_gateway.append()
async def get_latency(state: dict[str, typing.Any]):
    gateway: ShardManager = state["gateway"]

    for shard in gateway.active_shards:
        # Heartbeats are calculated after heartbeating. This may be VERY slow on bots with many shards, so use a test bot.
        await shard.raw_dispatcher.wait_for(lambda _: True, GatewayOpcode.HEARTBEAT_ACK)
        print(shard.latency)

# Get token / connect to gateway
@connect_to_gateway.append()
async def rescale_shards(state: dict[str, typing.Any]):
    gateway: ShardManager = state["gateway"]

    await gateway.rescale_shards(5)

    assert len(gateway.active_shards) == 5

@rescale_shards.cleanup()
async def cleanup_rescale_shards(state: dict[str, typing.Any]):
    gateway: ShardManager = state["gateway"]
    await gateway.rescale_shards(1)

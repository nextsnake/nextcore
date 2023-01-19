from __future__ import annotations

import os
import typing

import pytest
from discord_typings import EmbedData, GuildData, ReadyData, ChannelData, MessageData, ThreadChannelData
from pytest_harmony import TreeTests

from nextcore.gateway import GatewayOpcode, ShardManager
from nextcore.http import BotAuthentication, HTTPClient
from nextcore.http.errors import BadRequestError
from nextcore.http.file import File

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

    intents = 3276799  # Everything. TODO: Do this using a intents helper?

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


# Get token / create guild / create text channel
@create_guild.append()
async def create_text_channel(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]
    guild: GuildData = state["guild"]

    channel = await http_client.create_guild_channel(authentication, guild["id"], "test-text", type=0)

    state["channel"] = channel

@create_text_channel.cleanup()
async def cleanup_create_text_channel(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]
    channel: ChannelData = state["channel"]

    await http_client.delete_channel(authentication, channel["id"])

    del state["channel"]


# Get token / create guild / create text channel / get channel
@create_text_channel.append()
async def get_channel(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]
    channel: ChannelData = state["channel"]

    fetched_channel = await http_client.get_channel(authentication, channel["id"])

    assert fetched_channel["id"] == channel["id"]

# Get token / create guild / create text channel / modify text channel
@create_text_channel.append()
async def modify_text_channel(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]
    channel: ChannelData = state["channel"]
    
    modified_channel = await http_client.modify_guild_channel(authentication, channel["id"], name="cool-name", topic="This is a cool channel topic", nsfw=True, rate_limit_per_user=50, default_auto_archive_duration=1440)

    assert modified_channel["name"] == "cool-name"
    assert modified_channel["topic"] == "This is a cool channel topic"
    assert modified_channel["nsfw"] == True
    assert modified_channel["rate_limit_per_user"] == 50
    assert modified_channel["default_auto_archive_duration"] == 1440


# Get token / create guild / create text channel / create message
@create_text_channel.append()
async def create_message(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]
    channel: ChannelData = state["channel"]
    
    message = await http_client.create_message(authentication, channel["id"], content="Hello!")

    state["message"] = message

@create_message.cleanup()
async def cleanup_create_message(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]
    channel: ChannelData = state["channel"]
    message: MessageData = state["message"]

    await http_client.delete_message(authentication, channel["id"], message["id"])

    del state["message"]


# Get token / create guild / create text channel / create message / create reaction
@create_message.append()
async def create_reaction(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]
    channel: ChannelData = state["channel"]
    message: ChannelData = state["message"]

    await http_client.create_reaction(authentication, channel["id"], message["id"], "👋")


@create_message.cleanup()
async def cleanup_create_reaction(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]
    channel: ChannelData = state["channel"]
    message: ChannelData = state["message"]

    await http_client.delete_own_reaction(authentication, channel["id"], message["id"], "👋")


# Get token / create guild / create text channel / create message / create reaction / get reactions
@create_reaction.append()
async def get_reactions(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]
    channel: ChannelData = state["channel"]
    message: ChannelData = state["message"]

    reactions = await http_client.get_reactions(authentication, channel["id"], message["id"], "👋", limit=1, after=0)
    assert len(reactions) == 1


# Get token / create guild / create text channel / create message / create thread
@create_message.append()
async def create_thread(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]
    channel: ChannelData = state["channel"]
    message: ChannelData = state["message"]

    thread = await http_client.start_thread_from_message(authentication, channel["id"], message["id"], "Test thread stuff")
    await http_client.join_thread(authentication, thread["id"])

    state["thread"] = thread

@create_thread.cleanup()
async def cleanup_create_thread(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]
    thread: ThreadChannelData = state["thread"]

    await http_client.leave_thread(authentication, thread["id"])
    await http_client.delete_channel(authentication, thread["id"], reason="Bad thread")

# Get token / create guild / create text channel / create message / create thread / modify thread
@create_thread.append()
async def modify_thread(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]
    thread: ThreadChannelData = state["thread"]

    updated_thread = await http_client.modify_thread(authentication, thread["id"], archived=True, locked=True)
    updated_metadata = updated_thread["thread_metadata"]
    
    assert updated_metadata["archived"]
    assert updated_metadata["locked"]

@modify_thread.cleanup()
async def cleanup_modify_thread(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]
    thread: ThreadChannelData = state["thread"]

    await http_client.modify_thread(authentication, thread["id"], archived=False, locked=False)

# Get token / create guild / create text channel / create message / get channel messages
@create_message.append()
async def get_channel_messages(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]
    channel: ChannelData = state["channel"]
    message: MessageData = state["message"]

    messages = await http_client.get_channel_messages(authentication, channel["id"], around=message["id"], limit=1)
    assert len(messages) == 1

    before_messages = await http_client.get_channel_messages(authentication, channel["id"], before=message["id"], limit=1)
    assert len(before_messages) == 0

    after_messages = await http_client.get_channel_messages(authentication, channel["id"], after=message["id"], limit=1)
    assert len(after_messages) == 0

# Get token / create guild / create text channel / create message / edit message
@create_message.append()
async def edit_message(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]
    channel: ChannelData = state["channel"]
    message: MessageData = state["message"]

    new_message = await http_client.edit_message(authentication, channel["id"], message["id"], content="foobar")

    assert new_message["content"] == "foobar"

# Get token / create guild / create text channel / create message
@create_text_channel.append()
async def create_message_advanced(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]
    channel: ChannelData = state["channel"]
    
    embeds: list[EmbedData] = [
        {
            "title": "Hi",
            "description": "Hello"
        }
    ]
    file = File("test.txt", "Test contents")

    message = await http_client.create_message(authentication, channel["id"], embeds=embeds, files=[file])

    state["message"] = message

    assert len(message["embeds"]) == 1
    assert len(message["attachments"]) == 1

@create_message.cleanup()
async def cleanup_create_message(state: dict[str, typing.Any]):
    http_client: HTTPClient = state["http_client"]
    authentication: BotAuthentication = state["authentication"]
    channel: ChannelData = state["channel"]
    message: MessageData = state["message"]

    await http_client.delete_message(authentication, channel["id"], message["id"])

    del state["message"]



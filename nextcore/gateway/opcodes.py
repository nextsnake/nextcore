from enum import IntEnum


class GatewayOpcode(IntEnum):
    """
    Enum of all opcodes that can be sent/received to/from the gateway.
    """

    DISPATCH = 0
    """Can be received"""
    HEARTBEAT = 1
    """Can be sent/received"""
    IDENTIFY = 2
    """Can be sent"""
    PRESENCE_UPDAATE = 3
    """Can be sent"""
    VOICE_STATE_UPDATE = 4
    """Can be sent"""
    RESUME = 6
    """Can be sent"""
    RECONNECT = 7
    """Can be received"""
    REQUEST_GUILD_MEMBERS = 8
    """Can be sent"""
    INVALID_SESSION = 9
    """Can be received"""
    HELLO = 10
    """Can be received"""
    HEARTBEAT_ACK = 11
    """Can be received"""

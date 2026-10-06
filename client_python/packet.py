from enum import IntEnum
import struct


class PacketType(IntEnum):

    PING = 1
    LOGIN = 2
    CHAT = 3
    MOVE = 4
    LOG = 5
    SINGUP = 6
    LoginResponse = 7
    SignUpResponse = 8
    BAN = 9
    DECO =10
    MARKET_BUY = 11
    MARKET_SELL = 12
    MARKET_CANCEL_BUY = 13
    MARKET_CANCEL_SELL = 14
    PLAYER_STATE = 15
    PLAYER_REMOVE = 16
    SESSION = 17


class Packet:

    def __init__(
        self,
        packet_type,
        payload=b""
    ):

        self.packet_type = PacketType(packet_type)
        self.payload = payload


    def encode(self):

        body = (
            struct.pack(
                "!H",
                self.packet_type
            )
            +
            self.payload
        )

        return (
            struct.pack(
                "!I",
                len(body)
            )
            +
            body
        )


    @staticmethod
    def decode(data):

        packet_type = PacketType(
            struct.unpack(
                "!H",
                data[:2]
            )[0]
        )

        payload = data[2:]


        if packet_type == PacketType.LOGIN:
            from .packets.login import LoginPacket
            return LoginPacket.from_payload(payload)


        if packet_type == PacketType.CHAT:
            from .packets.chat import ChatPacket
            return ChatPacket.from_payload(payload)


        if packet_type == PacketType.MOVE:
            from .packets.move import MovePacket
            return MovePacket.from_payload(payload)


        if packet_type == PacketType.PING:
            from .packets.ping import PingPacket
            return PingPacket()
        if packet_type == PacketType.LOG:
            from .packets.log import LogPacket
            return LogPacket()
        if packet_type == PacketType.SINGUP:
            from .packets.singup import SingupPacket
            return SingupPacket.from_payload(payload)
        if packet_type == PacketType.BAN:
            from .packets.ban import BanPacket
            return BanPacket.from_payload(payload)
        if packet_type == PacketType.PLAYER_STATE:
            from .packets.player_state import PlayerStatePacket
            return PlayerStatePacket.from_payload(payload)
        if packet_type == PacketType.PLAYER_REMOVE:
            from .packets.player_remove import PlayerRemovePacket
            return PlayerRemovePacket.from_payload(payload)
        if packet_type == PacketType.SESSION:
            from .packets.session import SessionPacket
            return SessionPacket.from_payload(payload)
        if packet_type == PacketType.LoginResponse or packet_type == PacketType.SignUpResponse :
            return Packet(
            packet_type,
            payload
        )
        if packet_type == PacketType.DECO:
            from .packets.Deco import decoPacket
            return decoPacket.from_payload(payload)
        


        return Packet(
            packet_type,
            payload
        )

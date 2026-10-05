import struct
import uuid

from ..packet import Packet, PacketType


class PlayerStatePacket(Packet):

    def __init__(
        self,
        player_id,
        x,
        y,
        z,
    ):

        if isinstance(player_id, str):
            player_id = uuid.UUID(player_id)

        self.player_id = player_id
        self.x = x
        self.y = y
        self.z = z

        payload = (
            player_id.bytes
            + struct.pack(
                "!iii",
                x,
                y,
                z,
            )
        )

        super().__init__(
            PacketType.PLAYER_STATE,
            payload,
        )


    @classmethod
    def from_payload(
        cls,
        payload,
    ):

        if len(payload) != 28:
            raise ValueError(
                "PLAYER_STATE invalide"
            )

        player_id =
            uuid.UUID(
                bytes=payload[:16]
            )

        x, y, z = struct.unpack(
            "!iii",
            payload[16:28],
        )

        return cls(
            player_id,
            x,
            y,
            z,
        )
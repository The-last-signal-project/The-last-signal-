from __future__ import annotations

import struct
import uuid

from ..packet import Packet, PacketType


class PlayerStatePacket(Packet):
    """
    État autoritaire d'un joueur envoyé par le serveur.

    Payload :
        16 octets : UUID du joueur
         4 octets : X (int32 big-endian)
         4 octets : Y (int32 big-endian)
         4 octets : Z (int32 big-endian)

    Total : 28 octets
    """

    FORMAT = "!16siii"
    SIZE = struct.calcsize(FORMAT)

    def __init__(
        self,
        player_id: uuid.UUID,
        x: int,
        y: int,
        z: int,
    ) -> None:
        self.player_id = player_id
        self.x = x
        self.y = y
        self.z = z

        super().__init__(
            PacketType.PLAYER_STATE,
            self.encode_payload(),
        )

    def encode_payload(self) -> bytes:
        return struct.pack(
            self.FORMAT,
            self.player_id.bytes,
            self.x,
            self.y,
            self.z,
        )

    @classmethod
    def from_payload(cls, payload: bytes) -> "PlayerStatePacket":
        if len(payload) != cls.SIZE:
            raise ValueError(
                f"PlayerState invalide : "
                f"{len(payload)} octets reçus, "
                f"{cls.SIZE} attendus"
            )

        player_id_bytes, x, y, z = struct.unpack(
            cls.FORMAT,
            payload,
        )

        player_id = uuid.UUID(bytes=player_id_bytes)

        return cls(
            player_id=player_id,
            x=x,
            y=y,
            z=z,
        )

    def __repr__(self) -> str:
        return (
            f"PlayerStatePacket("
            f"player_id={self.player_id}, "
            f"x={self.x}, "
            f"y={self.y}, "
            f"z={self.z})"
        )
from __future__ import annotations

import uuid

from ..packet import Packet, PacketType


class PlayerRemovePacket(Packet):
    """Indique qu'un joueur a quitté le monde."""

    SIZE = 16

    def __init__(self, player_id: uuid.UUID) -> None:
        self.player_id = player_id

        super().__init__(
            PacketType.PLAYER_REMOVE,
            self.encode_payload(),
        )

    def encode_payload(self) -> bytes:
        return self.player_id.bytes

    @classmethod
    def decode_payload(cls, payload: bytes) -> "PlayerRemovePacket":
        if len(payload) != cls.SIZE:
            raise ValueError(
                f"PlayerRemove invalide : "
                f"{len(payload)} octets reçus, "
                f"{cls.SIZE} attendus"
            )

        return cls(
            player_id=uuid.UUID(bytes=payload),
        )

    def __repr__(self) -> str:
        return (
            f"PlayerRemovePacket("
            f"player_id={self.player_id})"
        )
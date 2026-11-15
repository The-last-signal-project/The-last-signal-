from __future__ import annotations

import struct
import uuid

from ..packet import Packet, PacketType


class ZoneStatePacket(Packet):
    """
    État de la clé et du trésor, envoyé par le serveur (autoritaire).

    Payload (43 octets) :
         1 octet  : état de la clé (0 = au sol, 1 = portée, 2 = utilisée)
         4 octets : x de la clé (int32), 0 si elle n'est pas au sol
         4 octets : y de la clé (int32), 0 si elle n'est pas au sol
        16 octets : UUID du porteur de la clé, nul si personne
         1 octet  : trésor pris (0 = disponible, 1 = pris)
        16 octets : UUID de celui qui a pris le trésor, nul sinon
         1 octet  : niveau du trésor (1 à 5)
    """

    FORMAT = "!B2i16sB16sB"
    SIZE = struct.calcsize(FORMAT)

    KEY_ON_GROUND = 0
    KEY_HELD = 1
    KEY_CONSUMED = 2

    _NIL = uuid.UUID(int=0)

    def __init__(
        self,
        key_state: int,
        key_x: int = 0,
        key_y: int = 0,
        key_holder: uuid.UUID | None = None,
        treasure_taken: bool = False,
        treasure_taker: uuid.UUID | None = None,
        treasure_level: int = 1,
    ) -> None:
        self.key_state = key_state
        self.key_x = key_x
        self.key_y = key_y
        self.key_holder = key_holder
        self.treasure_taken = treasure_taken
        self.treasure_taker = treasure_taker
        self.treasure_level = treasure_level

        super().__init__(
            PacketType.ZONE_STATE,
            self.encode_payload(),
        )

    def encode_payload(self) -> bytes:
        return struct.pack(
            self.FORMAT,
            self.key_state,
            self.key_x,
            self.key_y,
            (self.key_holder or self._NIL).bytes,
            1 if self.treasure_taken else 0,
            (self.treasure_taker or self._NIL).bytes,
            self.treasure_level,
        )

    @classmethod
    def from_payload(cls, payload: bytes) -> "ZoneStatePacket":
        if len(payload) != cls.SIZE:
            raise ValueError(
                f"ZoneState invalide : "
                f"{len(payload)} octets reçus, "
                f"{cls.SIZE} attendus"
            )

        key_state, key_x, key_y, holder, taken, taker, level = struct.unpack(
            cls.FORMAT,
            payload,
        )

        holder_id = uuid.UUID(bytes=holder)
        taker_id = uuid.UUID(bytes=taker)

        return cls(
            key_state=key_state,
            key_x=key_x,
            key_y=key_y,
            key_holder=None if holder_id == cls._NIL else holder_id,
            treasure_taken=bool(taken),
            treasure_taker=None if taker_id == cls._NIL else taker_id,
            treasure_level=level,
        )

    def __repr__(self) -> str:
        return (
            f"ZoneStatePacket(key_state={self.key_state}, "
            f"key=({self.key_x}, {self.key_y}), "
            f"holder={self.key_holder}, "
            f"treasure_taker={self.treasure_taker}, "
            f"level={self.treasure_level})"
        )

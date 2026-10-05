from __future__ import annotations

import uuid

from ..packet import Packet, PacketType


class SessionPacket(Packet):
    """
    Paquet envoyé par le serveur pour transmettre
    l'identifiant de session attribué au client.
    """

    SIZE = 16

    def __init__(self, session_id: uuid.UUID) -> None:
        self.session_id = session_id

        super().__init__(
            PacketType.SESSION,
            self.encode_payload(),
        )

    def encode_payload(self) -> bytes:
        """
        Encode l'UUID de session sur 16 octets.
        """
        return self.session_id.bytes

    @classmethod
    def from_payload(
        cls,
        payload: bytes,
    ) -> "SessionPacket":
        """
        Décode l'UUID de session reçu du serveur.
        """

        if len(payload) != cls.SIZE:
            raise ValueError(
                f"SessionPacket invalide : "
                f"{len(payload)} octets reçus, "
                f"{cls.SIZE} attendus"
            )

        session_id = uuid.UUID(
            bytes=payload
        )

        return cls(
            session_id=session_id
        )

    def __repr__(self) -> str:
        return (
            f"SessionPacket("
            f"session_id={self.session_id}"
            f")"
        )
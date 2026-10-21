from ..packet import Packet, PacketType


class LogPacket(Packet):

    def __init__(self):

        super().__init__(
            PacketType.LOG
        )
    @classmethod
    def from_payload(cls, payload: bytes):
        return cls(payload)

import struct

from ..packet import Packet, PacketType


class MovePacket(Packet):

    def __init__(self, x, y,z):

        self.x = x
        self.y = y
        self.z = z

        super().__init__(
            PacketType.MOVE,
            struct.pack("!iii", x, y, z)
        )
    @classmethod
    def from_payload(cls, payload):

        x, y, z = struct.unpack(
            "!iii",
            payload
        )

        return cls(
            x,
            y,
            z
        )

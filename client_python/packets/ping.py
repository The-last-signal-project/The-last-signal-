from ..packet import Packet, PacketType


class PingPacket(Packet):

    def __init__(self):

        super().__init__(
            PacketType.PING
        )

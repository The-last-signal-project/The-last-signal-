from ..packet import PacketType


class BanType:
    TEMPORARY = 1
    PERMANENT = 2


class BanPacket:

    def __init__(
        self,
        ban_type,
        reason,
        date_deban=None,
    ):
        self.packet_type = PacketType.BAN
        self.ban_type = ban_type
        self.reason = reason
        self.date_deban = date_deban

    @classmethod
    def from_payload(cls, payload):

        parts = payload.decode("utf-8").split("\0")

        ban_type = int(parts[0])
        reason = parts[1]

        date_deban = parts[2] if len(parts) > 2 else None

        if date_deban == "":
            date_deban = None

        return cls(
            ban_type,
            reason,
            date_deban,
        )
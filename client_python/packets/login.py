import struct

from ..packet import Packet, PacketType


class LoginPacket(Packet):

    def __init__(self, email: str, password: str):

        self.email = email
        self.password = password

        email_bytes = email.encode("utf-8")
        password_bytes = password.encode("utf-8")

        payload = (
            struct.pack("!H", len(email_bytes))
            + email_bytes
            + struct.pack("!H", len(password_bytes))
            + password_bytes
        )

        super().__init__(
            PacketType.LOGIN,
            payload
        )

    @classmethod
    def from_payload(cls, payload: bytes):

        offset = 0

        # -------------------------
        # Email
        # -------------------------

        if len(payload) < 2:
            raise ValueError("Payload LOGIN trop court")

        email_length = struct.unpack(
            "!H",
            payload[offset:offset + 2]
        )[0]

        offset += 2

        if len(payload) < offset + email_length:
            raise ValueError("Email incomplet")

        email = payload[
            offset:offset + email_length
        ].decode("utf-8")

        offset += email_length

        # -------------------------
        # Password
        # -------------------------

        if len(payload) < offset + 2:
            raise ValueError("Password absent")

        password_length = struct.unpack(
            "!H",
            payload[offset:offset + 2]
        )[0]

        offset += 2

        if len(payload) < offset + password_length:
            raise ValueError("Password incomplet")

        password = payload[
            offset:offset + password_length
        ].decode("utf-8")

        return cls(email, password)

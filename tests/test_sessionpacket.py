import uuid
import pytest
from client_python.packets.session import SessionPacket
from client_python.packet import PacketType


def test_session_packet_creation() -> None:
    """
    Verify that creating a SessionPacket with a UUID:
    - stores the UUID correctly;
    - uses PacketType.SESSION;
    - produces the expected payload.
    """
    test_uuid = uuid.uuid4()
    packet = SessionPacket(test_uuid)

    assert packet.session_id == test_uuid
    assert packet.packet_type == PacketType.SESSION
    assert packet.payload == test_uuid.bytes


def test_uuid_encoding() -> None:
    """
    Test that SessionPacket.encode_payload() produces exactly 16 bytes
    corresponding to the UUID.
    """
    test_uuid = uuid.uuid4()
    packet = SessionPacket(test_uuid)
    encoded = packet.encode_payload()

    assert isinstance(encoded, bytes)
    assert len(encoded) == 16
    assert encoded == test_uuid.bytes


def test_uuid_decoding() -> None:
    """
    Test that SessionPacket.from_payload() reconstructs the original UUID correctly.
    """
    test_uuid = uuid.uuid4()
    payload = test_uuid.bytes

    packet = SessionPacket.from_payload(payload)
    assert packet.session_id == test_uuid
    assert packet.packet_type == PacketType.SESSION


def test_round_trip() -> None:
    """
    Test the encode/decode round-trip:
    UUID -> SessionPacket -> encode_payload() -> from_payload() -> SessionPacket
    """
    test_uuid = uuid.uuid4()
    packet = SessionPacket(test_uuid)
    encoded = packet.encode_payload()
    decoded_packet = SessionPacket.from_payload(encoded)

    assert decoded_packet.session_id == test_uuid


def test_invalid_payload_size() -> None:
    """
    Test that SessionPacket.from_payload() raises ValueError when the payload:
    - contains fewer than 16 bytes;
    - contains more than 16 bytes.
    """
    short_payload = b"\x00" * 15
    long_payload = b"\x00" * 17

    with pytest.raises(ValueError):
        SessionPacket.from_payload(short_payload)

    with pytest.raises(ValueError):
        SessionPacket.from_payload(long_payload)


def test_representation() -> None:
    """
    Test that repr(SessionPacket(...)) contains the session UUID.
    """
    test_uuid = uuid.uuid4()
    packet = SessionPacket(test_uuid)
    rep = repr(packet)

    assert str(test_uuid) in rep
    assert "SessionPacket" in rep

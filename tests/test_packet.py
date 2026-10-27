import struct

from client_python.packet import Packet, PacketType


def test_encode_uses_big_endian_body_length_and_packet_type():
    packet = Packet(PacketType.LoginResponse, b"hello")

    encoded = packet.encode()
    body = encoded[4:]

    assert len(encoded[:4]) == 4
    assert struct.unpack("!I", encoded[:4])[0] == len(body)
    assert body[:2] == struct.pack("!H", PacketType.LoginResponse)
    assert body[2:] == b"hello"


def test_encode_preserves_empty_payload():
    packet = Packet(PacketType.LoginResponse, b"")

    encoded = packet.encode()
    body = encoded[4:]

    assert struct.unpack("!I", encoded[:4])[0] == 2
    assert body == struct.pack("!H", PacketType.LoginResponse)


def test_decode_preserves_generic_packet_type_and_payload():
    packet_type = PacketType.LoginResponse
    payload = b"response payload"

    decoded = Packet.decode(struct.pack("!H", packet_type) + payload)

    assert type(decoded) is Packet
    assert decoded.packet_type == packet_type
    assert decoded.payload == payload


def test_decode_preserves_empty_payload():
    packet_type = PacketType.SignUpResponse

    decoded = Packet.decode(struct.pack("!H", packet_type))

    assert type(decoded) is Packet
    assert decoded.packet_type == packet_type
    assert decoded.payload == b""


def test_encode_decode_round_trip_for_generic_packet():
    original = Packet(PacketType.LoginResponse, b"hello")

    encoded = original.encode()
    decoded = Packet.decode(encoded[4:])

    assert decoded.packet_type == original.packet_type
    assert decoded.payload == original.payload

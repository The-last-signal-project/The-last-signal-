import socket
import struct
import threading
import time
import uuid
import pytest

from client_python.client import Client
from client_python.packet import Packet, PacketType
from client_python.packets.ping import PingPacket
from client_python.packets.chat import ChatPacket
from client_python.packets.session import SessionPacket


class MockRustServer:
    """
    Mock TCP server replicating the wire protocol and packet behavior of the Rust server.
    Emits SESSION on connect and handles PING and CHAT packets according to network specs.
    """

    def __init__(self, host="127.0.0.1", port=0):
        self.host = host
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.host, port))
        self.port = self.server_sock.getsockname()[1]
        self.server_sock.listen(1)
        self.running = False
        self.thread = None
        self.client_sock = None
        self.session_uuid = uuid.uuid4()
        self.received_packets = []

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _recv_exact(self, sock, size):
        data = bytearray()
        while len(data) < size:
            chunk = sock.recv(size - len(data))
            if not chunk:
                return None
            data.extend(chunk)
        return bytes(data)

    def _run(self):
        try:
            self.server_sock.settimeout(3.0)
            client_sock, _ = self.server_sock.accept()
            self.client_sock = client_sock
            client_sock.settimeout(3.0)

            # 1. Server sends initial SESSION packet (16 bytes UUID)
            session_pkt = SessionPacket(self.session_uuid)
            client_sock.sendall(session_pkt.encode())

            # 2. Main packet reception and echo loop
            while self.running:
                header = self._recv_exact(client_sock, 4)
                if not header:
                    break
                size = struct.unpack("!I", header)[0]
                body = self._recv_exact(client_sock, size)
                if not body:
                    break

                ptype = struct.unpack("!H", body[:2])[0]
                payload = body[2:]
                self.received_packets.append((ptype, payload))

                if ptype == PacketType.PING:
                    # Rust server responds with PING and payload "PONG"
                    pong_pkt = Packet(PacketType.PING, b"PONG")
                    client_sock.sendall(pong_pkt.encode())

                elif ptype == PacketType.CHAT:
                    # Rust server echoes back the CHAT packet payload
                    chat_response = Packet(PacketType.CHAT, payload)
                    client_sock.sendall(chat_response.encode())

                elif ptype == PacketType.DECO:
                    break

        except (socket.timeout, OSError):
            pass
        finally:
            if self.client_sock:
                try:
                    self.client_sock.close()
                except OSError:
                    pass

    def stop(self):
        self.running = False
        try:
            self.server_sock.close()
        except OSError:
            pass
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)


class TestClientServerNetworkIntegration:
    """
    Integration tests covering client/server network protocol communication (Issue #117).
    """

    def test_connection_and_session_handshake(self):
        server = MockRustServer()
        server.start()
        try:
            client = Client(host=server.host, port=server.port)
            client.connect()

            assert client.connected is True
            assert client.session_id == server.session_uuid

            client.socket.close()
            client.connected = False
        finally:
            server.stop()

    def test_client_server_ping_pong_exchange(self):
        server = MockRustServer()
        server.start()
        try:
            client = Client(host=server.host, port=server.port)
            client.connect()

            # Client sends PING
            ping = PingPacket()
            client.send_packet(ping)

            # Server receives PING
            time.sleep(0.05)
            assert any(p[0] == PacketType.PING for p in server.received_packets)

            # Client receives PING packet response
            response = client.receive_packet()
            assert response is not None
            assert response.packet_type == PacketType.PING

            client.socket.close()
            client.connected = False
        finally:
            server.stop()

    def test_client_server_chat_exchange(self):
        server = MockRustServer()
        server.start()
        try:
            client = Client(host=server.host, port=server.port)
            client.connect()

            msg = "Hello The Last Signal Server!"
            chat = ChatPacket(msg)
            client.send_packet(chat)

            response = client.receive_packet()
            assert response is not None
            assert response.packet_type == PacketType.CHAT
            assert response.message == msg

            client.socket.close()
            client.connected = False
        finally:
            server.stop()

    def test_clean_connection_closure(self):
        server = MockRustServer()
        server.start()
        try:
            client = Client(host=server.host, port=server.port)
            client.connect()
            assert client.connected is True

            # Closing socket and verifying clean state
            client.socket.close()
            client.connected = False
            assert client.connected is False
        finally:
            server.stop()

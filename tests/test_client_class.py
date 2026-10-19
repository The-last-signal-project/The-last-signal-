import socket
import struct
from unittest.mock import MagicMock, call, patch

import pytest

from client_python.client import Client, MAX_PACKET_SIZE
from client_python.packet import Packet, PacketType


class TestClientInit:
    """Tests for Client.__init__()."""

    def test_init_default_values(self):
        client = Client()

        assert client.host == "127.0.0.1"
        assert client.port == 5000
        assert client.socket is None
        assert client.connected is False
        assert client.session_id is None

    def test_init_custom_values(self):
        client = Client(
            host="192.168.1.10",
            port=6000,
        )

        assert client.host == "192.168.1.10"
        assert client.port == 6000
        assert client.socket is None
        assert client.connected is False
        assert client.session_id is None


class TestClientConnect:
    """Tests for Client.connect()."""

    @patch("client_python.client.log")
    @patch("client_python.client.time.sleep")
    @patch("client_python.client.time.monotonic")
    @patch("client_python.client.socket.socket")
    def test_connect_success(
        self,
        mock_socket,
        mock_monotonic,
        mock_sleep,
        mock_log,
    ):
        mock_monotonic.side_effect = [0, 0]

        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        packet = MagicMock()
        packet.packet_type = PacketType.CHAT

        client = Client()

        with patch.object(
            client,
            "receive_packet",
            return_value=packet,
        ):
            client.connect()

        assert client.connected is True
        assert client.socket is mock_socket_instance

        mock_socket_instance.settimeout.assert_any_call(1)
        mock_socket_instance.connect.assert_called_once_with(
            ("127.0.0.1", 5000)
        )
        mock_socket_instance.settimeout.assert_any_call(None)

        mock_sleep.assert_not_called()
        mock_log.assert_called_once()

    @patch("client_python.client.log")
    @patch("client_python.client.time.sleep")
    @patch("client_python.client.time.monotonic")
    @patch("client_python.client.socket.socket")
    def test_connect_session_packet(
        self,
        mock_socket,
        mock_monotonic,
        mock_sleep,
        mock_log,
    ):
        mock_monotonic.side_effect = [0, 0]

        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        packet = MagicMock()
        packet.packet_type = PacketType.SESSION
        packet.session_id = "test-session-id"

        client = Client()

        with patch.object(
            client,
            "receive_packet",
            return_value=packet,
        ):
            client.connect()

        assert client.connected is True
        assert client.session_id == "test-session-id"

        mock_sleep.assert_not_called()
        mock_log.assert_called_once()

    @patch("client_python.client.log")
    @patch("client_python.client.time.sleep")
    @patch("client_python.client.time.monotonic")
    @patch("client_python.client.socket.socket")
    def test_connect_connection_refused_then_success(
        self,
        mock_socket,
        mock_monotonic,
        mock_sleep,
        mock_log,
    ):
        mock_monotonic.side_effect = [0, 0, 0]

        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        connect_results = [
            ConnectionRefusedError(),
            None,
        ]

        mock_socket_instance.connect.side_effect = connect_results

        packet = MagicMock()
        packet.packet_type = PacketType.CHAT

        client = Client()

        with patch.object(
            client,
            "receive_packet",
            return_value=packet,
        ):
            client.connect()

        assert client.connected is True
        assert mock_socket_instance.connect.call_count == 2

        mock_socket_instance.close.assert_called_once()
        mock_sleep.assert_called_once_with(0.5)
        mock_log.assert_called_once()

    @patch("client_python.client.log")
    @patch("client_python.client.time.sleep")
    @patch("client_python.client.time.monotonic")
    @patch("client_python.client.socket.socket")
    def test_connect_socket_timeout_then_success(
        self,
        mock_socket,
        mock_monotonic,
        mock_sleep,
        mock_log,
    ):
        mock_monotonic.side_effect = [0, 0, 0]

        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        mock_socket_instance.connect.side_effect = [
            socket.timeout(),
            None,
        ]

        packet = MagicMock()
        packet.packet_type = PacketType.CHAT

        client = Client()

        with patch.object(
            client,
            "receive_packet",
            return_value=packet,
        ):
            client.connect()

        assert client.connected is True
        assert mock_socket_instance.connect.call_count == 2

        mock_socket_instance.close.assert_called_once()
        mock_sleep.assert_called_once_with(0.5)
        mock_log.assert_called_once()

    @patch("client_python.client.time.monotonic")
    @patch("client_python.client.socket.socket")
    def test_connect_timeout(
        self,
        mock_socket,
        mock_monotonic,
    ):
        mock_monotonic.side_effect = [
            0,
            90,
        ]

        client = Client()

        with pytest.raises(SystemExit):
            client.connect()

        assert client.connected is False
        assert client.socket is None

        mock_socket.assert_not_called()

    @patch("client_python.client.socket.socket")
    def test_connect_when_already_connected(
        self,
        mock_socket,
    ):
        client = Client()
        client.connected = True

        client.connect()

        mock_socket.assert_not_called()

    @patch("client_python.client.socket.socket")
    def test_connect_unexpected_exception(
        self,
        mock_socket,
    ):
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        error = RuntimeError("unexpected error")

        mock_socket_instance.connect.side_effect = error

        client = Client()

        with pytest.raises(RuntimeError, match="unexpected error"):
            client.connect()

        assert client.connected is False
        assert client.socket is None

        mock_socket_instance.close.assert_called_once()

    @patch("client_python.client.log")
    @patch("client_python.client.time.sleep")
    @patch("client_python.client.time.monotonic")
    @patch("client_python.client.socket.socket")
    def test_connect_non_session_packet_leaves_session_id_none(
        self,
        mock_socket,
        mock_monotonic,
        mock_sleep,
        mock_log,
    ):
        """Non-SESSION handshake packet leaves session_id as None."""
        mock_monotonic.side_effect = [0, 0]

        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        packet = MagicMock()
        packet.packet_type = PacketType.CHAT

        client = Client()

        with patch.object(
            client,
            "receive_packet",
            return_value=packet,
        ):
            client.connect()

        assert client.connected is True
        assert client.session_id is None
        mock_sleep.assert_not_called()
        mock_log.assert_called_once()

    @patch("client_python.client.socket.socket")
    def test_connect_immediate_server_disconnect_raises_attribute_error(
        self,
        mock_socket,
    ):
        """Server EOF during handshake triggers AttributeError on None."""
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        client = Client()

        with patch.object(
            client,
            "receive_packet",
            return_value=None,
        ):
            with pytest.raises(AttributeError):
                client.connect()

        assert client.connected is False
        assert client.socket is None
        mock_socket_instance.close.assert_called_once()

    @patch("client_python.client.time.monotonic")
    @patch("client_python.client.socket.socket")
    def test_connect_initial_ban_packet_triggers_system_exit(
        self,
        mock_socket,
        mock_monotonic,
    ):
        """Initial BAN packet raises SystemExit(1) with shared wire layout."""
        mock_monotonic.side_effect = [0, 0]
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Shared wire layout with Rust encode_ban tests: type=9, "2\0Exploit\0"
        body = struct.pack("!H", 9) + b"2\x00Exploit\x00"
        header = len(body).to_bytes(4, "big")

        client = Client()

        with patch.object(
            client,
            "_recv_exact",
            side_effect=[header, body],
        ):
            with pytest.raises(SystemExit) as exc_info:
                client.connect()

        assert exc_info.value.code == 1

    @pytest.mark.xfail(
        strict=True,
        raises=AssertionError,
        reason=(
            "connect() leaks socket and leaves connected=True on SystemExit; "
            "see follow-up issue on connect cleanup"
        ),
    )
    @patch("client_python.client.time.monotonic")
    @patch("client_python.client.socket.socket")
    def test_connect_initial_ban_packet_socket_cleanup(
        self,
        mock_socket,
        mock_monotonic,
    ):
        """BAN during connect should close socket and clear connected."""
        mock_monotonic.side_effect = [0, 0]
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        body = struct.pack("!H", 9) + b"2\x00Exploit\x00"
        header = len(body).to_bytes(4, "big")

        client = Client()

        with patch.object(
            client,
            "_recv_exact",
            side_effect=[header, body],
        ):
            with pytest.raises(SystemExit):
                client.connect()

        # State assertions go after with block to verify cleanup
        assert client.connected is False
        mock_socket_instance.close.assert_called_once()

    @patch("client_python.client.time.monotonic")
    @patch("client_python.client.socket.socket")
    def test_connect_socket_creation_os_error(
        self,
        mock_socket,
        mock_monotonic,
    ):
        """OSError during socket creation cleanly propagates."""
        mock_monotonic.side_effect = [0, 0]
        mock_socket.side_effect = OSError("Too many open files")

        client = Client()

        with pytest.raises(OSError, match="Too many open files"):
            client.connect()

        assert client.connected is False
        assert client.socket is None

    @patch("client_python.client.log")
    @patch("client_python.client.time.sleep")
    @patch("client_python.client.time.monotonic")
    @patch("client_python.client.socket.socket")
    def test_connect_multiple_retries_close_each_failed_socket(
        self,
        mock_socket,
        mock_monotonic,
        mock_sleep,
        mock_log,
    ):
        """Each retry closes its own failed socket instance before next."""
        mock_monotonic.side_effect = [0, 0, 0, 0]

        sock1 = MagicMock()
        sock1.connect.side_effect = ConnectionRefusedError()

        sock2 = MagicMock()
        sock2.connect.side_effect = ConnectionRefusedError()

        sock3 = MagicMock()
        sock3.connect.return_value = None

        mock_socket.side_effect = [sock1, sock2, sock3]

        packet = MagicMock()
        packet.packet_type = PacketType.CHAT

        client = Client()

        with patch.object(
            client,
            "receive_packet",
            return_value=packet,
        ):
            client.connect()

        assert client.connected is True
        assert client.socket is sock3
        sock1.close.assert_called_once()
        sock2.close.assert_called_once()
        assert mock_sleep.call_args_list == [call(0.5), call(0.5)]
        mock_log.assert_called_once()


class TestClientSendPacket:
    """Tests for Client.send_packet()."""

    def test_send_packet_when_disconnected(self):
        client = Client()
        client.connected = False

        packet = MagicMock()

        with patch.object(client.socket, "sendall") if client.socket else patch(
            "client_python.client.log"
        ):
            client.send_packet(packet)

        packet.encode.assert_not_called()

    def test_send_packet_success(self):
        client = Client()
        client.connected = True
        client.socket = MagicMock()

        packet = MagicMock()
        encoded_packet = b"test-packet"

        packet.encode.return_value = encoded_packet

        client.send_packet(packet)

        packet.encode.assert_called_once()
        client.socket.sendall.assert_called_once_with(encoded_packet)

    @patch("client_python.client.log")
    def test_send_packet_error(self, mock_log):
        client = Client()
        client.connected = True
        client.socket = MagicMock()

        packet = MagicMock()

        packet.encode.side_effect = RuntimeError("send error")

        client.send_packet(packet)

        mock_log.assert_called_once()

    @pytest.mark.parametrize(
        "error",
        [
            BrokenPipeError("Broken pipe"),
            ConnectionResetError("Connection reset"),
            TimeoutError("timed out"),
            OSError("Network unreachable"),
        ],
    )
    def test_send_packet_socket_error_logged_gracefully(self, error):
        """Socket errors during sendall are caught and logged as ERROR."""
        client = Client()
        client.connected = True
        client.socket = MagicMock()
        client.socket.sendall.side_effect = error

        packet = MagicMock()
        packet.encode.return_value = b"test-payload"

        with patch("client_python.client.log") as mock_log:
            client.send_packet(packet)

        mock_log.assert_called_once()
        assert mock_log.call_args[0][1] == "ERROR"
        # Documents that send_packet does not mutate connected state
        assert client.connected is True

    def test_send_packet_socket_none_with_connected_true_logged(self):
        """Sending with socket=None when connected logs ERROR without crash."""
        client = Client()
        client.connected = True
        client.socket = None

        packet = MagicMock()
        packet.encode.return_value = b"test-payload"

        with patch("client_python.client.log") as mock_log:
            client.send_packet(packet)

        mock_log.assert_called_once()
        assert mock_log.call_args[0][1] == "ERROR"

    def test_send_packet_empty_payload_hand_built_wire_bytes(self):
        """PING packet serialization sends exact hand-built wire bytes."""
        client = Client()
        client.connected = True
        client.socket = MagicMock()

        packet = Packet(PacketType.PING)
        client.send_packet(packet)

        # Wire format: 4-byte len (2) + 2-byte type (1 for PING)
        expected_wire = b"\x00\x00\x00\x02\x00\x01"
        client.socket.sendall.assert_called_once_with(expected_wire)


class TestClientRecvExact:
    """Tests for Client._recv_exact()."""

    def test_recv_exact_when_disconnected(self):
        client = Client()
        client.connected = False
        client.socket = MagicMock()

        result = client._recv_exact(4)

        assert result is None
        client.socket.recv.assert_not_called()

    def test_recv_exact_single_chunk(self):
        client = Client()
        client.connected = True
        client.socket = MagicMock()

        client.socket.recv.return_value = b"test"

        result = client._recv_exact(4)

        assert result == b"test"
        client.socket.recv.assert_called_once_with(4)

    def test_recv_exact_multiple_chunks(self):
        client = Client()
        client.connected = True
        client.socket = MagicMock()

        client.socket.recv.side_effect = [
            b"te",
            b"st",
        ]

        result = client._recv_exact(4)

        assert result == b"test"

        assert client.socket.recv.call_count == 2
        client.socket.recv.assert_any_call(4)
        client.socket.recv.assert_any_call(2)

    def test_recv_exact_connection_closed(self):
        client = Client()
        client.connected = True
        client.socket = MagicMock()

        client.socket.recv.return_value = b""

        result = client._recv_exact(4)

        assert result is None
        assert client.connected is False

    @patch("client_python.client.log")
    def test_recv_exact_socket_error(self, mock_log):
        client = Client()
        client.connected = True
        client.socket = MagicMock()

        client.socket.recv.side_effect = OSError("socket error")

        result = client._recv_exact(4)

        assert result is None
        assert client.connected is False

        mock_log.assert_called_once()

    def test_recv_exact_zero_size_returns_empty_bytes(self):
        """_recv_exact(0) immediately returns empty bytes without reading."""
        client = Client()
        client.connected = True
        client.socket = MagicMock()

        result = client._recv_exact(0)

        assert result == b""
        client.socket.recv.assert_not_called()

    def test_recv_exact_partial_read_then_eof(self):
        """EOF after partial read returns None and marks connected=False."""
        client = Client()
        client.connected = True
        client.socket = MagicMock()
        client.socket.recv.side_effect = [b"AB", b""]

        result = client._recv_exact(4)

        # Asserts return is None and not b"AB"
        assert result is None
        assert client.connected is False

    def test_recv_exact_partial_read_then_socket_error(self):
        """Socket error after partial read returns None and logs ERROR."""
        client = Client()
        client.connected = True
        client.socket = MagicMock()
        client.socket.recv.side_effect = [
            b"AB",
            ConnectionResetError("Connection reset"),
        ]

        with patch("client_python.client.log") as mock_log:
            result = client._recv_exact(4)

        assert result is None
        assert client.connected is False
        mock_log.assert_called_once()
        assert mock_log.call_args[0][1] == "ERROR"

    def test_recv_exact_requests_exact_remaining_bytes_across_three_chunks(
        self,
    ):
        """Buffer chunks request only the remaining byte count each loop."""
        client = Client()
        client.connected = True
        client.socket = MagicMock()
        client.socket.recv.side_effect = [
            b"1234",
            b"5678",
            b"90",
        ]

        result = client._recv_exact(10)

        assert result == b"1234567890"
        assert client.socket.recv.call_args_list == [
            call(10),
            call(6),
            call(2),
        ]

    def test_recv_exact_socket_none_with_connected_true_returns_none(self):
        """_recv_exact with socket=None returns None and logs ERROR."""
        client = Client()
        client.connected = True
        client.socket = None

        with patch("client_python.client.log") as mock_log:
            result = client._recv_exact(4)

        assert result is None
        assert client.connected is False
        mock_log.assert_called_once()
        assert mock_log.call_args[0][1] == "ERROR"


class TestClientReceivePacket:
    """Tests for Client.receive_packet()."""

    def test_receive_packet_when_disconnected(self):
        client = Client()
        client.connected = False

        result = client.receive_packet()

        assert result is None

    def test_receive_packet_success(self):
        client = Client()
        client.connected = True
        client.socket = MagicMock()

        payload = b"test-payload"
        size = len(payload).to_bytes(4, "big")

        client.socket.recv.side_effect = [
            size,
            payload,
        ]

        packet = MagicMock()
        packet.packet_type = PacketType.CHAT

        with patch(
            "client_python.client.Packet.decode",
            return_value=packet,
        ):
            result = client.receive_packet()

        assert result is packet
        assert client.connected is True

    def test_receive_packet_header_error(self):
        client = Client()
        client.connected = True

        with patch.object(
            client,
            "_recv_exact",
            return_value=None,
        ):
            result = client.receive_packet()

        assert result is None

    def test_receive_packet_data_error(self):
        client = Client()
        client.connected = True

        calls = 0

        def fake_recv_exact(size):
            nonlocal calls

            calls += 1

            if calls == 1:
                return (4).to_bytes(4, "big")

            return None

        with patch.object(
            client,
            "_recv_exact",
            side_effect=fake_recv_exact,
        ):
            result = client.receive_packet()

        assert result is None

    @patch("client_python.client.log")
    def test_receive_packet_decode_error(self, mock_log):
        client = Client()
        client.connected = True

        payload = b"test"

        with patch.object(
            client,
            "_recv_exact",
            side_effect=[
                len(payload).to_bytes(4, "big"),
                payload,
            ],
        ):
            with patch(
                "client_python.client.Packet.decode",
                side_effect=ValueError("decode error"),
            ):
                result = client.receive_packet()

        assert result is None
        mock_log.assert_called_once()

    def test_receive_packet_ban_packet_raises_system_exit(self):
        """BAN packet in receive loop triggers SystemExit(1)."""
        client = Client()
        client.connected = True

        # Shared wire layout: type=9 (BAN), payload="2\0Exploit\0"
        body = struct.pack("!H", 9) + b"2\x00Exploit\x00"
        header = len(body).to_bytes(4, "big")

        with patch.object(
            client,
            "_recv_exact",
            side_effect=[header, body],
        ):
            with pytest.raises(SystemExit) as exc_info:
                client.receive_packet()

        assert exc_info.value.code == 1

    @patch("client_python.client.log")
    def test_receive_packet_oversized_header_rejected_before_allocating(self, mock_log):
        """Oversized header (>10 MB) must be rejected before body recv."""
        client = Client()
        client.connected = True

        oversized = MAX_PACKET_SIZE + 1
        header = oversized.to_bytes(4, "big")

        calls = []

        def fake_recv(n):
            calls.append(n)
            if n == 4:
                return header
            if n >= 2:
                return struct.pack("!H", int(PacketType.PING))
            return b"\x00" * n

        with patch.object(
            client,
            "_recv_exact",
            side_effect=fake_recv,
        ):
            assert client.receive_packet() is None
            assert calls == [4]
            assert client.connected is False
        mock_log.assert_called_once()
        assert mock_log.call_args.args[1] == "ERROR"

    def test_receive_packet_accepts_maximum_declared_size(self):
        client = Client()
        client.connected = True
        packet = MagicMock()
        packet.packet_type = PacketType.PING
        body = struct.pack("!H", int(PacketType.PING))

        with patch.object(
            client,
            "_recv_exact",
            side_effect=[MAX_PACKET_SIZE.to_bytes(4, "big"), body],
        ) as mock_recv:
            with patch("client_python.client.Packet.decode", return_value=packet):
                assert client.receive_packet() is packet

        assert [call.args[0] for call in mock_recv.call_args_list] == [4, MAX_PACKET_SIZE]
        assert client.connected is True

    @patch("client_python.client.log")
    def test_receive_packet_zero_size_payload_fails_decode(self, mock_log):
        """Payload size of 0 fails decode and logs ERROR without crash.

        _recv_exact(0) returns b"". In receive_packet(), line 125 checks
        `if data is None:` which is False for b"", so decode(b"") executes,
        raises struct.error, and is logged as ERROR.
        """
        client = Client()
        client.connected = True

        header = (0).to_bytes(4, "big")

        with patch.object(
            client,
            "_recv_exact",
            side_effect=[header, b""],
        ):
            result = client.receive_packet()

        assert result is None
        mock_log.assert_called_once()
        assert mock_log.call_args[0][1] == "ERROR"

    @patch("client_python.client.log")
    def test_receive_packet_struct_error_during_decode_returns_none(
        self,
        mock_log,
    ):
        """Non-empty 1-byte body fails struct unpack, returns None and logs."""
        client = Client()
        client.connected = True

        header = (1).to_bytes(4, "big")

        with patch.object(
            client,
            "_recv_exact",
            side_effect=[header, b"\x01"],
        ):
            result = client.receive_packet()

        assert result is None
        mock_log.assert_called_once()
        assert mock_log.call_args[0][1] == "ERROR"


class TestClientDisconnect:
    """Tests for Client.disconnect()."""

    @patch("client_python.client.time.sleep")
    def test_disconnect_with_socket(self, mock_sleep):
        client = Client()
        client.connected = True
        client.socket = MagicMock()

        with patch.object(
            client,
            "send_packet",
        ) as mock_send:
            client.disconnect("test")

        mock_send.assert_called_once()
        mock_sleep.assert_called_once_with(10)

        client.socket.close.assert_called_once()

        assert client.connected is False

    @patch("client_python.client.time.sleep")
    def test_disconnect_without_socket(self, mock_sleep):
        client = Client()
        client.connected = True
        client.socket = None

        with patch.object(
            client,
            "send_packet",
        ) as mock_send:
            client.disconnect("test")

        mock_send.assert_called_once()
        mock_sleep.assert_called_once_with(10)

        assert client.connected is False

    @patch("client_python.client.time.sleep")
    def test_disconnect_when_already_disconnected(self, mock_sleep):
        client = Client()
        client.connected = False
        client.socket = None

        with patch.object(
            client,
            "send_packet",
        ) as mock_send:
            client.disconnect("test")

        mock_send.assert_called_once()
        mock_sleep.assert_called_once_with(10)

        assert client.connected is False

    @pytest.mark.parametrize(
        "reason",
        [
            "quit",
            "Déconnexion 🛑",
        ],
    )
    @patch("client_python.client.time.sleep")
    def test_disconnect_sends_decopacket_with_hand_built_wire_bytes(
        self,
        mock_sleep,
        reason,
    ):
        """Disconnect sends DECO packet pinning client encoding format.

        The server handler at server_rust/src/network/handler.rs:1289-1296
        ignores the payload; this test pins the client's current encoding.
        """
        client = Client()
        client.connected = True
        client.socket = MagicMock()

        client.disconnect(reason)

        mock_sleep.assert_called_once_with(10)
        assert client.connected is False

        raw_payload = reason.encode("utf-8")
        expected_wire = (
            struct.pack("!IH", 2 + len(raw_payload), int(PacketType.DECO))
            + raw_payload
        )
        client.socket.sendall.assert_called_once_with(expected_wire)

    @pytest.mark.xfail(
        strict=True,
        raises=AssertionError,
        reason=(
            "disconnect lacks try/finally around socket.close(); "
            "exception prevents connected = False; see follow-up issue on "
            "disconnect try/finally"
        ),
    )
    @patch("client_python.client.time.sleep")
    def test_disconnect_socket_close_exception_handled(
        self,
        mock_sleep,
    ):
        """OSError during socket.close() should still mark connected=False."""
        client = Client()
        client.connected = True
        client.socket = MagicMock()
        client.socket.close.side_effect = OSError("close failure")

        try:
            client.disconnect("quit")
        except OSError:
            pass

        mock_sleep.assert_called_once_with(10)
        assert client.connected is False

import socket
from unittest.mock import MagicMock, patch

import pytest

from client_python.client import Client
from client_python.packet import PacketType


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
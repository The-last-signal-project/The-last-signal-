use log::error;
use std::io;

use serde::{Deserialize, Serialize};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;

pub const MAX_PACKET_SIZE: usize = 10 * 1024 * 1024;

/// Types de paquets.
#[repr(u16)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PacketType {
    Ping = 1,
    Login = 2,
    Chat = 3,
    Move = 4,
    Log = 5,
    SignUp = 6,
    LoginResponse = 7,
    SignUpResponse = 8,
    BAN = 9,
    DECO = 10,
    MarketBuy = 11,
    MarketSell = 12,
    MarketCancelBuy = 13,
    MarketCancelSell = 14,
    PlayerState = 15,
    PlayerRemove = 16,
    Session = 17,
    AccountListRequest = 18,
    AccountListResponse = 19,
    AccountCreate = 20,
    AccountSelect = 21,
    AccountResult = 22,
}
#[derive(Debug, Clone, Copy)]
pub enum BanType {
    Temporary = 1,
    Permanent = 2,
}
pub struct BanInfo {
    pub ban_type: BanType,
    pub reason: String,
    pub date_deban: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub enum LogLevel {
    TRACE,
    DEBUG,
    INFO,
    WARNING,
    ERROR,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ClientLog {
    pub level: LogLevel,
    pub module: String,
    pub file: String,
    pub line: u32,
    pub message: String,
}
impl PacketType {
    pub fn from_u16(value: u16) -> Option<Self> {
        match value {
            1 => Some(PacketType::Ping),
            2 => Some(PacketType::Login),
            3 => Some(PacketType::Chat),
            4 => Some(PacketType::Move),
            5 => Some(PacketType::Log),
            6 => Some(PacketType::SignUp),
            7 => Some(PacketType::LoginResponse),
            8 => Some(PacketType::SignUpResponse),
            9 => Some(PacketType::BAN),
            10 => Some(PacketType::DECO),
            11 => Some(PacketType::MarketBuy),
            12 => Some(PacketType::MarketSell),
            13 => Some(PacketType::MarketCancelBuy),
            14 => Some(PacketType::MarketCancelSell),
            15 => Some(PacketType::PlayerState),
            16 => Some(PacketType::PlayerRemove),
            17 => Some(PacketType::Session),
            18 => Some(PacketType::AccountListRequest),
            19 => Some(PacketType::AccountListResponse),
            20 => Some(PacketType::AccountCreate),
            21 => Some(PacketType::AccountSelect),
            22 => Some(PacketType::AccountResult),
            _ => None,
        }
    }
}

/// Un paquet réseau.
#[derive(Debug, Clone)]
pub struct Packet {
    pub packet_type: PacketType,
    pub payload: Vec<u8>,
}

impl Packet {
    pub fn new(packet_type: PacketType, payload: Vec<u8>) -> Self {
        Self {
            packet_type,
            payload,
        }
    }

    /// Analyse les octets du corps d'un paquet (type sur 2 octets suivi du payload).
    pub fn parse_body(body: &[u8]) -> io::Result<Self> {
        if body.len() < 2 {
            error!("paquet invalide");
            return Err(io::Error::new(
                io::ErrorKind::InvalidData,
                "Paquet invalide.",
            ));
        }

        let packet_type = u16::from_be_bytes([body[0], body[1]]);
        let packet_type = PacketType::from_u16(packet_type).ok_or_else(|| {
            error!("Type de paquet inconnu");
            io::Error::new(io::ErrorKind::InvalidData, "Type de paquet inconnu.")
        })?;

        let payload = body[2..].to_vec();

        Ok(Self {
            packet_type,
            payload,
        })
    }
}
pub fn encode_ban(ban_type: BanType, reason: &str, date_deban: Option<&str>) -> Vec<u8> {
    format!(
        "{}\0{}\0{}",
        ban_type as u8,
        reason,
        date_deban.unwrap_or("")
    )
    .into_bytes()
}

/// Envoie un paquet.
pub async fn send_packet(stream: &mut TcpStream, packet: &Packet) -> io::Result<()> {
    let payload_size = 2 + packet.payload.len();

    if payload_size > MAX_PACKET_SIZE {
        error!("paquet trop volumineux");
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "Paquet trop volumineux.",
        ));
    }

    let size = (payload_size as u32).to_be_bytes();

    stream.write_all(&size).await?;

    let packet_type = (packet.packet_type as u16).to_be_bytes();

    stream.write_all(&packet_type).await?;

    stream.write_all(&packet.payload).await?;

    Ok(())
}

/// Reçoit exactement `size` octets.
async fn recv_exact(stream: &mut TcpStream, size: usize) -> io::Result<Vec<u8>> {
    let mut buffer = vec![0u8; size];

    stream.read_exact(&mut buffer).await?;

    Ok(buffer)
}

/// Reçoit un paquet.
pub async fn receive_packet(stream: &mut TcpStream) -> io::Result<Packet> {
    // Taille
    let header = recv_exact(stream, 4).await?;

    let size = u32::from_be_bytes([header[0], header[1], header[2], header[3]]) as usize;

    if size < 2 {
        error!("paquet invalide");
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "Paquet invalide.",
        ));
    }

    if size > MAX_PACKET_SIZE {
        error!("paquet trop volumineux");
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "Paquet trop volumineux.",
        ));
    }

    // Corps du paquet
    let data = recv_exact(stream, size).await?;

    Packet::parse_body(&data)
}

#[cfg(test)]
mod tests {
    use super::*;
    use tokio::io::{AsyncReadExt, AsyncWriteExt};
    use tokio::net::{TcpListener, TcpStream};
    use tokio::time::{Duration, timeout};

    async fn create_tcp_pair() -> (TcpStream, TcpStream) {
        let listener = TcpListener::bind("127.0.0.1:0")
            .await
            .expect("failed to bind listener");
        let addr = listener.local_addr().expect("failed to get local addr");

        let client_fut = TcpStream::connect(addr);
        let server_fut = listener.accept();

        let (client_res, server_res) = tokio::join!(client_fut, server_fut);
        let client_stream = client_res.expect("client connect failed");
        let (server_stream, _) = server_res.expect("server accept failed");

        (client_stream, server_stream)
    }

    #[test]
    fn test_packet_type_from_u16_all_valid() {
        assert_eq!(PacketType::from_u16(1), Some(PacketType::Ping));
        assert_eq!(PacketType::from_u16(2), Some(PacketType::Login));
        assert_eq!(PacketType::from_u16(3), Some(PacketType::Chat));
        assert_eq!(PacketType::from_u16(4), Some(PacketType::Move));
        assert_eq!(PacketType::from_u16(5), Some(PacketType::Log));
        assert_eq!(PacketType::from_u16(6), Some(PacketType::SignUp));
        assert_eq!(PacketType::from_u16(7), Some(PacketType::LoginResponse));
        assert_eq!(PacketType::from_u16(8), Some(PacketType::SignUpResponse));
        assert_eq!(PacketType::from_u16(9), Some(PacketType::BAN));
        assert_eq!(PacketType::from_u16(10), Some(PacketType::DECO));
        assert_eq!(PacketType::from_u16(11), Some(PacketType::MarketBuy));
        assert_eq!(PacketType::from_u16(12), Some(PacketType::MarketSell));
        assert_eq!(PacketType::from_u16(13), Some(PacketType::MarketCancelBuy));
        assert_eq!(PacketType::from_u16(14), Some(PacketType::MarketCancelSell));
        assert_eq!(PacketType::from_u16(15), Some(PacketType::PlayerState));
        assert_eq!(PacketType::from_u16(16), Some(PacketType::PlayerRemove));
        assert_eq!(PacketType::from_u16(17), Some(PacketType::Session));
    }

    #[test]
    fn test_packet_type_from_u16_invalid_values() {
        assert_eq!(PacketType::from_u16(0), None);
        assert_eq!(PacketType::from_u16(18), None);
        assert_eq!(PacketType::from_u16(100), None);
        assert_eq!(PacketType::from_u16(999), None);
        assert_eq!(PacketType::from_u16(u16::MAX), None);
    }

    #[test]
    fn test_encode_ban_temporary() {
        let encoded = encode_ban(
            BanType::Temporary,
            "Cheating detected",
            Some("2026-12-31 23:59:59"),
        );
        assert_eq!(encoded, b"1\0Cheating detected\02026-12-31 23:59:59");
    }

    #[test]
    fn test_encode_ban_permanent() {
        let encoded = encode_ban(BanType::Permanent, "Severe exploit", None);
        assert_eq!(encoded, b"2\0Severe exploit\0");
    }

    #[tokio::test]
    async fn test_receive_packet_size_zero_fails() {
        let (mut client, mut server) = create_tcp_pair().await;

        tokio::spawn(async move {
            let size: u32 = 0;
            let _ = client.write_all(&size.to_be_bytes()).await;
        });

        let result = receive_packet(&mut server).await;
        assert!(result.is_err());
        let err = result.unwrap_err();
        assert_eq!(err.kind(), io::ErrorKind::InvalidData);
        assert_eq!(err.to_string(), "Paquet invalide.");
    }

    #[tokio::test]
    async fn test_receive_packet_size_one_fails() {
        let (mut client, mut server) = create_tcp_pair().await;

        tokio::spawn(async move {
            let size: u32 = 1;
            let _ = client.write_all(&size.to_be_bytes()).await;
        });

        let result = receive_packet(&mut server).await;
        assert!(result.is_err());
        let err = result.unwrap_err();
        assert_eq!(err.kind(), io::ErrorKind::InvalidData);
        assert_eq!(err.to_string(), "Paquet invalide.");
    }

    #[tokio::test]
    async fn test_receive_packet_exceeds_max_size() {
        let (mut client, mut server) = create_tcp_pair().await;

        tokio::spawn(async move {
            let size = (MAX_PACKET_SIZE + 1) as u32;
            let _ = client.write_all(&size.to_be_bytes()).await;
        });

        let result = receive_packet(&mut server).await;
        assert!(result.is_err());
        let err = result.unwrap_err();
        assert_eq!(err.kind(), io::ErrorKind::InvalidData);
        assert_eq!(err.to_string(), "Paquet trop volumineux.");
    }

    #[tokio::test]
    async fn test_receive_packet_unknown_packet_type() {
        let (mut client, mut server) = create_tcp_pair().await;

        tokio::spawn(async move {
            let size = 2u32;
            let unknown_type = 999u16;
            let _ = client.write_all(&size.to_be_bytes()).await;
            let _ = client.write_all(&unknown_type.to_be_bytes()).await;
        });

        let result = receive_packet(&mut server).await;
        assert!(result.is_err());
        let err = result.unwrap_err();
        assert_eq!(err.kind(), io::ErrorKind::InvalidData);
        assert_eq!(err.to_string(), "Type de paquet inconnu.");
    }

    #[tokio::test]
    async fn test_receive_packet_truncated_header() {
        let (mut client, mut server) = create_tcp_pair().await;

        tokio::spawn(async move {
            let partial_header = [0x00, 0x00];
            let _ = client.write_all(&partial_header).await;
            drop(client);
        });

        let result = receive_packet(&mut server).await;
        assert!(result.is_err());
        let err = result.unwrap_err();
        assert_eq!(err.kind(), io::ErrorKind::UnexpectedEof);
    }

    #[tokio::test]
    async fn test_receive_packet_truncated_payload() {
        let (mut client, mut server) = create_tcp_pair().await;

        tokio::spawn(async move {
            let size = 10u32;
            let _ = client.write_all(&size.to_be_bytes()).await;
            let _ = client
                .write_all(&(PacketType::Ping as u16).to_be_bytes())
                .await;
            let _ = client.write_all(b"123").await;
            drop(client);
        });

        let result = receive_packet(&mut server).await;
        assert!(result.is_err());
        let err = result.unwrap_err();
        assert_eq!(err.kind(), io::ErrorKind::UnexpectedEof);
    }

    #[tokio::test]
    async fn test_send_packet_exceeds_max_size() {
        let (mut client, _server) = create_tcp_pair().await;

        let oversized_payload = vec![0u8; MAX_PACKET_SIZE - 1];
        let packet = Packet::new(PacketType::Log, oversized_payload);

        let result = send_packet(&mut client, &packet).await;
        assert!(result.is_err());
        let err = result.unwrap_err();
        assert_eq!(err.kind(), io::ErrorKind::InvalidData);
        assert_eq!(err.to_string(), "Paquet trop volumineux.");
    }

    #[tokio::test]
    async fn test_send_and_receive_roundtrip() {
        let (mut client, mut server) = create_tcp_pair().await;

        let test_payload = b"hello signal network".to_vec();
        let sent_packet = Packet::new(PacketType::Chat, test_payload.clone());

        let client_task = tokio::spawn(async move { send_packet(&mut client, &sent_packet).await });

        let server_task = tokio::spawn(async move { receive_packet(&mut server).await });

        let (client_res, server_res) = tokio::join!(client_task, server_task);
        assert!(client_res.unwrap().is_ok());

        let received = server_res.unwrap().expect("receive_packet should succeed");
        assert_eq!(received.packet_type, PacketType::Chat);
        assert_eq!(received.payload, test_payload);
    }

    #[test]
    fn test_packet_parse_body_too_short() {
        let err = Packet::parse_body(&[]).unwrap_err();
        assert_eq!(err.kind(), io::ErrorKind::InvalidData);
        assert_eq!(err.to_string(), "Paquet invalide.");

        let err = Packet::parse_body(&[0x00]).unwrap_err();
        assert_eq!(err.kind(), io::ErrorKind::InvalidData);
        assert_eq!(err.to_string(), "Paquet invalide.");
    }

    #[test]
    fn test_packet_parse_body_unknown_type() {
        let err = Packet::parse_body(&[0xFF, 0xFF]).unwrap_err();
        assert_eq!(err.kind(), io::ErrorKind::InvalidData);
        assert_eq!(err.to_string(), "Type de paquet inconnu.");
    }

    #[test]
    fn test_packet_parse_body_empty_payload() {
        let body = (PacketType::Ping as u16).to_be_bytes();
        let packet =
            Packet::parse_body(&body).expect("parse_body should succeed with empty payload");
        assert_eq!(packet.packet_type, PacketType::Ping);
        assert!(packet.payload.is_empty());
    }

    #[test]
    fn test_packet_parse_body_with_payload() {
        let mut body = (PacketType::Chat as u16).to_be_bytes().to_vec();
        body.extend_from_slice(b"test message");
        let packet = Packet::parse_body(&body).expect("parse_body should succeed with payload");
        assert_eq!(packet.packet_type, PacketType::Chat);
        assert_eq!(packet.payload, b"test message");
    }

    #[test]
    fn test_packet_new_empty_payload() {
        let packet = Packet::new(PacketType::Ping, Vec::new());
        assert_eq!(packet.packet_type, PacketType::Ping);
        assert!(
            packet.payload.is_empty(),
            "Payload should be empty when initialized with empty Vec"
        );
    }

    #[test]
    fn test_packet_new_non_empty_payload() {
        let payload = vec![0x01, 0x02, 0x03, 0x04];
        let packet = Packet::new(PacketType::Move, payload.clone());
        assert_eq!(packet.packet_type, PacketType::Move);
        assert_eq!(packet.payload, payload);
    }

    #[test]
    fn test_packet_clone() {
        let original = Packet::new(PacketType::Chat, b"hello".to_vec());
        let mut cloned = original.clone();
        cloned.payload.push(b'!');
        assert_eq!(
            original.payload, b"hello",
            "mutating the clone must not affect the original"
        );
        assert_eq!(cloned.payload, b"hello!");
    }

    #[test]
    fn test_parse_body_all_supported_packet_types_protocol_lock() {
        let expected_mappings = [
            (1u16, PacketType::Ping),
            (2u16, PacketType::Login),
            (3u16, PacketType::Chat),
            (4u16, PacketType::Move),
            (5u16, PacketType::Log),
            (6u16, PacketType::SignUp),
            (7u16, PacketType::LoginResponse),
            (8u16, PacketType::SignUpResponse),
            (9u16, PacketType::BAN),
            (10u16, PacketType::DECO),
            (11u16, PacketType::MarketBuy),
            (12u16, PacketType::MarketSell),
            (13u16, PacketType::MarketCancelBuy),
            (14u16, PacketType::MarketCancelSell),
            (15u16, PacketType::PlayerState),
            (16u16, PacketType::PlayerRemove),
            (17u16, PacketType::Session),
        ];

        for (wire_id, expected_type) in expected_mappings {
            let body = wire_id.to_be_bytes();
            let packet = Packet::parse_body(&body)
                .unwrap_or_else(|e| panic!("Failed to parse body for wire ID {wire_id}: {e}"));
            assert_eq!(
                packet.packet_type, expected_type,
                "Wire ID {wire_id} did not map to expected PacketType::{expected_type:?}"
            );
            assert!(
                packet.payload.is_empty(),
                "Expected empty payload when parsing header-only body for wire ID {wire_id}"
            );
        }
    }

    #[test]
    fn test_parse_body_unknown_type_boundary_cases() {
        let unknown_ids = [0u16, 18u16, 999u16, u16::MAX];
        for unknown_id in unknown_ids {
            let body = unknown_id.to_be_bytes();
            let err = Packet::parse_body(&body)
                .expect_err(&format!("Wire ID {unknown_id} should return an error"));
            assert_eq!(
                err.kind(),
                io::ErrorKind::InvalidData,
                "Unknown wire ID {unknown_id} should return InvalidData"
            );
        }
    }

    #[test]
    fn test_parse_body_realistic_move_payload() {
        let mut body = (PacketType::Move as u16).to_be_bytes().to_vec();
        body.extend_from_slice(&100i32.to_be_bytes());
        body.extend_from_slice(&(-250i32).to_be_bytes());
        body.extend_from_slice(&42i32.to_be_bytes());

        let packet =
            Packet::parse_body(&body).expect("12-byte Move packet body should parse successfully");
        assert_eq!(packet.packet_type, PacketType::Move);
        assert_eq!(packet.payload.len(), 12);

        let x = i32::from_be_bytes(packet.payload[0..4].try_into().unwrap());
        let y = i32::from_be_bytes(packet.payload[4..8].try_into().unwrap());
        let z = i32::from_be_bytes(packet.payload[8..12].try_into().unwrap());
        assert_eq!((x, y, z), (100, -250, 42));
    }

    #[test]
    fn test_parse_body_realistic_session_payload() {
        let mut body = (PacketType::Session as u16).to_be_bytes().to_vec();
        let test_uuid = [0xAB; 16];
        body.extend_from_slice(&test_uuid);

        let packet = Packet::parse_body(&body)
            .expect("16-byte Session packet body should parse successfully");
        assert_eq!(packet.packet_type, PacketType::Session);
        assert_eq!(packet.payload, test_uuid);
    }

    #[test]
    fn test_parse_body_realistic_player_state_payload() {
        let mut body = (PacketType::PlayerState as u16).to_be_bytes().to_vec();
        let test_uuid = [0x07; 16];
        body.extend_from_slice(&test_uuid);
        body.extend_from_slice(&15i32.to_be_bytes());
        body.extend_from_slice(&30i32.to_be_bytes());
        body.extend_from_slice(&0i32.to_be_bytes());

        let packet =
            Packet::parse_body(&body).expect("28-byte PlayerState body should parse successfully");
        assert_eq!(packet.packet_type, PacketType::PlayerState);
        assert_eq!(packet.payload.len(), 28);
        assert_eq!(&packet.payload[..16], &test_uuid);
    }

    #[tokio::test]
    async fn test_send_packet_wire_format_inspection() {
        let (mut client, mut server) = create_tcp_pair().await;
        let test_payload = b"DIRECT_WIRE_TEST".to_vec();
        let packet = Packet::new(PacketType::Ping, test_payload.clone());

        let send_task = tokio::spawn(async move { send_packet(&mut client, &packet).await });

        // 1. Read raw 4-byte length header: size must equal 2 (type) + payload.len()
        let mut len_buf = [0u8; 4];
        server
            .read_exact(&mut len_buf)
            .await
            .expect("failed to read 4-byte length prefix");
        let declared_size = u32::from_be_bytes(len_buf) as usize;
        assert_eq!(
            declared_size,
            2 + test_payload.len(),
            "Declared size prefix must equal 2 + payload len"
        );

        // 2. Read raw 2-byte packet type
        let mut type_buf = [0u8; 2];
        server
            .read_exact(&mut type_buf)
            .await
            .expect("failed to read 2-byte packet type");
        let wire_type = u16::from_be_bytes(type_buf);
        assert_eq!(
            wire_type,
            PacketType::Ping as u16,
            "Wire type prefix must equal PacketType::Ping"
        );

        // 3. Read raw payload
        let mut payload_buf = vec![0u8; test_payload.len()];
        server
            .read_exact(&mut payload_buf)
            .await
            .expect("failed to read payload");
        assert_eq!(payload_buf, test_payload);

        let send_result = send_task.await.expect("send task panicked");
        assert!(send_result.is_ok());
    }

    #[tokio::test]
    async fn test_send_and_receive_empty_payload_roundtrip() {
        let (mut client, mut server) = create_tcp_pair().await;
        let packet = Packet::new(PacketType::Ping, Vec::new());

        let client_task = tokio::spawn(async move { send_packet(&mut client, &packet).await });
        let server_task = tokio::spawn(async move { receive_packet(&mut server).await });

        let (client_res, server_res) = tokio::join!(client_task, server_task);
        assert!(client_res.unwrap().is_ok());

        let received = server_res
            .unwrap()
            .expect("receive_packet with empty payload should succeed");
        assert_eq!(received.packet_type, PacketType::Ping);
        assert!(received.payload.is_empty());
    }

    #[tokio::test]
    async fn test_send_and_receive_exact_max_allowed_boundary() {
        let (mut client, mut server) = create_tcp_pair().await;

        // MAX_PACKET_SIZE limits total body (2 bytes type + payload)
        // Therefore max allowed payload is MAX_PACKET_SIZE - 2
        let max_payload: Vec<u8> = (0..MAX_PACKET_SIZE - 2).map(|i| (i % 251) as u8).collect();
        let packet = Packet::new(PacketType::Log, max_payload.clone());

        // Spawn reader first to drain TCP socket concurrently and avoid kernel buffer write blocks
        let server_task = tokio::spawn(async move { receive_packet(&mut server).await });
        let client_task = tokio::spawn(async move { send_packet(&mut client, &packet).await });

        let (client_res, server_res) = tokio::join!(client_task, server_task);
        assert!(
            client_res.unwrap().is_ok(),
            "Sending exact MAX_PACKET_SIZE frame should succeed"
        );

        let received = server_res
            .unwrap()
            .expect("Receiving exact MAX_PACKET_SIZE frame should succeed");
        assert_eq!(received.packet_type, PacketType::Log);
        assert!(
            received.payload == max_payload,
            "10 MB payload must arrive byte-for-byte (got {} bytes, expected {})",
            received.payload.len(),
            max_payload.len()
        );
    }

    #[tokio::test]
    async fn test_receive_packet_oversized_header_rejected_without_waiting() {
        let (mut client, mut server) = create_tcp_pair().await;

        tokio::spawn(async move {
            let oversized_size = (MAX_PACKET_SIZE + 1) as u32;
            let _ = client.write_all(&oversized_size.to_be_bytes()).await;
            // Keep connection open without writing body bytes
            tokio::time::sleep(Duration::from_secs(10)).await;
        });

        // The server must reject the oversized header immediately upon reading size,
        // without waiting for the body or hanging until EOF.
        let result = timeout(Duration::from_secs(3), receive_packet(&mut server))
            .await
            .expect("receive_packet should not hang waiting for oversized body");

        assert!(result.is_err(), "Oversized header must return an error");
        let err = result.unwrap_err();
        assert_eq!(err.kind(), io::ErrorKind::InvalidData);
    }

    #[test]
    fn test_encode_ban_none_vs_empty_expiration() {
        let with_none = encode_ban(BanType::Permanent, "Exploit", None);
        let with_empty = encode_ban(BanType::Permanent, "Exploit", Some(""));
        assert_eq!(with_none, b"2\x00Exploit\x00");
        assert_eq!(
            with_none, with_empty,
            "None and Some(\"\") must produce identical output due to unwrap_or(\"\")"
        );
    }

    #[test]
    fn test_encode_ban_empty_reason() {
        let encoded = encode_ban(BanType::Temporary, "", None);
        assert_eq!(encoded, b"1\x00\x00");
    }

    #[test]
    fn test_encode_ban_multibyte_utf8() {
        let encoded = encode_ban(BanType::Permanent, "Raison: ⚠ triche", None);
        // Asserts literal byte sequence: ⚠ is encoded as [0xE2, 0x9A, 0xA0]
        assert_eq!(encoded, b"2\x00Raison: \xE2\x9A\xA0 triche\x00");
    }

    #[test]
    fn test_encode_ban_reason_with_nul_documents_delimiter_collision() {
        // Documents that embedded NUL in reason creates extra delimiters in the current protocol
        let encoded = encode_ban(BanType::Permanent, "Bad\x00Actor", None);
        assert_eq!(encoded, b"2\x00Bad\x00Actor\x00");
    }
}

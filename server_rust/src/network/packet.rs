use log::error;
use std::io;

use tokio::io::{
    AsyncReadExt,
    AsyncWriteExt,
};
use tokio::net::TcpStream;
use serde::{Deserialize, Serialize};


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
    pub fn new(
        packet_type: PacketType,
        payload: Vec<u8>,
    ) -> Self {
        Self {
            packet_type,
            payload,
        }
    }
}
pub fn encode_ban(
    ban_type: BanType,
    reason: &str,
    date_deban: Option<&str>,
) -> Vec<u8> {

    format!(
        "{}\0{}\0{}",
        ban_type as u8,
        reason,
        date_deban.unwrap_or("")
    )
    .into_bytes()
}

/// Envoie un paquet.
pub async fn send_packet(
    stream: &mut TcpStream,
    packet: &Packet,
) -> io::Result<()> {

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

    let packet_type =
        (packet.packet_type as u16).to_be_bytes();

    stream.write_all(&packet_type).await?;

    stream.write_all(&packet.payload).await?;

    Ok(())
}

/// Reçoit exactement `size` octets.
async fn recv_exact(
    stream: &mut TcpStream,
    size: usize,
) -> io::Result<Vec<u8>> {

    let mut buffer = vec![0u8; size];

    stream.read_exact(&mut buffer).await?;

    Ok(buffer)
}

/// Reçoit un paquet.
pub async fn receive_packet(
    stream: &mut TcpStream,
) -> io::Result<Packet> {

    // Taille
    let header = recv_exact(stream, 4).await?;

    let size = u32::from_be_bytes([
        header[0],
        header[1],
        header[2],
        header[3],
    ]) as usize;

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

    // Type
    let packet_type =
        u16::from_be_bytes([data[0], data[1]]);

    let packet_type =
        PacketType::from_u16(packet_type)
            .ok_or_else(|| {
                error!("Type de paquet inconnu");
                io::Error::new(
                    io::ErrorKind::InvalidData,
                    "Type de paquet inconnu.",
                )
            })?;

    // Payload
    let payload = data[2..].to_vec();

    Ok(Packet {
        packet_type,
        payload,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use tokio::io::AsyncWriteExt;
    use tokio::net::{TcpListener, TcpStream};

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
        let encoded = encode_ban(BanType::Temporary, "Cheating detected", Some("2026-12-31 23:59:59"));
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
            let _ = client.write_all(&(PacketType::Ping as u16).to_be_bytes()).await;
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

        let client_task = tokio::spawn(async move {
            send_packet(&mut client, &sent_packet).await
        });

        let server_task = tokio::spawn(async move {
            receive_packet(&mut server).await
        });

        let (client_res, server_res) = tokio::join!(client_task, server_task);
        assert!(client_res.unwrap().is_ok());

        let received = server_res.unwrap().expect("receive_packet should succeed");
        assert_eq!(received.packet_type, PacketType::Chat);
        assert_eq!(received.payload, test_payload);
    }
}


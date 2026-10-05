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

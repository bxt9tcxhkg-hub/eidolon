use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::net::SocketAddr;
use thiserror::Error;
use uuid::Uuid;

// --- Mesh-Fehler ---

#[derive(Debug, Error)]
pub enum MeshError {
    #[error("io error: {0}")]
    Io(#[from] std::io::Error),
    #[error("serialization error: {0}")]
    Serialization(#[from] serde_json::Error),
    #[error("crypto error: {0}")]
    Crypto(String),
    #[error("transport error: {0}")]
    Transport(String),
    #[error("discovery error: {0}")]
    Discovery(String),
    #[error("device not found: {0}")]
    DeviceNotFound(String),
    #[error("pairing required")]
    PairingRequired,
    #[error("protocol error: {0}")]
    Protocol(String),
    #[error("timeout")]
    Timeout,
}

pub type Result<T> = std::result::Result<T, MeshError>;

// --- IDs ---

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub struct DeviceId(pub String);

impl DeviceId {
    pub fn new() -> Self {
        Self(uuid::Uuid::new_v4().to_string())
    }
}

impl std::fmt::Display for DeviceId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub struct PacketId(pub String);

impl PacketId {
    pub fn new() -> Self {
        Self(uuid::Uuid::new_v4().to_string())
    }
}

// --- Gerätetyp ---

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum DeviceType {
    Host,
    Phone,
    Tablet,
    Watch,
    Speaker,
    Display,
    Sensor,
    Appliance,
    Custom(String),
}

impl std::fmt::Display for DeviceType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Host => write!(f, "host"),
            Self::Phone => write!(f, "phone"),
            Self::Tablet => write!(f, "tablet"),
            Self::Watch => write!(f, "watch"),
            Self::Speaker => write!(f, "speaker"),
            Self::Display => write!(f, "display"),
            Self::Sensor => write!(f, "sensor"),
            Self::Appliance => write!(f, "appliance"),
            Self::Custom(name) => write!(f, "custom:{name}"),
        }
    }
}

// --- Gerätefähigkeiten ---

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum DeviceCapability {
    Display,
    AudioIn,
    AudioOut,
    Camera,
    Haptic,
    Location,
    Sensors,
    Actuator,
    Compute,
    Custom(String),
}

// --- Verbindungstyp ---

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum ConnectionType {
    LocalLan {
        host: SocketAddr,
        latency_ms: u32,
    },
    Ble {
        device_address: [u8; 6],
        rssi: i8,
    },
    WebRtc {
        peer_id: String,
        connection_state: ConnectionState,
    },
    ThreadMesh {
        node_id: [u8; 16],
        hop_count: u8,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum ConnectionState {
    New,
    Connecting,
    Connected,
    Disconnected,
    Failed,
}

// --- Gerät ---

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Device {
    pub id: DeviceId,
    pub name: String,
    pub device_type: DeviceType,
    pub connection: ConnectionType,
    pub capabilities: Vec<DeviceCapability>,
    pub paired: bool,
    pub paired_at: Option<chrono::DateTime<chrono::Utc>>,
    pub last_seen: chrono::DateTime<chrono::Utc>,
    pub certificate_fingerprint: Option<String>,
}

impl Device {
    pub fn new(name: String, device_type: DeviceType) -> Self {
        Self {
            id: DeviceId::new(),
            name,
            device_type,
            connection: ConnectionType::LocalLan {
                host: "0.0.0.0:0".parse().unwrap(),
                latency_ms: 0,
            },
            capabilities: Vec::new(),
            paired: false,
            paired_at: None,
            last_seen: chrono::Utc::now(),
            certificate_fingerprint: None,
        }
    }
}

use crate::types::device::{DeviceCapability, DeviceId, DeviceType};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::net::SocketAddr;

// --- Pakettyp ---

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum PacketType {
    // Device Management
    DeviceHello,
    DeviceGoodbye,
    DeviceHeartbeat,
    DeviceCapability,

    // Task Execution
    TaskRequest,
    TaskResponse,
    TaskProgress,
    TaskCancel,

    // Real-time Communication
    ChatMessage,
    VoiceFrame,
    MediaFrame,

    // Discovery
    DeviceAnnounce,
    ServiceQuery,
    ServiceResponse,

    // Agent-to-Agent
    AgentHello,
    AgentCapability,
    AgentTaskRequest,
    AgentTaskResponse,
}

// --- Eidolon Packet ---

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EidolonPacket {
    pub version: u8,
    pub packet_type: PacketType,
    pub source: DeviceId,
    pub destination: DeviceId,
    pub payload: Vec<u8>,
    pub timestamp: i64,
}

impl EidolonPacket {
    pub fn new(packet_type: PacketType, source: DeviceId, destination: DeviceId) -> Self {
        Self {
            version: 1,
            packet_type,
            source,
            destination,
            payload: Vec::new(),
            timestamp: Utc::now().timestamp(),
        }
    }

    pub fn with_payload(mut self, payload: Vec<u8>) -> Self {
        self.payload = payload;
        self
    }
}

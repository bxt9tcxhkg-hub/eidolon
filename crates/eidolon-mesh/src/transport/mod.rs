use serde::{Deserialize, Serialize};

use crate::types::device::{MeshError, PacketId, Result};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TransportEnvelope {
    pub packet_id: PacketId,
    pub channel: String,
    pub payload: Vec<u8>,
}

impl TransportEnvelope {
    pub fn new(channel: impl Into<String>, payload: impl Into<Vec<u8>>) -> Self {
        Self {
            packet_id: PacketId::new(),
            channel: channel.into(),
            payload: payload.into(),
        }
    }
}

#[derive(Debug, Default)]
pub struct QuicTransport;

impl QuicTransport {
    pub fn encode(envelope: &TransportEnvelope) -> Result<Vec<u8>> {
        serde_json::to_vec(envelope).map_err(MeshError::from)
    }

    pub fn decode(bytes: &[u8]) -> Result<TransportEnvelope> {
        serde_json::from_slice(bytes).map_err(MeshError::from)
    }
}

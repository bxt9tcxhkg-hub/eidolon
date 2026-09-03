use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Message {
    pub id: String,
    pub from: String,
    pub to: String,
    pub message_type: MessageType,
    pub payload: serde_json::Value,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum MessageType {
    Chat,
    TaskRequest,
    TaskResponse,
    DeviceDiscovery,
    SkillRequest,
    SkillResponse,
}

#[derive(Debug, Clone)]
pub struct MessageError;

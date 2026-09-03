use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Episode {
    pub id: String,
    pub agent_id: String,
    pub task_id: Option<String>,
    pub content: serde_json::Value,
    pub timestamp: DateTime<Utc>,
    pub importance: f32,
}

impl Episode {
    pub fn new(agent_id: &str, content: serde_json::Value) -> Self {
        Self {
            id: uuid::Uuid::new_v4().to_string(),
            agent_id: agent_id.to_string(),
            task_id: None,
            content,
            timestamp: Utc::now(),
            importance: 0.5,
        }
    }
}

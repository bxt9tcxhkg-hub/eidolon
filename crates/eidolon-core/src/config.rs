use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentConfig {
    pub agent_name: String,
    pub model_endpoint: String,
    pub mesh_port: u16,
    pub persistence_dir: String,
    pub log_level: String,
}

impl Default for AgentConfig {
    fn default() -> Self {
        Self {
            agent_name: "eidolon".to_string(),
            model_endpoint: "http://localhost:11434".to_string(),
            mesh_port: 14434,
            persistence_dir: "data/persistence".to_string(),
            log_level: "info".to_string(),
        }
    }
}

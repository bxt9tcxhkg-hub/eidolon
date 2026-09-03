use std::path::PathBuf;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RuntimeConfig {
    pub http_port: u16,
    pub quic_port: u16,
    pub discovery_port: u16,
    pub data_dir: PathBuf,
    pub identity_key_path: Option<PathBuf>,
    pub max_peers: usize,
    pub discovery_interval_secs: u64,
    pub health_check_interval_secs: u64,
    pub enable_quic: bool,
    pub enable_discovery: bool,
}

impl Default for RuntimeConfig {
    fn default() -> Self {
        Self {
            http_port: 8002,
            quic_port: 4434,
            discovery_port: 8001,
            data_dir: PathBuf::from("data"),
            identity_key_path: None,
            max_peers: 20,
            discovery_interval_secs: 30,
            health_check_interval_secs: 30,
            enable_quic: true,
            enable_discovery: true,
        }
    }
}

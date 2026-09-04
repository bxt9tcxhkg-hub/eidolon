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

/// Ports reserved by the live Python FastAPI runtime. The Rust crates must
/// not bind these; they are quarantined, not a second product server.
pub const PYTHON_LIVE_HTTP_PORT: u16 = 8002;
pub const PYTHON_LIVE_QUIC_PORT: u16 = 4434;
pub const PYTHON_LIVE_DISCOVERY_PORT: u16 = 8001;
pub const PYTHON_LIVE_PORTS: [u16; 3] = [
    PYTHON_LIVE_HTTP_PORT,
    PYTHON_LIVE_QUIC_PORT,
    PYTHON_LIVE_DISCOVERY_PORT,
];

impl RuntimeConfig {
    pub fn uses_python_live_port(&self) -> bool {
        PYTHON_LIVE_PORTS.contains(&self.http_port)
            || PYTHON_LIVE_PORTS.contains(&self.quic_port)
            || PYTHON_LIVE_PORTS.contains(&self.discovery_port)
    }
}

impl Default for RuntimeConfig {
    fn default() -> Self {
        Self {
            http_port: 18002,
            quic_port: 14434,
            discovery_port: 18001,
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

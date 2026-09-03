use std::net::SocketAddr;
use std::sync::Arc;

use tracing::{info, warn, error};
use serde::{Deserialize, Serialize};
use crate::api::AppState;
use crate::transport::protocol::{PeerInfo, PeerStatus, MeshNode};
use tokio::net::UdpSocket;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DiscoveryMessage {
    pub msg_type: String,
    pub node_id: String,
    pub node_name: String,
    pub http_port: u16,
    pub quic_port: u16,
    pub public_key: String,
    pub timestamp: String,
}

pub async fn run_discovery(state: Arc<AppState>, discovery_port: u16) {
    let addr = SocketAddr::from(([0, 0, 0, 0], discovery_port));
    let socket = match UdpSocket::bind(addr).await {
        Ok(s) => s,
        Err(e) => {
            error!("Failed to bind discovery socket on {}: {}", discovery_port, e);
            return;
        }
    };
    
    info!("UDP discovery listening on port {}", discovery_port);
    
    let mut buf = vec![0u8; 2048];
    let mesh = MeshNode::new(state.keypair.clone(), state.config.max_peers);
    
    loop {
        match socket.recv_from(&mut buf).await {
            Ok((n, from)) => {
                let msg = match serde_json::from_slice::<DiscoveryMessage>(&buf[..n]) {
                    Ok(m) => m,
                    Err(_) => continue,
                };
                
                if msg.node_id == state.keypair.public_key_hex() {
                    continue; // Ignore own messages
                }
                
                let peer = PeerInfo {
                    id: msg.node_id.clone(),
                    name: msg.node_name,
                    address: from.ip().to_string(),
                    port: msg.quic_port,
                    public_key: msg.public_key,
                    last_seen: chrono::Utc::now().to_rfc3339(),
                    status: PeerStatus::Connected,
                };
                
                if let Err(e) = mesh.add_peer(peer).await {
                    warn!("Failed to add peer {}: {}", msg.node_id, e);
                }
            }
            Err(e) => {
                warn!("Discovery receive error: {}", e);
            }
        }
    }
}

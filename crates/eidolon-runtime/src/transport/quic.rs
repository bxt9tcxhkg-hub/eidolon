use std::net::SocketAddr;
use std::sync::Arc;
use std::time::Duration;

use quinn::{Endpoint, RecvStream, SendStream, ServerConfig, ConnectionError};
use rustls::{pki_types::{CertificateDer, PrivatePkcs8KeyDer}, RootCertStore};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use tokio::sync::RwLock;
use tracing::{error, info, warn, debug};

use crate::api::AppState;

/// Mesh message envelope for QUIC transport
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MeshEnvelope {
    pub version: String,
    pub msg_type: MeshMessageType,
    pub sender_id: String,
    pub target_id: Option<String>,
    pub payload: Value,
    pub timestamp: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum MeshMessageType {
    PairingRequest,
    PairingResponse,
    PeerDiscovery,
    ChatMessage,
    StateSync,
    Ping,
    Pong,
    Error,
}

/// QUIC Mesh Server for Eidolon P2P transport
pub struct QuicMeshServer {
    endpoint: Endpoint,
    state: Arc<AppState>,
    peers: Arc<RwLock<Vec<PeerConnection>>>,
}

#[derive(Debug, Clone)]
pub struct PeerConnection {
    pub peer_id: String,
    pub address: SocketAddr,
    pub connected_at: String,
}

impl QuicMeshServer {
    pub async fn new(state: Arc<AppState>, port: u16) -> Result<Self, anyhow::Error> {
        let addr = SocketAddr::from(([0, 0, 0, 0], port));

        // Generate self-signed cert for now (in production, use proper mTLS with certstore)
        let certified = rcgen::generate_simple_self_signed(vec![
            "localhost".into(),
            "eidolon-mesh".into(),
        ])?;
        let certs = vec![CertificateDer::from(certified.cert)];
        let key = PrivatePkcs8KeyDer::from(certified.key_pair.serialize_der());

        let mut server_config = ServerConfig::with_single_cert(certs, key.into())?;
        let mut transport_config = quinn::TransportConfig::default();
        transport_config.max_idle_timeout(Some(Duration::from_secs(60).try_into()?));
        transport_config.keep_alive_interval(Some(Duration::from_secs(30)));

        let server_transport = Arc::get_mut(&mut server_config.transport)
            .ok_or_else(|| anyhow::anyhow!("transport configuration unavailable"))?;
        *server_transport = transport_config;

        let endpoint = Endpoint::server(server_config, addr)?;
        info!("QUIC Mesh server listening on udp://{}", addr);

        Ok(Self {
            endpoint,
            state,
            peers: Arc::new(RwLock::new(Vec::new())),
        })
    }

    pub async fn run(self) -> Result<(), anyhow::Error> {
        let state = self.state.clone();
        let peers = self.peers.clone();

        while let Some(conn) = self.endpoint.accept().await {
            let state = state.clone();
            let peers = peers.clone();
            tokio::spawn(async move {
                if let Err(e) = handle_connection(conn, state, peers).await {
                    error!("QUIC connection error: {}", e);
                }
            });
        }
        Ok(())
    }

    /// Send a message to a specific peer
    pub async fn send_to_peer(&self, peer_addr: SocketAddr, envelope: &MeshEnvelope) -> Result<(), anyhow::Error> {
        let connect_addr = peer_addr;
        let connection = self.endpoint.connect(connect_addr, "eidolon-mesh")?
            .await
            .map_err(|e| anyhow::anyhow!("Connection failed: {}", e))?;

        let (mut send, mut recv) = connection.open_bi().await?;
        let data = serde_json::to_vec(envelope)?;
        send.write_all(&data).await?;
        send.finish()?;

        // Read response
        let mut buf = vec![0u8; 8192];
        if let Some(n) = recv.read(&mut buf).await? {
            buf.truncate(n);
            let response: MeshEnvelope = serde_json::from_slice(&buf)?;
            debug!("Received response: {:?}", response);
        }

        connection.close(0u32.into(), b"done");
        Ok(())
    }

    /// Broadcast to all connected peers
    pub async fn broadcast(&self, envelope: &MeshEnvelope) -> Result<(), anyhow::Error> {
        let peers = self.peers.read().await;
        for peer in peers.iter() {
            if let Err(e) = self.send_to_peer(peer.address, envelope).await {
                warn!("Failed to send to peer {}: {}", peer.peer_id, e);
            }
        }
        Ok(())
    }

    pub async fn peer_count(&self) -> usize {
        self.peers.read().await.len()
    }
}

async fn handle_connection(
    conn: quinn::Incoming,
    state: Arc<AppState>,
    peers: Arc<RwLock<Vec<PeerConnection>>>,
) -> Result<(), anyhow::Error> {
    let connection = conn.await?;
    let remote = connection.remote_address();
    info!("QUIC connection from {}", remote);

    // Register peer
    {
        let mut peers_guard = peers.write().await;
        peers_guard.push(PeerConnection {
            peer_id: format!("peer-{}", remote),
            address: remote,
            connected_at: chrono::Utc::now().to_rfc3339(),
        });
    }

    loop {
        let (send, recv) = match connection.accept_bi().await {
            Ok(stream) => stream,
            Err(ConnectionError::ApplicationClosed(_)) => {
                info!("Connection closed by application: {}", remote);
                break;
            }
            Err(e) => {
                warn!("Stream accept error: {}", e);
                break;
            }
        };

        let state = state.clone();
        let peers = peers.clone();
        tokio::spawn(async move {
            if let Err(e) = handle_stream(send, recv, state, peers).await {
                warn!("Stream error: {}", e);
            }
        });
    }

    // Unregister peer
    {
        let mut peers_guard = peers.write().await;
        peers_guard.retain(|p| p.address != remote);
    }

    Ok(())
}

async fn handle_stream(
    mut send: SendStream,
    mut recv: RecvStream,
    state: Arc<AppState>,
    _peers: Arc<RwLock<Vec<PeerConnection>>>,
) -> Result<(), anyhow::Error> {
    // Read message
    let mut buf = vec![0u8; 8192];
    let n = match recv.read(&mut buf).await {
        Ok(Some(n)) => n,
        Ok(None) => return Ok(()),
        Err(e) => return Err(e.into()),
    };
    buf.truncate(n);

    // Parse envelope
    let envelope: MeshEnvelope = match serde_json::from_slice(&buf) {
        Ok(env) => env,
        Err(e) => {
            let error_response = MeshEnvelope {
                version: "eidolon-mesh/v2".into(),
                msg_type: MeshMessageType::Error,
                sender_id: state.keypair.public_key_hex(),
                target_id: None,
                payload: serde_json::json!({"error": format!("Invalid message: {}", e)}),
                timestamp: chrono::Utc::now().to_rfc3339(),
            };
            let data = serde_json::to_vec(&error_response)?;
            send.write_all(&data).await?;
            send.finish()?;
            return Ok(());
        }
    };

    debug!("Received message: type={:?} from={}", envelope.msg_type, envelope.sender_id);

    // Process message based on type
    let response = match envelope.msg_type {
        MeshMessageType::Ping => MeshEnvelope {
            version: "eidolon-mesh/v2".into(),
            msg_type: MeshMessageType::Pong,
            sender_id: state.keypair.public_key_hex(),
            target_id: Some(envelope.sender_id),
            payload: serde_json::json!({"status": "alive", "uptime_s": (chrono::Utc::now() - state.start_time).num_seconds()}),
            timestamp: chrono::Utc::now().to_rfc3339(),
        },
        MeshMessageType::PeerDiscovery => MeshEnvelope {
            version: "eidolon-mesh/v2".into(),
            msg_type: MeshMessageType::PeerDiscovery,
            sender_id: state.keypair.public_key_hex(),
            target_id: Some(envelope.sender_id),
            payload: serde_json::json!({
                "node_id": state.keypair.public_key_hex(),
                "http_port": state.config.http_port,
                "quic_port": state.config.quic_port,
                "capabilities": ["chat", "pairing", "state_sync"]
            }),
            timestamp: chrono::Utc::now().to_rfc3339(),
        },
        MeshMessageType::PairingRequest => {
        // Handle pairing request — in production, forward to Python mesh_service
        MeshEnvelope {
            version: "eidolon-mesh/v2".into(),
            msg_type: MeshMessageType::PairingResponse,
            sender_id: state.keypair.public_key_hex(),
            target_id: Some(envelope.sender_id),
            payload: serde_json::json!({
                "accepted": true,
                "node_id": state.keypair.public_key_hex(),
                "message": "Pairing accepted via QUIC"
            }),
            timestamp: chrono::Utc::now().to_rfc3339(),
        }
        }
        MeshMessageType::ChatMessage => {
            // Echo chat for now (in production, route to chat engine)
            MeshEnvelope {
                version: "eidolon-mesh/v2".into(),
                msg_type: MeshMessageType::ChatMessage,
                sender_id: state.keypair.public_key_hex(),
                target_id: Some(envelope.sender_id),
                payload: serde_json::json!({
                    "echo": true,
                    "original": envelope.payload
                }),
                timestamp: chrono::Utc::now().to_rfc3339(),
            }
        }
        _ => MeshEnvelope {
            version: "eidolon-mesh/v2".into(),
            msg_type: MeshMessageType::Error,
            sender_id: state.keypair.public_key_hex(),
            target_id: Some(envelope.sender_id),
            payload: serde_json::json!({"error": "Unknown message type"}),
            timestamp: chrono::Utc::now().to_rfc3339(),
        },
    };

    let data = serde_json::to_vec(&response)?;
    send.write_all(&data).await?;
    send.finish()?;

    Ok(())
}

/// QUIC Mesh Client for outgoing connections
pub struct QuicMeshClient {
    endpoint: Endpoint,
}

impl QuicMeshClient {
    pub fn new() -> Result<Self, anyhow::Error> {
        let addr = SocketAddr::from(([0, 0, 0, 0], 0));
        let mut endpoint = Endpoint::client(addr).map_err(|e| anyhow::anyhow!("Endpoint bind failed: {}", e))?;
        let client_config = quinn::ClientConfig::try_with_platform_verifier()
            .map_err(|e| anyhow::anyhow!("Client config init failed: {}", e))?;
        endpoint.set_default_client_config(client_config);
        Ok(Self { endpoint })
    }

    pub fn new_with_trusted_certs(certs: Vec<CertificateDer<'static>>) -> Result<Self, anyhow::Error> {
        let addr = SocketAddr::from(([0, 0, 0, 0], 0));
        let mut endpoint = Endpoint::client(addr).map_err(|e| anyhow::anyhow!("Endpoint bind failed: {}", e))?;
        let mut roots = RootCertStore::empty();
        for cert in certs {
            roots.add(cert).map_err(|e| anyhow::anyhow!("Root certificate add failed: {}", e))?;
        }
        let client_config = quinn::ClientConfig::with_root_certificates(Arc::new(roots))
            .map_err(|e| anyhow::anyhow!("Client config init failed: {}", e))?;
        endpoint.set_default_client_config(client_config);
        Ok(Self { endpoint })
    }

    pub async fn send_message(
        &self,
        target: SocketAddr,
        envelope: &MeshEnvelope,
    ) -> Result<MeshEnvelope, anyhow::Error> {
        let connection = self.endpoint.connect(target, "eidolon-mesh")
            .map_err(|e| anyhow::anyhow!("Connect failed: {}", e))?
            .await
            .map_err(|e| anyhow::anyhow!("Connection failed: {}", e))?;

        let (mut send, mut recv) = connection.open_bi().await?;
        let data = serde_json::to_vec(envelope)?;
        send.write_all(&data).await.map_err(|e| anyhow::anyhow!("Write failed: {}", e))?;
        send.finish().map_err(|e| anyhow::anyhow!("Finish failed: {}", e))?;

        let mut buf = vec![0u8; 8192];
        let n = recv.read(&mut buf).await?
            .ok_or_else(|| anyhow::anyhow!("No response received"))?;
        buf.truncate(n);

        let response: MeshEnvelope = serde_json::from_slice(&buf)?;
        connection.close(0u32.into(), b"done");
        Ok(response)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn test_server_config() -> Result<(ServerConfig, CertificateDer<'static>), anyhow::Error> {
        let certified = rcgen::generate_simple_self_signed(vec!["localhost".into(), "eidolon-mesh".into()])?;
        let cert = CertificateDer::from(certified.cert);
        let key = PrivatePkcs8KeyDer::from(certified.key_pair.serialize_der());
        let server_config = ServerConfig::with_single_cert(vec![cert.clone()], key.into())?;
        Ok((server_config, cert))
    }

    #[tokio::test]
    async fn quic_mesh_client_can_exchange_mesh_envelope_with_trusted_self_signed_server() -> Result<(), anyhow::Error> {
        let (server_config, cert) = test_server_config()?;
        let server = Endpoint::server(server_config, SocketAddr::from(([127, 0, 0, 1], 0)))?;
        let server_addr = server.local_addr()?;
        let (shutdown_tx, shutdown_rx) = tokio::sync::oneshot::channel::<()>();

        let server_task = tokio::spawn(async move {
            let connecting = server.accept().await.expect("incoming connection");
            let connection = connecting.await.expect("connection handshake");
            let (mut send, mut recv) = connection.accept_bi().await.expect("stream accept");
            let mut buf = vec![0u8; 8192];
            let n = recv.read(&mut buf).await.expect("stream read").expect("payload bytes");
            let request: MeshEnvelope = serde_json::from_slice(&buf[..n]).expect("valid envelope");
            assert!(matches!(request.msg_type, MeshMessageType::Ping));
            let response = MeshEnvelope {
                version: "eidolon-mesh/v2".into(),
                msg_type: MeshMessageType::Pong,
                sender_id: "server-node".into(),
                target_id: Some(request.sender_id),
                payload: json!({"status": "alive"}),
                timestamp: chrono::Utc::now().to_rfc3339(),
            };
            let data = serde_json::to_vec(&response).expect("serialize response");
            send.write_all(&data).await.expect("stream write");
            send.finish().expect("finish send");
            let _ = shutdown_rx.await;
        });

        let client = QuicMeshClient::new_with_trusted_certs(vec![cert])?;
        let response = client.send_message(
            server_addr,
            &MeshEnvelope {
                version: "eidolon-mesh/v2".into(),
                msg_type: MeshMessageType::Ping,
                sender_id: "client-node".into(),
                target_id: None,
                payload: json!({"hello": "world"}),
                timestamp: chrono::Utc::now().to_rfc3339(),
            },
        ).await?;

        assert!(matches!(response.msg_type, MeshMessageType::Pong));
        assert_eq!(response.sender_id, "server-node");
        assert_eq!(response.payload["status"], "alive");
        let _ = shutdown_tx.send(());
        server_task.await?;
        Ok(())
    }
}

use std::collections::HashMap;
use std::sync::Arc;
use std::time::Duration;
use tokio::sync::RwLock;
use ed25519_dalek::Verifier;
use serde::{Deserialize, Serialize};
use crate::crypto::KeyPair;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PeerInfo {
    pub id: String,
    pub name: String,
    pub address: String,
    pub port: u16,
    pub public_key: String,
    pub last_seen: String,
    pub status: PeerStatus,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum PeerStatus {
    Connected,
    Disconnected,
    Stale,
}

pub struct MeshNode {
    keypair: Arc<KeyPair>,
    peers: Arc<RwLock<HashMap<String, PeerInfo>>>,
    max_peers: usize,
}

impl MeshNode {
    pub fn new(keypair: Arc<KeyPair>, max_peers: usize) -> Self {
        Self {
            keypair,
            peers: Arc::new(RwLock::new(HashMap::new())),
            max_peers,
        }
    }

    pub async fn add_peer(&self, peer: PeerInfo) -> Result<(), anyhow::Error> {
        let mut peers = self.peers.write().await;
        if peers.len() >= self.max_peers && !peers.contains_key(&peer.id) {
            anyhow::bail!("Max peers reached ({})", self.max_peers);
        }
        peers.insert(peer.id.clone(), peer);
        Ok(())
    }

    pub async fn remove_peer(&self, peer_id: &str) {
        let mut peers = self.peers.write().await;
        peers.remove(peer_id);
    }

    pub async fn get_peer(&self, peer_id: &str) -> Option<PeerInfo> {
        let peers = self.peers.read().await;
        peers.get(peer_id).cloned()
    }

    pub async fn list_peers(&self) -> Vec<PeerInfo> {
        let peers = self.peers.read().await;
        peers.values().cloned().collect()
    }

    pub async fn update_peer_status(&self, peer_id: &str, status: PeerStatus) {
        let mut peers = self.peers.write().await;
        if let Some(peer) = peers.get_mut(peer_id) {
            peer.status = status;
            peer.last_seen = chrono::Utc::now().to_rfc3339();
        }
    }

    pub async fn mark_stale_peers(&self, timeout: Duration) {
        let mut peers = self.peers.write().await;
        let now = chrono::Utc::now();
        for peer in peers.values_mut() {
            if let Ok(last_seen) = chrono::DateTime::parse_from_rfc3339(&peer.last_seen) {
                let elapsed = now.signed_duration_since(last_seen);
                if elapsed > chrono::Duration::from_std(timeout).unwrap_or(chrono::Duration::minutes(5)) {
                    peer.status = PeerStatus::Stale;
                }
            }
        }
    }

    pub fn public_key_hex(&self) -> String {
        self.keypair.public_key_hex()
    }

    pub fn sign_message(&self, message: &[u8]) -> Vec<u8> {
        self.keypair.sign(message).to_bytes().to_vec()
    }

    pub fn verify_message(&self, message: &[u8], signature: &[u8], public_key: &str) -> bool {
        let sig_bytes: [u8; 64] = match signature.try_into() {
            Ok(b) => b,
            Err(_) => return false,
        };
        let signature = ed25519_dalek::Signature::from_bytes(&sig_bytes);
        
        let pk_bytes = match hex::decode(public_key) {
            Ok(b) => b,
            Err(_) => return false,
        };
        let pk_array: [u8; 32] = match pk_bytes.try_into() {
            Ok(b) => b,
            Err(_) => return false,
        };
        let verifying_key = match ed25519_dalek::VerifyingKey::from_bytes(&pk_array) {
            Ok(k) => k,
            Err(_) => return false,
        };
        
        verifying_key.verify(message, &signature).is_ok()
    }
}

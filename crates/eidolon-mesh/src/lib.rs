use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Peer {
    pub id: String,
    pub name: String,
    pub address: String,
    pub port: u16,
    pub public_key_hex: String,
    pub last_seen: chrono::DateTime<chrono::Utc>,
}

pub struct DiscoveryService {
    pub peers: Arc<Mutex<HashMap<String, Peer>>>,
}

impl DiscoveryService {
    pub fn new() -> Self {
        Self {
            peers: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    pub fn add_peer(&self, peer: Peer) {
        let mut peers = self.peers.lock().unwrap();
        peers.insert(peer.id.clone(), peer);
    }

    pub fn discover(&self) -> Vec<Peer> {
        let peers = self.peers.lock().unwrap();
        peers.values().cloned().collect()
    }

    pub fn remove_peer(&self, id: &str) {
        let mut peers = self.peers.lock().unwrap();
        peers.remove(id);
    }
}

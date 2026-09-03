use chrono::Utc;

use crate::types::device::{ConnectionState, ConnectionType, Device, DeviceCapability, DeviceId, DeviceType};
use crate::types::registry::DeviceRegistry;

#[derive(Debug, Default)]
pub struct DeviceDiscovery {
    registry: DeviceRegistry,
}

impl DeviceDiscovery {
    pub fn new() -> Self {
        Self {
            registry: DeviceRegistry::new(),
        }
    }

    pub fn upsert_local_peer(&mut self, name: impl Into<String>, host: std::net::SocketAddr, latency_ms: u32) -> DeviceId {
        let name = name.into();
        if let Some(existing) = self.registry.list().into_iter().find(|device| device.name == name) {
            let id = existing.id.clone();
            if let Some(device) = self.registry.get_mut(&id) {
                device.connection = ConnectionType::WebRtc {
                    peer_id: host.to_string(),
                    connection_state: ConnectionState::Connected,
                };
                device.last_seen = Utc::now();
            }
            return id;
        }

        let mut device = Device::new(name, DeviceType::Host);
        device.connection = ConnectionType::LocalLan { host, latency_ms };
        device.capabilities = vec![DeviceCapability::Compute, DeviceCapability::Display];
        device.last_seen = Utc::now();
        self.registry.register(device)
    }

    pub fn known_devices(&self) -> Vec<Device> {
        self.registry.list().into_iter().cloned().collect()
    }

    pub fn paired_devices(&self) -> Vec<Device> {
        self.registry.list_paired().into_iter().cloned().collect()
    }
}

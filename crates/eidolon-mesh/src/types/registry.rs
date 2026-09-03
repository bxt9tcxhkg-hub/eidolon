use std::collections::HashMap;

use crate::types::device::{Device, DeviceId};

#[derive(Debug, Clone, Default)]
pub struct DeviceRegistry {
    devices: HashMap<DeviceId, Device>,
}

impl DeviceRegistry {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn register(&mut self, device: Device) -> DeviceId {
        let id = device.id.clone();
        self.devices.insert(id.clone(), device);
        id
    }

    pub fn get(&self, id: &DeviceId) -> Option<&Device> {
        self.devices.get(id)
    }

    pub fn get_mut(&mut self, id: &DeviceId) -> Option<&mut Device> {
        self.devices.get_mut(id)
    }

    pub fn list(&self) -> Vec<&Device> {
        self.devices.values().collect()
    }

    pub fn list_paired(&self) -> Vec<&Device> {
        self.devices.values().filter(|d| d.paired).collect()
    }

    pub fn remove(&mut self, id: &DeviceId) -> Option<Device> {
        self.devices.remove(id)
    }

    pub fn update_last_seen(&mut self, id: &DeviceId) {
        if let Some(device) = self.devices.get_mut(id) {
            device.last_seen = chrono::Utc::now();
        }
    }
}

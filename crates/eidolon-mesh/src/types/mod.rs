pub mod device;
pub mod registry;

pub use device::{ConnectionState, ConnectionType, Device, DeviceCapability, DeviceId, DeviceType, MeshError, PacketId, Result};
pub use registry::DeviceRegistry;

pub fn describe_device(device: &Device) -> String {
    format!(
        "{} [{}] paired={} capabilities={}",
        device.name,
        device.device_type,
        device.paired,
        device.capabilities.len()
    )
}

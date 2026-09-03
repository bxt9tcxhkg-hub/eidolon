pub mod quic;
pub mod discovery;
pub mod protocol;

pub const TRANSPORT_STACK: &[&str] = &["http", "udp-discovery", "quic"];

pub fn describe_transports() -> Vec<&'static str> {
    TRANSPORT_STACK.to_vec()
}

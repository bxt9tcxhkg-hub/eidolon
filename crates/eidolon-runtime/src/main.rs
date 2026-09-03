use eidolon_runtime::{Runtime, config::RuntimeConfig};
use std::path::PathBuf;

#[tokio::main]
async fn main() -> Result<(), anyhow::Error> {
    let config = RuntimeConfig {
        http_port: 8002,
        quic_port: 4434,
        discovery_port: 8001,
        data_dir: PathBuf::from("data"),
        identity_key_path: Some(PathBuf::from("data/identity.key")),
        max_peers: 20,
        discovery_interval_secs: 30,
        health_check_interval_secs: 30,
        enable_quic: true,
        enable_discovery: true,
    };

    let runtime = Runtime::new(config).await?;
    runtime.run().await?;

    Ok(())
}

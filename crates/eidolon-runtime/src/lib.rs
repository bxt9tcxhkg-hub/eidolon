pub mod api;
pub mod config;
pub mod crypto;
pub mod graph;
pub mod health;
pub mod models;
pub mod skills;
pub mod transport;

use std::net::SocketAddr;
use std::sync::Arc;
use tokio::sync::RwLock;
use tracing::info;

use crate::api::AppState;
use crate::config::RuntimeConfig;
use crate::crypto::KeyPair;
use crate::graph::KnowledgeGraph;
use crate::health::HealthMonitor;
use crate::skills::SkillRegistry;
use crate::transport::quic::QuicMeshServer;

pub struct Runtime {
    config: RuntimeConfig,
    state: Arc<AppState>,
}

impl Runtime {
    pub async fn new(config: RuntimeConfig) -> Result<Self, anyhow::Error> {
        tracing_subscriber::fmt()
            .with_env_filter("info,eidolon_runtime=debug")
            .init();

        info!("Starting Eidolon Runtime v{}", env!("CARGO_PKG_VERSION"));
        info!("HTTP port: {}, QUIC port: {}", config.http_port, config.quic_port);

        let keypair = if let Some(ref key_path) = config.identity_key_path {
            if key_path.exists() {
                KeyPair::load_from_file(key_path)?
            } else {
                let kp = KeyPair::generate();
                kp.save_to_file(key_path)?;
                kp
            }
        } else {
            KeyPair::generate()
        };

        info!("Node ID: {}", keypair.public_key_hex());

        let graph = KnowledgeGraph::new(&config.data_dir).await?;
        info!("Knowledge graph initialized");

        let skills = SkillRegistry::new();
        skills.load_builtin_skills();
        info!("Skills registry initialized");

        let health = HealthMonitor::new();

        let state = Arc::new(AppState {
            config: config.clone(),
            keypair: Arc::new(keypair),
            graph: Arc::new(RwLock::new(graph)),
            skills: Arc::new(RwLock::new(skills)),
            health: Arc::new(RwLock::new(health)),
            start_time: chrono::Utc::now(),
        });

        Ok(Self { config, state })
    }

    pub async fn run(self) -> Result<(), anyhow::Error> {
        let addr = SocketAddr::from(([0, 0, 0, 0], self.config.http_port));
        info!("Listening on http://{}", addr);

        let quic_state = self.state.clone();
        let quic_port = self.config.quic_port;
        tokio::spawn(async move {
            let run_state = quic_state.clone();
            match QuicMeshServer::new(quic_state, quic_port).await {
                Ok(server) => {
                    let _ = run_state;
                    if let Err(e) = server.run().await {
                        tracing::error!("QUIC server error: {}", e);
                    }
                }
                Err(e) => tracing::error!("Failed to start QUIC server: {}", e),
            }
        });

        let discovery_state = self.state.clone();
        let discovery_port = self.config.discovery_port;
        tokio::spawn(async move {
            crate::transport::discovery::run_discovery(discovery_state, discovery_port).await;
        });

        let app = api::create_router(self.state);
        let listener = tokio::net::TcpListener::bind(addr).await?;
        axum::serve(listener, app).await?;

        Ok(())
    }
}

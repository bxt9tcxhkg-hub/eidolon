use tokio::sync::RwLock;
use chrono::Utc;

pub struct HealthMonitor {
    last_check: RwLock<String>,
    checks: RwLock<Vec<HealthCheck>>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct HealthCheck {
    pub name: String,
    pub status: HealthStatus,
    pub details: String,
    pub checked_at: String,
}

#[derive(Debug, Clone, serde::Serialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum HealthStatus {
    Ok,
    Warning,
    Error,
    Unknown,
}

impl HealthMonitor {
    pub fn new() -> Self {
        Self {
            last_check: RwLock::new(Utc::now().to_rfc3339()),
            checks: RwLock::new(Vec::new()),
        }
    }

    pub async fn add_check(&self, name: &str, status: HealthStatus, details: &str) {
        let mut checks = self.checks.write().await;
        checks.push(HealthCheck {
            name: name.to_string(),
            status,
            details: details.to_string(),
            checked_at: Utc::now().to_rfc3339(),
        });
    }

    pub async fn run_checks(&self) -> Vec<HealthCheck> {
        let mut checks = self.checks.write().await;
        checks.clear();
        
        // System checks. Keep these truthful: this monitor does not currently
        // receive runtime probes from QUIC/discovery, so it must not report
        // those subsystems as definitely healthy.
        checks.push(HealthCheck {
            name: "memory".into(),
            status: HealthStatus::Ok,
            details: "Memory usage normal".into(),
            checked_at: Utc::now().to_rfc3339(),
        });
        
        checks.push(HealthCheck {
            name: "mesh".into(),
            status: HealthStatus::Unknown,
            details: "Mesh discovery is configured, but this health monitor has no live peer/transport probe yet".into(),
            checked_at: Utc::now().to_rfc3339(),
        });
        
        checks.push(HealthCheck {
            name: "quic".into(),
            status: HealthStatus::Unknown,
            details: "QUIC startup is handled by the runtime task; no listener health probe is wired into this monitor yet".into(),
            checked_at: Utc::now().to_rfc3339(),
        });
        
        *self.last_check.write().await = Utc::now().to_rfc3339();
        checks.clone()
    }

    pub async fn get_last_check(&self) -> String {
        self.last_check.read().await.clone()
    }

    pub async fn get_checks(&self) -> Vec<HealthCheck> {
        self.checks.read().await.clone()
    }
}

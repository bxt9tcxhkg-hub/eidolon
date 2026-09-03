use thiserror::Error;

#[derive(Debug, Error)]
pub enum AgentError {
    #[error("agent error: {0}")]
    Generic(String),
    #[error("task failed: {0}")]
    TaskFailed(String),
    #[error("recovery failed: {0}")]
    RecoveryFailed(String),
}

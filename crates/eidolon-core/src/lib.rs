//! Eidolon Core: Agent State Machine + Task Scheduler
//!
//! Stufen-Kaskade:
//! 0.9: Intent-Erkennung (Pattern-Matching)
//! 1.0: Task-Orchestrierung (Subtask-Planung)
//! 2.0: Multi-Agenten-Ökonomie (Credits, Reputation)
//! 3.0: Self-Healing (Architektur-Refaktorierung)

pub mod agent;
pub mod config;
pub mod error;
pub mod message;
pub mod task;

pub use agent::*;
pub use config::*;
pub use error::*;
pub use message::*;
pub use task::*;

use uuid::Uuid;

pub type AgentId = String;
pub type TaskId = String;

#[derive(Debug, Clone)]
pub struct AgentState {
    pub id: AgentId,
    pub name: String,
    pub status: AgentStatus,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, PartialEq)]
pub enum AgentStatus {
    Initializing,
    Running,
    Idle,
    Error(String),
    Recovering,
}

impl AgentState {
    pub fn new(name: &str) -> Self {
        Self {
            id: Uuid::new_v4().to_string(),
            name: name.to_string(),
            status: AgentStatus::Initializing,
            created_at: chrono::Utc::now(),
        }
    }
}

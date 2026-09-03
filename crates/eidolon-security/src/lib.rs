use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum TrustDecision {
    Allow,
    Challenge,
    Deny,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityEvent {
    pub id: String,
    pub subject: String,
    pub reason: String,
    pub decision: TrustDecision,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Default, Clone, Serialize, Deserialize)]
pub struct SecurityAuditLog {
    pub events: Vec<SecurityEvent>,
}

impl SecurityAuditLog {
    pub fn record(&mut self, subject: impl Into<String>, reason: impl Into<String>, decision: TrustDecision) {
        self.events.push(SecurityEvent {
            id: uuid::Uuid::new_v4().to_string(),
            subject: subject.into(),
            reason: reason.into(),
            decision,
            created_at: Utc::now(),
        });
    }

    pub fn latest_decision_for(&self, subject: &str) -> Option<&TrustDecision> {
        self.events.iter().rev().find(|event| event.subject == subject).map(|event| &event.decision)
    }
}

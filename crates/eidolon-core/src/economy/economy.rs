use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Wallet {
    pub agent_id: String,
    pub credits: f64,
    pub transactions: Vec<Transaction>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Transaction {
    pub id: String,
    pub amount: f64,
    pub balance_after: f64,
    pub reason: String,
    pub timestamp: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Budget {
    pub max_cost: f64,
    pub max_tokens: u32,
    pub max_duration_ms: u64,
}

impl Wallet {
    pub fn new(agent_id: &str, initial_credits: f64) -> Self {
        Self {
            agent_id: agent_id.to_string(),
            credits: initial_credits,
            transactions: Vec::new(),
        }
    }

    pub fn spend(&mut self, amount: f64, reason: &str) -> bool {
        if self.credits >= amount {
            self.credits -= amount;
            self.transactions.push(Transaction {
                id: uuid::Uuid::new_v4().to_string(),
                amount: -amount,
                balance_after: self.credits,
                reason: reason.to_string(),
                timestamp: Utc::now(),
            });
            true
        } else {
            false
        }
    }

    pub fn credit(&mut self, amount: f64, reason: &str) {
        self.credits += amount;
        self.transactions.push(Transaction {
            id: uuid::Uuid::new_v4().to_string(),
            amount,
            balance_after: self.credits,
            reason: reason.to_string(),
            timestamp: Utc::now(),
        });
    }

    pub fn can_afford(&self, cost: f64) -> bool {
        self.credits >= cost
    }
}

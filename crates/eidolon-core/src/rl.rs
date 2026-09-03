use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Reward {
    pub action: String,
    pub reward: f64,
    pub timestamp: chrono::DateTime<Utc>,
}

#[derive(Debug)]
pub struct AtroposRL {
    pub rewards: Vec<Reward>,
}

impl AtroposRL {
    pub fn new() -> Self {
        Self { rewards: Vec::new() }
    }

    pub fn record_reward(&mut self, action: &str, reward: f64) {
        self.rewards.push(Reward {
            action: action.to_string(),
            reward,
            timestamp: chrono::Utc::now(),
        });
    }

    pub fn total_reward(&self) -> f64 {
        self.rewards.iter().map(|r| r.reward).sum()
    }
}

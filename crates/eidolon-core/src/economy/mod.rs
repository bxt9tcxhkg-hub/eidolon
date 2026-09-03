pub mod economy;
pub mod reputation;

pub use economy::{Budget, Transaction, Wallet};
pub use reputation::{Reputation, ReputationEvent, ReputationRegistry};

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EconomicSnapshot {
    pub agent_id: String,
    pub credits: f64,
    pub trust_score: f64,
    pub trust_level: String,
    pub transaction_count: usize,
    pub interaction_count: usize,
}

impl EconomicSnapshot {
    pub fn from_state(wallet: &Wallet, reputation: &Reputation) -> Self {
        Self {
            agent_id: wallet.agent_id.clone(),
            credits: wallet.credits,
            trust_score: reputation.trust_score,
            trust_level: reputation.trust_level().to_string(),
            transaction_count: wallet.transactions.len(),
            interaction_count: reputation.interactions.len(),
        }
    }

    pub fn budget_headroom(&self, budget: &Budget) -> bool {
        self.credits >= budget.max_cost
    }
}

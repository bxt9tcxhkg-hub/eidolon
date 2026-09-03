use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Reputation {
    pub agent_id: String,
    pub trust_score: f64,
    pub interactions: Vec<ReputationEvent>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReputationEvent {
    pub id: String,
    pub source_agent: String,
    pub action: String,
    pub weight: f64,
    pub timestamp: DateTime<Utc>,
}

const TRUST_DECAY: f64 = 0.99;
const MAX_TRUST: f64 = 100.0;
const MIN_TRUST: f64 = 0.0;

impl Reputation {
    pub fn new(agent_id: &str) -> Self {
        Self {
            agent_id: agent_id.to_string(),
            trust_score: 50.0,
            interactions: Vec::new(),
        }
    }

    pub fn record_interaction(&mut self, source: &str, action: &str, weight: f64) {
        self.interactions.push(ReputationEvent {
            id: uuid::Uuid::new_v4().to_string(),
            source_agent: source.to_string(),
            action: action.to_string(),
            weight,
            timestamp: Utc::now(),
        });

        self.trust_score = (self.trust_score * TRUST_DECAY + weight).clamp(MIN_TRUST, MAX_TRUST);
    }

    pub fn trust_level(&self) -> &str {
        match self.trust_score {
            80.0..=MAX_TRUST => "trusted",
            50.0..=79.9 => "neutral",
            MIN_TRUST..=49.9 => "suspicious",
            _ => "unknown",
        }
    }
}

pub struct ReputationRegistry {
    agents: HashMap<String, Reputation>,
}

impl ReputationRegistry {
    pub fn new() -> Self {
        Self {
            agents: HashMap::new(),
        }
    }

    pub fn register(&mut self, agent_id: &str) {
        if !self.agents.contains_key(agent_id) {
            self.agents.insert(agent_id.to_string(), Reputation::new(agent_id));
        }
    }

    pub fn get(&self, agent_id: &str) -> Option<&Reputation> {
        self.agents.get(agent_id)
    }

    pub fn record(&mut self, agent_id: &str, source: &str, action: &str, weight: f64) {
        self.register(agent_id);
        if let Some(rep) = self.agents.get_mut(agent_id) {
            rep.record_interaction(source, action, weight);
        }
    }
}

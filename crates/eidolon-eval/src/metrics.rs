use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Metric {
    pub name: String,
    pub value: f64,
    pub unit: String,
    pub timestamp: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EvaluationRun {
    pub id: String,
    pub task_id: String,
    pub agent_id: String,
    pub metrics: Vec<Metric>,
    pub score: f64,
    pub raw_output: serde_json::Value,
    pub timestamp: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MetricType {
    Accuracy,
    Precision,
    Recall,
    F1,
    LatencyMs,
    TokenUsage,
    Cost,
    Custom(String),
}

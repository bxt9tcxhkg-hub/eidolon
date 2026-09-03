use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Metric {
    #[serde(default)]
    pub name: String,
    #[serde(default)]
    pub value: f64,
    #[serde(default)]
    pub unit: String,
    #[serde(default)]
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EvaluationRun {
    #[serde(default)]
    pub id: String,
    #[serde(default)]
    pub task_id: String,
    #[serde(default)]
    pub metrics: Vec<Metric>,
    #[serde(default)]
    pub success: bool,
    pub feedback: Option<String>,
}

pub struct EvaluationEngine {
    pub runs: Vec<EvaluationRun>,
}

impl EvaluationEngine {
    pub fn new() -> Self {
        Self { runs: Vec::new() }
    }

    pub fn record(&mut self, task_id: &str, success: bool, metrics: Vec<Metric>, feedback: Option<String>) {
        let run = EvaluationRun {
            id: uuid::Uuid::new_v4().to_string(),
            task_id: task_id.to_string(),
            metrics,
            success,
            feedback,
        };
        self.runs.push(run);
    }

    pub fn average_metric(&self, name: &str) -> f64 {
        let relevant: Vec<f64> = self
            .runs
            .iter()
            .flat_map(|r| r.metrics.iter())
            .filter(|m| m.name == name)
            .map(|m| m.value)
            .collect();

        if relevant.is_empty() {
            return 0.0;
        }

        relevant.iter().sum::<f64>() / relevant.len() as f64
    }
}

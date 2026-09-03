use crate::metrics::{EvaluationRun, Metric, MetricType};
use serde_json::Value;
use uuid::Uuid;

pub struct LLMJudge {
    pub judge_prompt: String,
}

impl LLMJudge {
    pub fn new(judge_prompt: &str) -> Self {
        Self {
            judge_prompt: judge_prompt.to_string(),
        }
    }

    pub fn evaluate(&self, task_description: &str, agent_output: &str, expected: Option<&str>) -> EvaluationRun {
        let mut score = 0.5;

        if let Some(expected) = expected {
            let similarity = strsim::jaro_winkler(agent_output, expected);
            score = similarity as f64;
        }

        let metrics = vec![
            Metric {
                name: MetricType::Accuracy.to_string(),
                value: score,
                unit: "ratio".to_string(),
                timestamp: chrono::Utc::now(),
            },
            Metric {
                name: MetricType::LatencyMs.to_string(),
                value: 0.0,
                unit: "ms".to_string(),
                timestamp: chrono::Utc::now(),
            },
        ];

        EvaluationRun {
            id: Uuid::new_v4().to_string(),
            task_id: Uuid::new_v4().to_string(),
            agent_id: "agent-host".to_string(),
            metrics,
            score,
            raw_output: Value::String(agent_output.to_string()),
            timestamp: chrono::Utc::now(),
        }
    }
}

impl MetricType {
    pub fn to_string(&self) -> String {
        match self {
            MetricType::Accuracy => "accuracy".to_string(),
            MetricType::Precision => "precision".to_string(),
            MetricType::Recall => "recall".to_string(),
            MetricType::F1 => "f1".to_string(),
            MetricType::LatencyMs => "latency_ms".to_string(),
            MetricType::TokenUsage => "token_usage".to_string(),
            MetricType::Cost => "cost".to_string(),
            MetricType::Custom(s) => s.clone(),
        }
    }
}

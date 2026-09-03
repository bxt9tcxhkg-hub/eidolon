use crate::metrics::EvaluationRun;
use crate::judge::LLMJudge;
use std::collections::HashMap;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum EngineError {
    #[error("evaluation failed: {0}")]
    Eval(String),
    #[error("no metrics recorded")]
    EmptyMetrics,
}

pub type Result<T> = std::result::Result<T, EngineError>;

pub struct EvaluationEngine {
    metrics: HashMap<String, EvaluationRun>,
    judge: LLMJudge,
}

impl EvaluationEngine {
    pub fn new(judge_prompt: &str) -> Self {
        Self {
            metrics: HashMap::new(),
            judge: LLMJudge::new(judge_prompt),
        }
    }

    pub fn evaluate_task(&mut self, task_desc: &str, output: &str, expected: Option<&str>) -> Result<EvaluationRun> {
        let run = self.judge.evaluate(task_desc, output, expected);
        self.metrics.insert(run.id.clone(), run.clone());
        Ok(run)
    }

    pub fn recent_metrics(&self, limit: usize) -> Vec<&EvaluationRun> {
        self.metrics.values().take(limit).collect()
    }

    pub fn average_score(&self) -> f64 {
        if self.metrics.is_empty() {
            return 0.0;
        }
        let sum: f64 = self.metrics.values().map(|m| m.score).sum();
        sum / self.metrics.len() as f64
    }
}

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TrainingRun {
    pub id: String,
    pub dataset: String,
    pub model: String,
    pub epochs: u32,
    pub status: String,
}

#[derive(Debug)]
pub struct FineTuningPipeline {
    pub job: Option<TrainingRun>,
}

impl FineTuningPipeline {
    pub fn new() -> Self {
        Self { job: None }
    }

    pub fn start_training(&mut self, dataset: &str, model: &str, epochs: u32) -> TrainingRun {
        let run = TrainingRun {
            id: uuid::Uuid::new_v4().to_string(),
            dataset: dataset.to_string(),
            model: model.to_string(),
            epochs,
            status: "started".to_string(),
        };
        self.job = Some(run.clone());
        run
    }
}

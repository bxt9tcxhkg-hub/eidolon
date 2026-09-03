use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Relationship {
    pub id: String,
    pub source_id: String,
    pub target_id: String,
    pub rel_type: String,
    pub weight: f32,
}

impl Relationship {
    pub fn new(source_id: &str, target_id: &str, rel_type: &str, weight: f32) -> Self {
        Self {
            id: uuid::Uuid::new_v4().to_string(),
            source_id: source_id.to_string(),
            target_id: target_id.to_string(),
            rel_type: rel_type.to_string(),
            weight,
        }
    }
}

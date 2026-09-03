use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SkillSpec {
    pub id: String,
    pub name: String,
    pub description: String,
    pub intent_patterns: Vec<String>,
    pub parameters: Vec<SkillParameter>,
    pub source: SkillSource,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SkillParameter {
    pub name: String,
    pub param_type: String,
    pub description: String,
    pub required: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "lowercase")]
pub enum SkillSource {
    Python { path: String },
    Rust { module: String },
    Bash { script: String },
}

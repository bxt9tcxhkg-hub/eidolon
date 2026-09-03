use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Skill {
    pub id: String,
    pub name: String,
    pub description: String,
    pub intent_patterns: Vec<String>,
    pub parameters: HashMap<String, serde_json::Value>,
    pub script_path: String,
}

pub struct SkillRegistry {
    pub skills: HashMap<String, Skill>,
}

impl SkillRegistry {
    pub fn new() -> Self {
        Self {
            skills: HashMap::new(),
        }
    }

    pub fn register(&mut self, skill: Skill) {
        self.skills.insert(skill.id.clone(), skill);
    }

    pub fn match_intent(&self, query: &str) -> Option<&Skill> {
        for skill in self.skills.values() {
            for pattern in &skill.intent_patterns {
                if query.to_lowercase().contains(&pattern.to_lowercase()) {
                    return Some(skill);
                }
            }
        }
        None
    }
}

pub fn extract_params(query: &str, skill: &Skill) -> HashMap<String, String> {
    let mut params = HashMap::new();
    for (key, _) in &skill.parameters {
        params.insert(key.clone(), query.to_string());
    }
    params
}

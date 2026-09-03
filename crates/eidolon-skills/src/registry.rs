use crate::parser::SkillSpec;
use std::collections::HashMap;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum RegistryError {
    #[error("skill not found: {0}")]
    NotFound(String),
    #[error("load error: {0}")]
    LoadError(String),
}

pub type Result<T> = std::result::Result<T, RegistryError>;

pub struct SkillRegistry {
    pub skills: HashMap<String, SkillSpec>,
}

impl SkillRegistry {
    pub fn new() -> Self {
        Self {
            skills: HashMap::new(),
        }
    }

    pub fn register(&mut self, spec: SkillSpec) {
        self.skills.insert(spec.id.clone(), spec);
    }

    pub fn get(&self, id: &str) -> Option<&SkillSpec> {
        self.skills.get(id)
    }

    pub fn list(&self) -> Vec<&SkillSpec> {
        self.skills.values().collect()
    }

    pub fn match_intent(&self, text: &str) -> Option<&SkillSpec> {
        for skill in self.skills.values() {
            for pattern in &skill.intent_patterns {
                if let Ok(re) = regex::Regex::new(pattern) {
                    if re.is_match(text) {
                        return Some(skill);
                    }
                }
            }
        }
        None
    }
}

impl Default for SkillRegistry {
    fn default() -> Self {
        Self::new()
    }
}

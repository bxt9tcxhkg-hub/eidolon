use crate::parser::SkillSpec;
use std::collections::HashMap;
use std::path::PathBuf;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum LoaderError {
    #[error("file not found: {0}")]
    FileNotFound(String),
    #[error("parse error: {0}")]
    ParseError(String),
    #[error("io error: {0}")]
    Io(#[from] std::io::Error),
}

pub type Result<T> = std::result::Result<T, LoaderError>;

pub struct SkillLoader {
    pub skills_dir: PathBuf,
    pub loaded: HashMap<String, SkillSpec>,
}

impl SkillLoader {
    pub fn new(skills_dir: PathBuf) -> Self {
        Self {
            skills_dir,
            loaded: HashMap::new(),
        }
    }

    pub fn load_all(&mut self) -> Result<Vec<SkillSpec>> {
        let mut specs = Vec::new();
        if !self.skills_dir.exists() {
            return Ok(specs);
        }
        for entry in std::fs::read_dir(&self.skills_dir)? {
            let entry = entry?;
            let path = entry.path();
            if path.extension().and_then(|e| e.to_str()) == Some("toml") {
                if let Ok(spec) = self.load_from_toml(&path) {
                    self.loaded.insert(spec.id.clone(), spec.clone());
                    specs.push(spec);
                }
            }
        }
        Ok(specs)
    }

    pub fn load_from_toml(&self, path: &PathBuf) -> Result<SkillSpec> {
        let content = std::fs::read_to_string(path)?;
        let spec: SkillSpec = toml::from_str(&content)
            .map_err(|e| LoaderError::ParseError(e.to_string()))?;
        Ok(spec)
    }
}

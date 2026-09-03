use crate::{Entity, Episode, Relationship};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum MemoryError {
    #[error("entity not found: {0}")]
    EntityNotFound(String),
    #[error("episode not found: {0}")]
    EpisodeNotFound(String),
    #[error("relationship not found: {0}")]
    RelationshipNotFound(String),
    #[error("storage error: {0}")]
    Storage(String),
}

pub type Result<T> = std::result::Result<T, MemoryError>;

pub struct MemoryStore {
    entities: std::collections::HashMap<String, Entity>,
    episodes: std::collections::HashMap<String, Episode>,
    relationships: std::collections::HashMap<String, Relationship>,
}

impl MemoryStore {
    pub fn new() -> Self {
        Self {
            entities: std::collections::HashMap::new(),
            episodes: std::collections::HashMap::new(),
            relationships: std::collections::HashMap::new(),
        }
    }

    pub fn save_entity(&mut self, entity: Entity) -> Result<()> {
        self.entities.insert(entity.id.clone(), entity);
        Ok(())
    }

    pub fn get_entity(&self, id: &str) -> Result<&Entity> {
        self.entities.get(id).ok_or_else(|| MemoryError::EntityNotFound(id.to_string()))
    }

    pub fn list_entities(&self) -> Vec<&Entity> {
        self.entities.values().collect()
    }

    pub fn save_episode(&mut self, episode: Episode) -> Result<()> {
        self.episodes.insert(episode.id.clone(), episode);
        Ok(())
    }

    pub fn get_episode(&self, id: &str) -> Result<&Episode> {
        self.episodes.get(id).ok_or_else(|| MemoryError::EpisodeNotFound(id.to_string()))
    }

    pub fn list_episodes(&self) -> Vec<&Episode> {
        self.episodes.values().collect()
    }

    pub fn save_relationship(&mut self, rel: Relationship) -> Result<()> {
        self.relationships.insert(rel.id.clone(), rel);
        Ok(())
    }

    pub fn find_relationships(&self, source_id: &str) -> Vec<&Relationship> {
        self.relationships.values().filter(|r| r.source_id == source_id).collect()
    }
}

impl Default for MemoryStore {
    fn default() -> Self {
        Self::new()
    }
}

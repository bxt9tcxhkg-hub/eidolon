use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Entity {
    pub id: String,
    pub entity_type: String,
    pub name: String,
    pub properties: HashMap<String, serde_json::Value>,
    pub embedding: Option<Vec<f32>>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Relationship {
    pub id: String,
    pub source_id: String,
    pub target_id: String,
    pub rel_type: String,
    pub strength: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Episode {
    pub id: String,
    pub agent_id: String,
    pub content: serde_json::Value,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

pub struct KnowledgeGraph {
    pub entities: HashMap<String, Entity>,
    pub relationships: Vec<Relationship>,
    pub episodes: Vec<Episode>,
}

impl KnowledgeGraph {
    pub fn new() -> Self {
        Self {
            entities: HashMap::new(),
            relationships: Vec::new(),
            episodes: Vec::new(),
        }
    }

    pub fn get_or_create_entity(&mut self, entity_type: &str, name: &str) -> &Entity {
        let id = format!("{}:{}", entity_type, name);
        self.entities.entry(id.clone()).or_insert_with(|| Entity {
            id,
            entity_type: entity_type.to_string(),
            name: name.to_string(),
            properties: HashMap::new(),
            embedding: None,
        })
    }

    pub fn relate(&mut self, source: &str, target: &str, rel_type: &str, strength: f32) {
        self.relationships.push(Relationship {
            id: format!("{}-{}-{}", source, rel_type, target),
            source_id: source.to_string(),
            target_id: target.to_string(),
            rel_type: rel_type.to_string(),
            strength,
        });
    }
}

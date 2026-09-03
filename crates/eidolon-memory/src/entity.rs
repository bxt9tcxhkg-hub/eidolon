use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Entity {
    pub id: String,
    pub entity_type: String,
    pub name: Option<String>,
    pub properties: HashMap<String, serde_json::Value>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EntityId(pub String);

impl EntityId {
    pub fn new() -> Self {
        Self(Uuid::new_v4().to_string())
    }
}

impl Default for EntityId {
    fn default() -> Self {
        Self::new()
    }
}

impl Entity {
    pub fn new(entity_type: &str) -> Self {
        let now = Utc::now();
        Self {
            id: EntityId::new().0,
            entity_type: entity_type.to_string(),
            name: None,
            properties: HashMap::new(),
            created_at: now,
            updated_at: now,
        }
    }

    pub fn with_name(mut self, name: &str) -> Self {
        self.name = Some(name.to_string());
        self
    }

    pub fn set_property(mut self, key: &str, value: serde_json::Value) -> Self {
        self.properties.insert(key.to_string(), value);
        self
    }
}

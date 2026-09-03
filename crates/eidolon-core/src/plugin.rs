use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Plugin {
    pub id: String,
    pub name: String,
    pub version: String,
    pub path: String,
}

pub struct PluginMarketplace {
    pub plugins: HashMap<String, Plugin>,
}

impl PluginMarketplace {
    pub fn new() -> Self {
        Self {
            plugins: HashMap::new(),
        }
    }

    pub fn register(&mut self, plugin: Plugin) {
        self.plugins.insert(plugin.id.clone(), plugin);
    }

    pub fn list(&self) -> Vec<&Plugin> {
        self.plugins.values().collect()
    }
}

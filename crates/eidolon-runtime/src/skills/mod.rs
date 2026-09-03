use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use tracing::info;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SkillDefinition {
    pub name: String,
    pub description: String,
    pub handler: String,
    pub params: Vec<String>,
    pub enabled: bool,
    pub priority: i32,
}

pub struct SkillRegistry {
    skills: Arc<RwLock<HashMap<String, SkillDefinition>>>,
}

impl SkillRegistry {
    pub fn new() -> Self {
        Self {
            skills: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    pub fn load_builtin_skills(&self) {
        let mut skills = self.skills.blocking_write();
        let builtins = vec![
            SkillDefinition {
                name: "chat".into(),
                description: "Allgemeiner Chat-Skill".into(),
                handler: "builtin".into(),
                params: vec!["text".into()],
                enabled: true,
                priority: 0,
            },
            SkillDefinition {
                name: "runtime_facts".into(),
                description: "Liefert Fakten über den LLM-Runtime".into(),
                handler: "builtin".into(),
                params: vec!["text".into()],
                enabled: true,
                priority: 0,
            },
            SkillDefinition {
                name: "system_info".into(),
                description: "System-Informationen".into(),
                handler: "builtin".into(),
                params: vec![],
                enabled: true,
                priority: 0,
            },
            SkillDefinition {
                name: "goal_manager".into(),
                description: "Verwalte autonome Ziele".into(),
                handler: "builtin".into(),
                params: vec!["action".into(), "goal".into()],
                enabled: true,
                priority: 0,
            },
            SkillDefinition {
                name: "device_status".into(),
                description: "Zeige verbundene Geräte".into(),
                handler: "builtin".into(),
                params: vec![],
                enabled: true,
                priority: 0,
            },
            SkillDefinition {
                name: "mesh_send".into(),
                description: "Nachricht an Peer senden".into(),
                handler: "builtin".into(),
                params: vec!["peer".into(), "message".into()],
                enabled: true,
                priority: 0,
            },
            SkillDefinition {
                name: "note".into(),
                description: "Notizen verwalten".into(),
                handler: "builtin".into(),
                params: vec!["action".into(), "content".into()],
                enabled: true,
                priority: 0,
            },
            SkillDefinition {
                name: "file_organizer".into(),
                description: "Dateien organisieren".into(),
                handler: "builtin".into(),
                params: vec!["path".into()],
                enabled: true,
                priority: 0,
            },
        ];
        for skill in builtins {
            skills.insert(skill.name.clone(), skill);
        }
        info!("Loaded {} builtin skills", skills.len());
    }

    pub async fn enable(&self, name: &str) -> Result<(), anyhow::Error> {
        let mut skills = self.skills.write().await;
        if let Some(skill) = skills.get_mut(name) {
            skill.enabled = true;
            Ok(())
        } else {
            anyhow::bail!("Skill not found: {}", name)
        }
    }

    pub async fn disable(&self, name: &str) -> Result<(), anyhow::Error> {
        let mut skills = self.skills.write().await;
        if let Some(skill) = skills.get_mut(name) {
            skill.enabled = false;
            Ok(())
        } else {
            anyhow::bail!("Skill not found: {}", name)
        }
    }

    pub async fn toggle(&self, name: &str) -> Result<bool, anyhow::Error> {
        let mut skills = self.skills.write().await;
        if let Some(skill) = skills.get_mut(name) {
            skill.enabled = !skill.enabled;
            Ok(skill.enabled)
        } else {
            anyhow::bail!("Skill not found: {}", name)
        }
    }

    pub async fn list_all(&self) -> Vec<SkillDefinition> {
        let skills = self.skills.read().await;
        skills.values().cloned().collect()
    }

    pub async fn list_enabled(&self) -> Vec<SkillDefinition> {
        let skills = self.skills.read().await;
        skills.values().filter(|s| s.enabled).cloned().collect()
    }

    pub async fn set_priority(&self, name: &str, priority: i32) -> Result<(), anyhow::Error> {
        let mut skills = self.skills.write().await;
        if let Some(skill) = skills.get_mut(name) {
            skill.priority = priority;
            Ok(())
        } else {
            anyhow::bail!("Skill not found: {}", name)
        }
    }
}

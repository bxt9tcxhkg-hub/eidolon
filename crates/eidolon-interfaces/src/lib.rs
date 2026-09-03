use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum InterfaceSurface {
    Web,
    Mobile,
    Desktop,
    Api,
    Terminal,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserIntentEnvelope {
    pub id: String,
    pub surface: InterfaceSurface,
    pub utterance: String,
    pub active_project: Option<String>,
    pub created_at: DateTime<Utc>,
}

impl UserIntentEnvelope {
    pub fn new(surface: InterfaceSurface, utterance: impl Into<String>, active_project: Option<String>) -> Self {
        Self {
            id: uuid::Uuid::new_v4().to_string(),
            surface,
            utterance: utterance.into(),
            active_project,
            created_at: Utc::now(),
        }
    }

    pub fn is_project_scoped(&self) -> bool {
        self.active_project.as_ref().is_some_and(|value| !value.trim().is_empty())
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InterfaceContract {
    pub surface: InterfaceSurface,
    pub supports_direct_manipulation: bool,
    pub supports_background_execution: bool,
    pub supports_interrupts: bool,
}

impl InterfaceContract {
    pub fn recommended_for(surface: InterfaceSurface) -> Self {
        let is_visual = matches!(surface, InterfaceSurface::Web | InterfaceSurface::Mobile | InterfaceSurface::Desktop);
        Self {
            surface,
            supports_direct_manipulation: is_visual,
            supports_background_execution: true,
            supports_interrupts: true,
        }
    }
}

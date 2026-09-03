use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UpdateInfo {
    pub version: String,
    pub download_url: String,
    pub changelog: Vec<String>,
}

#[derive(Debug, Clone)]
pub struct Updater {
    pub current_version: String,
    pub update_endpoint: String,
}

impl Updater {
    pub fn new(current_version: &str, update_endpoint: &str) -> Self {
        Self {
            current_version: current_version.to_string(),
            update_endpoint: update_endpoint.to_string(),
        }
    }

    pub fn check_for_update(&self) -> Option<UpdateInfo> {
        // In production: fetch from update_endpoint
        Some(UpdateInfo {
            version: "1.1.0".to_string(),
            download_url: "https://github.com/eidolon/releases".to_string(),
            changelog: vec!["Performance improvements".to_string()],
        })
    }
}

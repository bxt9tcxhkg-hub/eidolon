use serde::{Deserialize, Serialize};
use uuid::Uuid;
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Pattern {
    pub id: String,
    pub name: String,
    pub pattern: String,
    pub frequency: u32,
    pub last_seen: chrono::DateTime<Utc>,
}

pub struct SkillGenerator;

impl SkillGenerator {
    pub fn detect_patterns(interactions: &[String]) -> Vec<Pattern> {
        let mut counts: std::collections::HashMap<String, u32> = std::collections::HashMap::new();
        for interaction in interactions {
            *counts.entry(interaction.clone()).or_insert(0) += 1;
        }

        counts
            .into_iter()
            .filter(|(_, count)| *count >= 3)
            .map(|(pattern, frequency)| Pattern {
                id: Uuid::new_v4().to_string(),
                name: format!("auto-skill-{}", pattern.chars().take(20).collect::<String>()),
                pattern,
                frequency,
                last_seen: chrono::Utc::now(),
            })
            .collect()
    }

    pub fn generate_skill_template(pattern: &Pattern) -> String {
        format!(
            r#"pub struct AutoSkill {{}}

impl AutoSkill {{
    pub fn run(&self, params: &str) -> String {{
        format!("AutoSkill '{}' executed with: {{}}", "{name}", params)
    }}
}}
"#,
            name = pattern.name
        )
    }
}

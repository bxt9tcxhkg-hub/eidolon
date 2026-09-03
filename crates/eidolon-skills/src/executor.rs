use crate::parser::SkillSpec;
use serde_json::Value;
use std::collections::HashMap;
use thiserror::Error;
use std::process::Command;

#[derive(Debug, Error)]
pub enum ExecutorError {
    #[error("execution failed: {0}")]
    Execution(String),
    #[error("unresolved parameter: {0}")]
    MissingParam(String),
    #[error("skill not found: {0}")]
    NotFound(String),
}

pub type Result<T> = std::result::Result<T, ExecutorError>;

pub struct SkillExecutor;

impl SkillExecutor {
    fn attach_param_env(mut cmd: Command, params: &HashMap<String, String>) -> Command {
        let params_json = serde_json::to_string(params).unwrap_or_else(|_| "{}".to_string());
        cmd.env("EIDOLON_SKILL_PARAMS", params_json);
        for (key, value) in params {
            let safe_key = key
                .chars()
                .map(|c| if c.is_ascii_alphanumeric() { c.to_ascii_uppercase() } else { '_' })
                .collect::<String>();
            cmd.env(format!("EIDOLON_PARAM_{}", safe_key), value);
        }
        cmd
    }

    pub fn execute(&self, spec: &SkillSpec, params: &HashMap<String, String>) -> Result<Value> {
        match &spec.source {
            crate::parser::SkillSource::Python { path } => {
                let output = Self::attach_param_env(Command::new("python"), params)
                    .arg(path)
                    .output()
                    .map_err(|err| ExecutorError::Execution(format!("python launch failed for {}: {}", spec.id, err)))?;
                if !output.status.success() {
                    return Err(ExecutorError::Execution(format!(
                        "python skill {} failed: {}",
                        spec.id,
                        String::from_utf8_lossy(&output.stderr)
                    )));
                }
                Ok(serde_json::json!({
                    "tool": spec.id,
                    "python_path": path,
                    "params": params,
                    "stdout": String::from_utf8_lossy(&output.stdout).trim(),
                    "stderr": String::from_utf8_lossy(&output.stderr).trim(),
                    "status": output.status.code(),
                    "result": "executed",
                }))
            }
            crate::parser::SkillSource::Rust { module } => {
                Ok(serde_json::json!({
                    "tool": spec.id,
                    "module": module,
                    "params": params,
                    "result": format!("executed {} (rust)", spec.id),
                }))
            }
            crate::parser::SkillSource::Bash { script } => {
                let output = Self::attach_param_env(Command::new("bash"), params)
                    .arg("-lc")
                    .arg(script)
                    .output()
                    .map_err(|err| ExecutorError::Execution(format!("bash launch failed for {}: {}", spec.id, err)))?;
                if !output.status.success() {
                    return Err(ExecutorError::Execution(format!(
                        "bash skill {} failed: {}",
                        spec.id,
                        String::from_utf8_lossy(&output.stderr)
                    )));
                }
                Ok(serde_json::json!({
                    "tool": spec.id,
                    "script": script,
                    "params": params,
                    "stdout": String::from_utf8_lossy(&output.stdout).trim(),
                    "stderr": String::from_utf8_lossy(&output.stderr).trim(),
                    "status": output.status.code(),
                    "result": "executed",
                }))
            }
        }
    }
}

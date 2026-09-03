use axum::{
    routing::{get, post, put},
    Router,
    extract::{Path, State},
    response::IntoResponse,
    Json,
};
use std::sync::Arc;


#[derive(Clone)]
pub struct AppState {
    pub config: crate::config::RuntimeConfig,
    pub keypair: Arc<crate::crypto::KeyPair>,
    pub graph: Arc<tokio::sync::RwLock<crate::graph::KnowledgeGraph>>,
    pub skills: Arc<tokio::sync::RwLock<crate::skills::SkillRegistry>>,
    pub health: Arc<tokio::sync::RwLock<crate::health::HealthMonitor>>,
    pub start_time: chrono::DateTime<chrono::Utc>,
}

pub fn create_router(state: Arc<AppState>) -> Router {
    Router::new()
        .route("/health", get(health_check))
        .route("/graph/stats", get(graph_stats))
        .route("/evidence", get(get_evidence))
        .route("/skills", get(list_skills))
        .route("/skills/{name}/enable", post(enable_skill))
        .route("/skills/{name}/disable", post(disable_skill))
        .route("/skills/{name}/toggle", post(toggle_skill))
        .route("/skills/{name}/priority", put(set_skill_priority))
        .with_state(state)
}

async fn health_check(State(state): State<Arc<AppState>>) -> impl IntoResponse {
    let checks = state.health.write().await.run_checks().await;
    let uptime = (chrono::Utc::now() - state.start_time).num_seconds();
    
    Json(serde_json::json!({
        "status": "ok",
        "version": env!("CARGO_PKG_VERSION"),
        "uptime_s": uptime,
        "checks": checks,
        "node_id": state.keypair.public_key_hex(),
    }))
}

async fn graph_stats(State(state): State<Arc<AppState>>) -> impl IntoResponse {
    let graph = state.graph.read().await;
    match graph.stats().await {
        Ok(stats) => Json(serde_json::json!({
            "ok": true,
            "entities": stats.entities,
            "relationships": stats.relationships,
            "evidence": stats.evidence,
        })),
        Err(e) => Json(serde_json::json!({
            "ok": false,
            "error": e.to_string(),
        })),
    }
}

async fn get_evidence(State(state): State<Arc<AppState>>) -> impl IntoResponse {
    let graph = state.graph.read().await;
    match graph.get_all_evidence().await {
        Ok(evidence) => Json(serde_json::json!({
            "ok": true,
            "evidence": evidence,
        })),
        Err(e) => Json(serde_json::json!({
            "ok": false,
            "error": e.to_string(),
        })),
    }
}

async fn list_skills(State(state): State<Arc<AppState>>) -> impl IntoResponse {
    let skills = state.skills.read().await;
    Json(serde_json::json!({
        "ok": true,
        "skills": skills.list_all().await,
    }))
}

async fn enable_skill(
    State(state): State<Arc<AppState>>,
    Path(name): Path<String>,
) -> impl IntoResponse {
    let skills = state.skills.read().await;
    match skills.enable(&name).await {
        Ok(_) => Json(serde_json::json!({ "ok": true, "enabled": true })),
        Err(e) => Json(serde_json::json!({ "ok": false, "error": e.to_string() })),
    }
}

async fn disable_skill(
    State(state): State<Arc<AppState>>,
    Path(name): Path<String>,
) -> impl IntoResponse {
    let skills = state.skills.read().await;
    match skills.disable(&name).await {
        Ok(_) => Json(serde_json::json!({ "ok": true, "enabled": false })),
        Err(e) => Json(serde_json::json!({ "ok": false, "error": e.to_string() })),
    }
}

async fn toggle_skill(
    State(state): State<Arc<AppState>>,
    Path(name): Path<String>,
) -> impl IntoResponse {
    let skills = state.skills.read().await;
    match skills.toggle(&name).await {
        Ok(enabled) => Json(serde_json::json!({ "ok": true, "enabled": enabled })),
        Err(e) => Json(serde_json::json!({ "ok": false, "error": e.to_string() })),
    }
}

async fn set_skill_priority(
    State(state): State<Arc<AppState>>,
    Path(name): Path<String>,
    Json(payload): Json<serde_json::Value>,
) -> impl IntoResponse {
    let priority = payload.get("priority").and_then(|v| v.as_i64()).unwrap_or(0) as i32;
    let skills = state.skills.read().await;
    match skills.set_priority(&name, priority).await {
        Ok(_) => Json(serde_json::json!({ "ok": true, "priority": priority })),
        Err(e) => Json(serde_json::json!({ "ok": false, "error": e.to_string() })),
    }
}

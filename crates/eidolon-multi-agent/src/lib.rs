use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentAssignment {
    pub assignment_id: String,
    pub agent_id: String,
    pub scope: String,
    pub created_at: DateTime<Utc>,
}

impl AgentAssignment {
    pub fn new(agent_id: impl Into<String>, scope: impl Into<String>) -> Self {
        Self {
            assignment_id: uuid::Uuid::new_v4().to_string(),
            agent_id: agent_id.into(),
            scope: scope.into(),
            created_at: Utc::now(),
        }
    }
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct AssignmentPlan {
    pub assignments: Vec<AgentAssignment>,
}

impl AssignmentPlan {
    pub fn add(&mut self, assignment: AgentAssignment) {
        self.assignments.push(assignment);
    }

    pub fn is_empty(&self) -> bool {
        self.assignments.is_empty()
    }
}

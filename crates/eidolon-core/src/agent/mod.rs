use crate::{AgentState, AgentStatus, TaskId};

pub struct Agent {
    pub state: AgentState,
}

impl Agent {
    pub fn new(name: &str) -> Self {
        Self {
            state: AgentState::new(name),
        }
    }

    pub fn start(&mut self) -> Result<(), crate::error::AgentError> {
        self.state.status = AgentStatus::Running;
        Ok(())
    }

    pub fn schedule(&self, _task: TaskId) -> Result<(), crate::error::AgentError> {
        Ok(())
    }
}

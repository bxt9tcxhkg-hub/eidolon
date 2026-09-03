use crate::task::{Priority, Task, TaskStatus};
use std::collections::{BinaryHeap, HashMap};
use std::cmp::Ordering;

pub struct ScheduledTask {
    pub task_id: String,
    pub priority: Priority,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

impl Ord for ScheduledTask {
    fn cmp(&self, other: &Self) -> Ordering {
        self.priority
            .cmp(&other.priority)
            .then(self.created_at.cmp(&other.created_at))
            .then(self.task_id.cmp(&other.task_id))
    }
}

impl PartialOrd for ScheduledTask {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl PartialEq for ScheduledTask {
    fn eq(&self, other: &Self) -> bool {
        self.task_id == other.task_id
    }
}

impl Eq for ScheduledTask {}

pub struct TaskScheduler {
    pub tasks: HashMap<String, Task>,
    pub queue: BinaryHeap<ScheduledTask>,
}

impl TaskScheduler {
    pub fn new() -> Self {
        Self {
            tasks: HashMap::new(),
            queue: BinaryHeap::new(),
        }
    }

    pub fn schedule(&mut self, task: Task) -> Result<(), String> {
        let id = task.id.clone();
        self.queue.push(ScheduledTask {
            task_id: task.id.clone(),
            priority: task.priority.clone(),
            created_at: task.created_at,
        });
        self.tasks.insert(id, task);
        Ok(())
    }

    pub fn next(&mut self) -> Option<Task> {
        if let Some(scheduled) = self.queue.pop() {
            if let Some(task) = self.tasks.get_mut(&scheduled.task_id) {
                task.status = TaskStatus::Running;
                return Some(task.clone());
            }
        }
        None
    }

    pub fn complete_task(&mut self, id: &str, success: bool, result: String) -> Result<(), String> {
        if let Some(task) = self.tasks.get_mut(id) {
            task.status = if success {
                TaskStatus::Completed(result)
            } else {
                TaskStatus::Failed("task failed".to_string())
            };
        }
        Ok(())
    }

    pub fn status(&self, id: &str) -> Option<&Task> {
        self.tasks.get(id)
    }
}

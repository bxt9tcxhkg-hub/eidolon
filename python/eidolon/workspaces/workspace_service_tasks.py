from __future__ import annotations


def create_task(engine, **kwargs): return engine.create_task(**kwargs)
def get_task(engine, task_id: str): return engine.get_task(task_id)
def update_task(engine, task_id: str, **kwargs): return engine.update_task(task_id, **kwargs)
def delete_task(engine, task_id: str): return engine.delete_task(task_id)
def list_tasks(engine, domain: str | None = None, status: str | None = None): return engine.list_tasks(domain=domain, status=status)
def transition_task(engine, task_id: str, new_status: str): return engine.transition_task(task_id, new_status)
def set_blocker(engine, task_id: str, reason: str): return engine.set_blocker(task_id, reason)
def resolve_blocker(engine, task_id: str): return engine.resolve_blocker(task_id)
def add_dependency(engine, task_id: str, depends_on_id: str): return engine.add_dependency(task_id, depends_on_id)
def remove_dependency(engine, task_id: str, depends_on_id: str): return engine.remove_dependency(task_id, depends_on_id)
def get_dependency_status(engine, task_id: str): return engine.get_dependency_status(task_id)
def next_best_action(engine, domain: str = 'project'): return engine.next_best_action(domain)
def get_stats(engine, domain: str = 'project'): return engine.get_stats(domain)

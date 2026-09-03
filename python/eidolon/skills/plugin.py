from __future__ import annotations
from pathlib import Path
import logging

from agent_server import app
from eidolon.skills.registry import SkillRegistry
from eidolon.skills.builtin import ensure_builtin_skills

logger = logging.getLogger("eidolon.skills")


skills_dir = Path(__file__).resolve().parent.parent.parent / "skills"
registry = SkillRegistry(skills_dir)


@app.on_event("startup")
async def _skills_startup() -> None:
    ensure_builtin_skills()
    registry.load()
    logger.info("Loaded %s skills", len(registry.skills))

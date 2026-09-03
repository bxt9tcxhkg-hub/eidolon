from __future__ import annotations
import importlib.util
import inspect
from pathlib import Path
from typing import Any

from eidolon.skills.registry import Skill


class SkillRuntime:
    def __init__(self, skills_dir: Path) -> None:
        self.skills_dir = skills_dir

    def load_dynamic(self) -> list[Skill]:
        loaded: list[Skill] = []
        skip = {"__init__.py", "registry.py", "runtime.py", "builtin.py", "plugin.py"}
        for path in self.skills_dir.glob("*.py"):
            if path.name in skip or path.name.startswith("_"):
                continue
            try:
                spec = importlib.util.spec_from_file_location(path.stem, path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
            except Exception as exc:
                print(f"SKILL_LOAD_FAIL {path.name}: {type(exc).__name__}: {exc}", flush=True)
                continue

            # Variante 1: SKILL-Variable als Metadaten-Dict
            skill_data = getattr(mod, "SKILL", None)
            if isinstance(skill_data, dict):
                skill = Skill(
                    id=str(skill_data.get("id") or path.stem),
                    name=str(skill_data.get("name") or path.stem),
                    description=str(skill_data.get("description") or ""),
                    tags=[str(t) for t in (skill_data.get("tags") or [])],
                    keywords=[str(k) for k in (skill_data.get("keywords") or [])],
                    handler=str(skill_data.get("handler") or "run"),
                    params={k: v for k, v in (skill_data.get("params") or {}).items()},
                )
                loaded.append(skill)
                continue

            # Variante 2: Auto-Discovery — Modul mit run()-Funktion
            if hasattr(mod, "run") and callable(mod.run):
                # Extrahiere Keywords aus Docstring + Funktionsname
                doc = getattr(mod, "__doc__", "") or ""
                name = path.stem.replace("-", " ").title()
                # Keywords aus Dateiname ableiten
                keywords = [path.stem.replace("-", " "), path.stem]
                # Keywords aus Docstring extrahieren
                if doc:
                    doc_lower = doc.lower()
                    for kw in ["system", "info", "gerät", "geräte", "datei", "file", "notiz", "note",
                               "mesh", "send", "goal", "ziel", "calendar", "kalender", "image",
                               "bild", "skill", "generator", "organizer", "organisier"]:
                        if kw in doc_lower:
                            keywords.append(kw)

                skill = Skill(
                    id=path.stem,
                    name=name,
                    description=doc.strip().split("\n")[0] if doc else "",
                    keywords=list(dict.fromkeys(keywords)),
                    handler="run",
                )
                loaded.append(skill)

        return loaded

    def execute(self, skill_id: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        params = params or {}
        module_path = self.skills_dir / f"{skill_id}.py"
        if not module_path.exists():
            return {"ok": False, "error": f"Skill module not found: {skill_id}"}
        try:
            spec = importlib.util.spec_from_file_location(skill_id, module_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as exc:
            return {"ok": False, "error": f"Load failed: {exc}"}
        handler_name = params.pop("handler", None)
        if not handler_name:
            handler_name = getattr(mod, "DEFAULT_HANDLER", None)
        if not handler_name:
            return {"ok": False, "error": "No handler specified"}
        handler = getattr(mod, handler_name, None)
        if not callable(handler):
            return {"ok": False, "error": f"Handler not callable: {handler_name}"}
        try:
            result = handler(params)
            if inspect.iscoroutine(result):
                import asyncio
                result = asyncio.run(result)
            return {"ok": True, "result": result}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

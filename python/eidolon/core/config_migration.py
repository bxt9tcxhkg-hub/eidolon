from __future__ import annotations

import shutil
from pathlib import Path


def copy_tree_once(src: Path, dst: Path) -> None:
    if not src.exists() or dst.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)


def copy_file_once(src: Path, dst: Path) -> None:
    if not src.exists() or dst.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def migrate_legacy_state(resolve_state_root_or_project_root, project_root: Path | None = None, default_project_root: Path | None = None) -> Path:
    from eidolon.core.config_paths import PROJECT_ROOT, resolve_state_root as default_resolve_state_root
    if callable(resolve_state_root_or_project_root):
        resolver = resolve_state_root_or_project_root
        base_root = Path(project_root).resolve() if project_root is not None else (default_project_root or PROJECT_ROOT)
    else:
        resolver = default_resolve_state_root
        base_root = Path(resolve_state_root_or_project_root).resolve() if resolve_state_root_or_project_root is not None else (default_project_root or PROJECT_ROOT)
    target_root = resolver(base_root)
    legacy_pairs = [
        (base_root / 'python' / 'data' / 'mesh', target_root / 'mesh'),
        (base_root / 'python' / 'data' / 'operate', target_root / 'operate'),
        (base_root / 'python' / 'data' / 'evidence', target_root / 'evidence'),
        (base_root / 'python' / 'data' / 'healing', target_root / 'healing'),
        (base_root / 'python' / 'data' / 'browser', target_root / 'browser'),
        (base_root / 'python' / 'data' / 'generated', target_root / 'generated'),
        (base_root / 'python' / 'data' / 'voice', target_root / 'voice'),
        (base_root / 'data' / 'user', target_root / 'user'),
        (base_root / 'data' / 'autonomy', target_root / 'autonomy'),
        (base_root / 'data' / 'mesh', target_root / 'mesh_legacy'),
        (base_root / 'data' / 'persistence', target_root / 'persistence'),
        (base_root / 'data' / 'auth', target_root / 'auth'),
        (base_root / 'data' / 'graph', target_root / 'graph'),
        (base_root / 'data' / 'backups', target_root / 'backups'),
    ]
    for src, dst in legacy_pairs:
        copy_tree_once(src, dst)
    for src, dst in [
        (base_root / 'python' / 'data' / 'llm_config.json', target_root / 'llm_config.json'),
        (base_root / 'python' / 'data' / 'openai_token.json', target_root / 'openai_token.json'),
    ]:
        copy_file_once(src, dst)
    return target_root

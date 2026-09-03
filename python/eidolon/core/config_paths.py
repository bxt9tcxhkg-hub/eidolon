from __future__ import annotations

import os
from pathlib import Path

_PYTHON_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = _PYTHON_ROOT.parent
LEGACY_PYTHON_DATA_DIR = _PYTHON_ROOT / 'data'
LEGACY_DATA_ROOT = PROJECT_ROOT / 'data'


def default_external_state_root() -> Path:
    explicit = os.environ.get('EIDOLON_STATE_DIR', '').strip()
    if explicit:
        return Path(explicit).expanduser()
    local_appdata = os.environ.get('LOCALAPPDATA', '').strip()
    return (Path(local_appdata) / 'Eidolon' / 'state') if local_appdata else (PROJECT_ROOT.parent / 'AppData' / 'Local' / 'Eidolon' / 'state')


def resolve_state_root(project_root: str | Path | None = None) -> Path:
    explicit = os.environ.get('EIDOLON_STATE_DIR', '').strip()
    if explicit:
        root = Path(explicit).expanduser()
    elif project_root is None or Path(project_root).resolve() == PROJECT_ROOT.resolve():
        root = default_external_state_root()
    else:
        root = Path(project_root).resolve() / '.eidolon-state'
    root.mkdir(parents=True, exist_ok=True)
    return root


def state_path(*parts: str, project_root: str | Path | None = None) -> Path:
    path = resolve_state_root(project_root).joinpath(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def legacy_repo_path(*parts: str, project_root: str | Path | None = None) -> Path:
    base_root = Path(project_root).resolve() if project_root is not None else PROJECT_ROOT
    return (base_root / 'python' / 'data' / Path(*parts[1:])) if parts and parts[0] == 'python-data' else (base_root / 'data' / Path(*parts))

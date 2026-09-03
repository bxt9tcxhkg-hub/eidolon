from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from eidolon.core.config import PROJECT_ROOT, resolve_state_root

STATE_ROOT = resolve_state_root(PROJECT_ROOT)
ARCHIVE_ROOT = STATE_ROOT / '_legacy_repo_snapshot' / datetime.now().strftime('%Y%m%dT%H%M%S')

LEGACY_DIRS = [
    ('python/data/mesh', 'mesh'),
    ('python/data/operate', 'operate'),
    ('python/data/evidence', 'evidence'),
    ('python/data/healing', 'healing'),
    ('python/data/browser', 'browser'),
    ('python/data/generated', 'generated'),
    ('python/data/voice', 'voice'),
    ('data/user', 'user'),
    ('data/autonomy', 'autonomy'),
    ('data/mesh', 'mesh_legacy'),
    ('data/persistence', 'persistence'),
    ('data/auth', 'auth'),
    ('data/graph', 'graph'),
    ('data/backups', 'backups'),
]

LEGACY_FILES = [
    ('python/data/llm_config.json', 'llm_config.json'),
    ('python/data/openai_token.json', 'openai_token.json'),
]


def merge_dir(src: Path, dst: Path) -> tuple[int, int]:
    copied = 0
    overwritten = 0
    if not src.exists():
        return copied, overwritten
    for item in src.rglob('*'):
        rel = item.relative_to(src)
        target = dst / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            overwritten += 1
        shutil.copy2(item, target)
        copied += 1
    return copied, overwritten


def archive_path(rel: str) -> Path:
    return ARCHIVE_ROOT / Path(rel)


def main() -> int:
    print(f'project_root={PROJECT_ROOT}')
    print(f'state_root={STATE_ROOT}')
    archived_any = False
    for src_rel, dst_rel in LEGACY_DIRS:
        src = PROJECT_ROOT / src_rel
        dst = STATE_ROOT / dst_rel
        if not src.exists():
            print(f'skip_dir missing {src_rel}')
            continue
        copied, overwritten = merge_dir(src, dst)
        arc = archive_path(src_rel)
        arc.parent.mkdir(parents=True, exist_ok=True)
        if arc.exists():
            shutil.rmtree(arc)
        shutil.move(str(src), str(arc))
        archived_any = True
        print(f'migrated_dir {src_rel} -> {dst_rel} copied={copied} overwritten={overwritten} archived={arc}')
    for src_rel, dst_rel in LEGACY_FILES:
        src = PROJECT_ROOT / src_rel
        dst = STATE_ROOT / dst_rel
        if not src.exists():
            print(f'skip_file missing {src_rel}')
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            shutil.copy2(src, dst)
        else:
            shutil.copy2(src, dst)
        arc = archive_path(src_rel)
        arc.parent.mkdir(parents=True, exist_ok=True)
        if arc.exists():
            arc.unlink()
        shutil.move(str(src), str(arc))
        archived_any = True
        print(f'migrated_file {src_rel} -> {dst_rel} archived={arc}')
    if not archived_any:
        print('nothing_to_archive')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

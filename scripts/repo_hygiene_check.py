from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ACTIVE_ROOT_FILES = {
    '.gitignore',
    'AGENT.md',
    'ARCHITECTURE.md',
    'Cargo.lock',
    'Cargo.toml',
    'pytest.ini',
    'README.md',
    'ROADMAP.md',
}
ACTIVE_ROOT_DIRS = {
    '.hermes',
    'crates',
    'docs',
    'dogfood-output',
    'eidolon',
    'python',
    'references',
    'scripts',
    'sketches',
    'skills',
    'SPECS',
    'target',
    'tests',
    '.pytest_cache',
}
SCRATCH_PREFIXES = ('_live_index', '_ui_', '_chat_')
LEGACY_STATE_DIRS = (ROOT / 'data', ROOT / 'python' / 'data')


def main() -> None:
    unexpected = []
    for p in sorted(ROOT.iterdir()):
        name = p.name
        if p.is_file() and name not in ACTIVE_ROOT_FILES:
            unexpected.append(name)
        elif p.is_dir() and name not in ACTIVE_ROOT_DIRS:
            unexpected.append(name + '/')

    python_data = ROOT / 'python' / 'data'
    scratch = []
    if python_data.exists():
        for p in sorted(python_data.iterdir()):
            if p.is_file() and p.name.startswith(SCRATCH_PREFIXES):
                scratch.append(p.name)

    legacy_state = [str(p.relative_to(ROOT)) for p in LEGACY_STATE_DIRS if p.exists()]

    print('Repo hygiene report')
    print(f'root_unexpected={len(unexpected)}')
    for item in unexpected:
        print('  unexpected:', item)
    print(f'python_data_scratch={len(scratch)}')
    for item in scratch:
        print('  scratch:', item)
    print(f'legacy_state_dirs={len(legacy_state)}')
    for item in legacy_state:
        print('  legacy_state:', item)

    if not unexpected and not scratch and not legacy_state:
        print('status=clean')
    else:
        print('status=needs_attention')


if __name__ == '__main__':
    main()

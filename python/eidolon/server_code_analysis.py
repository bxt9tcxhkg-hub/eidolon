from __future__ import annotations

import ast
from pathlib import Path


def analyze_python_file(file_path: str) -> dict:
    target = Path(file_path)
    if not target.exists():
        return {'error': f'Datei nicht gefunden: {file_path}'}
    try:
        source = target.read_text(encoding='utf-8')
        tree = ast.parse(source)
        functions = []
        classes = []
        imports = []
        complexity = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({'name': node.name, 'lineno': node.lineno, 'args': len(node.args.args)})
                complexity += 1
            elif isinstance(node, ast.ClassDef):
                classes.append({'name': node.name, 'lineno': node.lineno})
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(ast.dump(node))
        lines = len(source.splitlines())
        non_empty = len([line for line in source.splitlines() if line.strip()])
        comments = len([line for line in source.splitlines() if line.strip().startswith('#')])
        return {
            'path': str(target),
            'exists': True,
            'functions': functions[:50],
            'classes': classes[:20],
            'imports': imports[:30],
            'lines': lines,
            'non_empty_lines': non_empty,
            'comment_lines': comments,
            'complexity': complexity + lines // 10,
            'maintainability': max(1, min(100, 100 - complexity * 2 - lines // 20)),
            'long_functions': [item for item in functions if item['lineno'] > 50][:5],
        }
    except SyntaxError as exc:
        return {'path': str(target), 'error': f'Syntax-Fehler: {exc}'}
    except Exception as exc:
        return {'path': str(target), 'error': str(exc)}

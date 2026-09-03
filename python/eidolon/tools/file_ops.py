"""Dateioperationen: patch, read, write — ersetzt provisionale Shell-Hacks."""
from pathlib import Path

def read_file(path: str, start_line: int = 1, end_line: int = None):
    """
    Liest Dateiinhalt mit optionalen Zeilenbegrenzungen.
    Gibt strukturierte Antwort mit Metadaten zurück.
    """
    p = Path(path)
    if not p.exists():
        return {"error": f"Datei nicht gefunden: {path}", "content": ""}
    if not p.is_file():
        return {"error": f"Pfad ist keine Datei: {path}", "content": ""}
    
    lines = p.read_text(encoding="utf-8").splitlines()
    total = len(lines)
    
    if end_line is None:
        end_line = total
    
    # Clamp
    start_line = max(1, start_line)
    end_line = min(total, end_line)
    
    content_lines = lines[start_line - 1:end_line]
    return {
        "path": path,
        "total_lines": total,
        "start_line": start_line,
        "end_line": end_line,
        "content": "\n".join(content_lines),
        "error": None
    }

def write_file(path: str, content: str):
    """
    Schreibt Inhalt in Datei (überschreibt).
    Erstellt Eltern-Verzeichnisse automatisch.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return {"path": path, "bytes_written": len(content), "error": None}

def patch_file(path: str, old_string: str, new_string: str):
    """
    Findet und ersetzt einen eindeutigen String in der Datei.
    Fehlerbehandlung für mehrere Treffer.
    """
    p = Path(path)
    if not p.exists():
        return {"error": f"Datei nicht gefunden: {path}"}
    
    content = p.read_text(encoding="utf-8")
    matches = content.count(old_string)
    
    if matches == 0:
        return {"error": f"'old_string' nicht gefunden in {path}"}
    if matches > 1:
        return {"error": f"'old_string' mehrfach gefunden ({matches}x) in {path}"}
    
    patched = content.replace(old_string, new_string, 1)
    p.write_text(patched, encoding="utf-8")
    return {"path": path, "replacements": 1, "error": None}

def list_directory(path: str):
    """
    Listet Verzeichnisinhalt mit Dateitypen und Größen.
    """
    p = Path(path)
    if not p.exists():
        return {"error": f"Verzeichnis nicht gefunden: {path}"}
    
    entries = []
    for entry in sorted(p.iterdir()):
        stat = entry.stat()
        entries.append({
            "name": entry.name,
            "type": "dir" if entry.is_dir() else "file",
            "size": stat.st_size,
            "modified": stat.st_mtime
        })
    return {"path": path, "entries": entries, "error": None}

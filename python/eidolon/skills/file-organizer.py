"""Datei-Organizer-Skill: Organisiert Dateien in Ordnern."""
from pathlib import Path
import os

def run(params: dict) -> dict:
    directory = params.get("directory", ".")
    pattern = params.get("pattern", "*")
    
    base = Path(directory)
    if not base.exists():
        return {"error": f"Verzeichnis nicht gefunden: {directory}"}
    
    files = list(base.glob(pattern))
    results = []
    
    for f in files:
        if f.is_file():
            ext = f.suffix.lower().lstrip('.')
            if not ext:
                ext = "other"
            target_dir = base / ext
            target_dir.mkdir(exist_ok=True)
            try:
                new_path = target_dir / f.name
                f.rename(new_path)
                results.append({"file": str(f), "new_path": str(new_path)})
            except Exception as e:
                results.append({"file": str(f), "error": str(e)})
    
    return {"organized": len(results), "results": results}

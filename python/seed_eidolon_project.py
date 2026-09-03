#!/usr/bin/env python3
"""Seeded das Eidolon-Projekt aus der Codebasis-Analyse."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from eidolon.workspaces.project_model import ProjectService
from eidolon.workspaces.project_analyzer import ProjectAnalyzer


def main():
    root = Path(__file__).parent.parent
    service = ProjectService(root)
    analyzer = ProjectAnalyzer(root)
    
    analysis = analyzer.analyze()
    print(f"Projekt: {analysis['title']}")
    print(f"Module: {len(analysis['modules'])}")
    print(f"Roadmap-Items: {len(analysis['roadmap_items'])}")
    
    # Prüfen ob schon vorhanden
    existing = [p for p in service.list_projects() if "Eidolon" in p.title]
    if existing:
        print(f"\n⚠ Projekt existiert bereits:")
        for p in existing:
            print(f"   [{p.status}] {p.title} ({len(p.elements)} Elemente)")
        
        print("\nLöschen und neu seeden? (j/n): ", end="")
        if input().strip().lower() != "j":
            print("Abgebrochen.")
            return
    
    # Alte Eidolon-Projekte löschen
    for p in existing:
        service.delete_project(p.id)
    
    # Projekt anlegen
    project = service.create_project(
        title=analysis["title"],
        description=analysis["description"],
        domain="development",
    )
    print(f"\n✓ Projekt angelegt: {project.id}")
    
    # Module als Elemente
    module_ids = {}
    for mod in analysis["modules"]:
        element = service.add_element(
            project.id,
            title=f"{mod['name']} ({mod['files']} Dateien)",
            description=f"Pfad: {mod['path']} — Status: {mod['status']}",
            status="planned" if mod["status"] == "active" else "idea",
            priority=2 if mod["status"] == "active" else 1,
            element_type="deliverable",
            tags=["module", mod["name"]],
        )
        if element:
            module_ids[mod["name"]] = element.id
    print(f"✓ {len(module_ids)} Module angelegt")
    
    # Roadmap-Items als Tasks
    prev_id = None
    count = 0
    for item in analysis["roadmap_items"][:20]:
        element = service.add_element(
            project.id,
            title=item["title"],
            description=f"Phase: {item['phase']}",
            status=item["status"],
            priority=3 if item["status"] == "done" else 2,
            element_type="task",
            tags=["roadmap", item["phase"]],
            dependencies=[prev_id] if prev_id else [],
        )
        if element:
            prev_id = element.id
            count += 1
    print(f"✓ {count} Roadmap-Tasks angelegt")
    
    # Zusammenfassung
    project = service.get_project(project.id)
    print(f"\n{'='*60}")
    print(f"Eidolon-Projekt geseeded!")
    print(f"  ID: {project.id}")
    print(f"  Elemente: {len(project.elements)}")
    print(f"  Module: {len(module_ids)}")
    print(f"  Roadmap-Tasks: {count}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

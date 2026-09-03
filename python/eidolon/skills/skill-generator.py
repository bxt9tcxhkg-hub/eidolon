"""Skill-Generator-Skill: Erkennt wiederkehrende Patterns und generiert automatisch neue Skills."""
from collections import Counter
from pathlib import Path
import json
import re

from eidolon.core.config import PROJECT_ROOT, state_path

def run(params: dict) -> dict:
    # Analysiere Chat-Logging für Patterns
    log_path = state_path('persistence', 'chat_history.json')
    skills_dir = PROJECT_ROOT / 'python' / 'eidolon' / 'skills'
    
    patterns = []
    
    if log_path.exists():
        try:
            history = json.loads(log_path.read_text())
        except (json.JSONDecodeError, ValueError):
            history = []
    else:
        history = []
    
    # Sammle alle user-Messages
    user_messages = []
    for entry in history:
        if isinstance(entry, dict):
            msg = entry.get("user_message") or entry.get("message", "")
            if msg and isinstance(msg, str):
                user_messages.append(msg)
    
    # Pattern-Erkennung: Wiederkehrende Keywords/Phrasen
    keyword_counts = Counter()
    for msg in user_messages:
        words = msg.lower().split()
        # Bigrams und Unigrams zählen
        for w in words:
            keyword_counts[w] += 1
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            keyword_counts[bigram] += 1
    
    # Top-Patterns mit Threshold >= 2
    frequent_patterns = [(p, c) for p, c in keyword_counts.most_common(10) if c >= 2]
    
    # Generiere Skill-Vorschläge
    generated_skills = []
    for pattern, count in frequent_patterns:
        if not pattern.strip():
            continue
        skill_name = pattern.replace(" ", "-").replace("_", "-")[:30]
        if not skill_name:
            continue
        
        # Prüfe, ob Skill bereits existiert
        existing = list(skills_dir.glob(f"{skill_name}.py"))
        if not existing:
            generated_skills.append({
                "name": skill_name,
                "trigger": pattern,
                "frequency": count,
                "template": f'# Auto-generierter Skill für Pattern: "{pattern}"\ndef run(params):\n    return {{"pattern": "{pattern}", "count": {count}}}'
            })
    
    return {
        "analyzed_messages": len(user_messages),
        "frequent_patterns": frequent_patterns,
        "generated_skills": generated_skills,
        "total_generated": len(generated_skills)
    }

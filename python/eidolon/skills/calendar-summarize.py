"""Kalender-Summarizer-Skill: Fasst Kalender-Events oder Text zusammen."""
import re
from collections import defaultdict

def run(params: dict) -> dict:
    text = params.get("text", "")
    events_file = params.get("events_file", "")
    
    if events_file:
        try:
            with open(events_file, 'r') as f:
                text = f.read()
        except FileNotFoundError:
            return {"error": f"Datei nicht gefunden: {events_file}"}
    
    # Einfache Kalender-Pattern-Erkennung
    date_pattern = r'\d{1,2}\.\d{1,2}\.\d{2,4}'
    events = defaultdict(list)
    
    for line in text.split('\n'):
        dates = re.findall(date_pattern, line)
        for d in dates:
            events[d].append(line.strip())
    
    summary = {
        "events_by_date": dict(events),
        "total_events": sum(len(v) for v in events.values()),
        "dates": list(events.keys())
    }
    
    return summary

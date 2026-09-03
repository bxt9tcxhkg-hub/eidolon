"""Web-Suche via DuckDuckGo API mit Offline-Cache."""
import json
import hashlib
import urllib.parse
import urllib.request
from eidolon.core.config import state_path

CACHE_DIR = state_path('browser', 'search_cache')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _cache_key(query: str) -> str:
    """Generiert Hash für Query-Caching."""
    return hashlib.sha256(query.encode()).hexdigest()

def _load_cache(key: str):
    """Lädt gecachte Ergebnisse, falls vorhanden."""
    cache_file = CACHE_DIR / f"{key}.json"
    if cache_file.exists():
        with open(cache_file) as f:
            return json.loads(f.read())
    return None

def _save_cache(key: str, results):
    """Speichert Suchergebnisse im Cache."""
    cache_file = CACHE_DIR / f"{key}.json"
    with open(cache_file, "w") as f:
        json.dump(results, f)

def web_search(query: str, max_results: int = 5):
    """
    Sucht im Web via DuckDuckGo Instant Answer API.
    Nutzt Offline-Cache für wiederholte Queries.
    """
    key = _cache_key(query)
    cached = _load_cache(key)
    if cached:
        return cached

    url = "https://api.duckduckgo.com/?" + urllib.parse.urlencode({
        "q": query,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1,
        "no_redirect": 1,
        "ddg_ads": 0,
        "t": "eidolon",
    })
    
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            results = []
            
            # Instant Answer
            if data.get("AbstractText"):
                results.append({
                    "title": data.get("Heading", "Instant Answer"),
                    "url": data.get("AbstractURL", ""),
                    "snippet": data.get("AbstractText", ""),
                    "source": "duckduckgo"
                })
            
            # Related Topics (Text-basiert)
            for topic in data.get("RelatedTopics", [])[:max_results - len(results)]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append({
                        "title": topic.get("FirstURL", "").split("/")[-1] or "Related",
                        "url": topic.get("FirstURL", ""),
                        "snippet": topic.get("Text", ""),
                        "source": "duckduckgo"
                    })
            
            if not results:
                results.append({
                    "title": "Keine Ergebnisse",
                    "snippet": f"Keine Suchergebnisse für: {query}",
                    "source": "duckduckgo"
                })
            
            _save_cache(key, results)
            return results[:max_results]
    except Exception as e:
        return [{
            "title": "Fehler",
            "snippet": f"Suche fehlgeschlagen: {str(e)}",
            "source": "error"
        }]

def clear_cache():
    """Löscht alle Cachedateien."""
    for f in CACHE_DIR.glob("*.json"):
        f.unlink()

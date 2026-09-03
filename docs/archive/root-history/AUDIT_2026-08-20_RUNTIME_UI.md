# Eidolon Audit — Runtime + Web/Mobile UI

Datum: 2026-08-20
Scope: Laufende Python-PoC-Runtime auf Port 8002, Web-UI `python/eidolon/web/index.html`, Live-Interaktion im echten Edge-Fenster, Backend-Endpunkte, Stage-C-Autonomie-Stand.

## Executive Summary

Der Kernstatus von Eidolon ist **teilweise funktional, aber nicht release-reif**.

**Was funktioniert:**
- Runtime `/health` meldet `ok`
- QUIC-Port 4434 lauscht
- Integrationsstatus für Ollama/OpenAI ist jetzt über `/llm/connection` plus kompatibles `/integrations/status` ehrlich abbildbar
- Settings-POST funktioniert
- Chat-POST funktioniert
- Delegation-POST funktioniert
- Stage-C-Persistenzdateien für Strategy/Delegation existieren
- Desktop-Navigation zwischen Tabs funktioniert sichtbar

**Was nicht release-reif ist:**
- Live-WebSocket der UI ist defekt
- Self-Reflect-Button ist hart kaputt (500)
- Chat rendert Serverantwort falsch
- Frontend-Error-Reporting ist selbst fehlerhaft
- Mesh-/Pairing-Inbox ist schema-seitig falsch verdrahtet
- Mobile-Navigation hat keine Funktionsparität
- Code-Fix-UI behauptet Erfolg, obwohl nur ein Stub zurückkommt

## Priorisierte Findings

### F1 — WebSocket-Liveupdates sind defekt
**Severity:** Kritisch  
**Kategorie:** Funktional / Runtime / UI

**Symptom**
- Live im Edge-Fenster sichtbar: `WebSocket: Getrennt`
- UI bekommt keine Live-Health-Updates

**Live-Evidenz**
- Echter WebSocket-Client gegen `ws://127.0.0.1:8003/ws` bricht sofort ab: `ConnectionClosedError no close frame received or sent`
- Uvicorn-Log am isolierten Audit-Port 8003 zeigt:
  - `INFO: 127.0.0.1:62506 - "WebSocket /ws" [accepted]`
  - `[WebSocket] Error: 'CapabilityRegistry' object has no attribute 'all'`

**Root Cause**
- `agent_server.py:1446-1449` baut `_build_ws_health()` mit `capability_registry.all()`
- Der aktuelle `CapabilityRegistry` besitzt diese Methode offenbar nicht mehr
- Dadurch fällt der WebSocket direkt beim Initial-Health-Payload um

**Code-Evidenz**
- `agent_server.py:1398-1410` — WebSocket sendet initial sofort `_build_ws_health()`
- `agent_server.py:1438-1451` — defekter `_build_ws_health()`-Pfad

---

### F2 — Self-Reflect-Button ist hart kaputt
**Severity:** Kritisch  
**Kategorie:** Funktional

**Symptom (historisch, inzwischen behoben)**
- Damals lieferte `GET /code/self-reflect` `500 Internal Server Error`
- Der damalige UI-Button `Start Self-Reflect` konnte deshalb nicht funktionieren

**Historische Evidenz**
- HTTP-Test damals: `GET /code/self-reflect -> HTTP 500`

**Root Cause damals**
- `agent_server.py` rief einen nicht mehr vorhandenen / nicht verdrahteten Self-Reflect-Pfad auf
- alte Claims zu `python/eidos/core/self_code_generator.py` passten nicht mehr zur aktiven Codebasis
- dadurch drifteten Doku und Runtime auseinander

**Heutiger Stand**
- `/code/self-reflect` liefert jetzt reale Kandidatenlisten statt 500
- `/code/fix` und `/code/refactor` nutzen eine echte Python-Mutationspipeline mit Backup + `py_compile`

**Code-Evidenz**
- `agent_server.py:686-703`
- `python/eidos/core/self_code_generator.py:7-34`

---

### F3 — Chat funktioniert backend-seitig, aber das Frontend rendert die Antwort falsch
**Severity:** Hoch  
**Kategorie:** Funktional / UX

**Symptom**
- Live im Chat sichtbar: statt sauberer Antwort wird JSON-artiger Wrapper angezeigt
- Beobachtet im Edge-Fenster nach UI-Sendevorgang:
  - `Eidolon: {"ok":true,"reply":"Eidolon: ui audit chat test"}`

**Live-Evidenz**
- UI-Interaktion erfolgreich ausgeführt
- Backend liefert bei POST `/chat`:
  - `{"matched_skill":"chat","intent":"chat","result":{"ok":true,"reply":"Eidolon: ui-audit ping"}}`

**Root Cause**
- Frontend prüft in `sendChat()` nur:
  - `data.result.result`
  - `data.reply`
- Der echte Rückgabewert liegt aber in:
  - `data.result.reply`
- Deshalb fällt das UI auf `JSON.stringify(data.result || data)` zurück

**Code-Evidenz**
- Frontend: `python/eidolon/web/index.html:1200-1215`
- Backend-Response beobachtet per POST `/chat`

---

### F4 — Frontend-Error-Reporting ist selbst kaputt
**Severity:** Hoch  
**Kategorie:** Console / Observability

**Symptom**
- Wenn ein Frontendfehler auftritt, ist der Error-Reporter selbst fehleranfällig
- Dadurch geht Debug-Evidenz verloren oder wird sekundär beschädigt

**Root Cause**
- In beiden Listenern wird `.catch(() => {})` auf das Ergebnis von `JSON.stringify(...)` gehängt
- `JSON.stringify(...)` gibt einen String zurück, keinen Promise

**Code-Evidenz**
- `python/eidolon/web/index.html:624-649`
- Konkret falsch:
  - `body: JSON.stringify({...}).catch(() => {})`

**Erwartetes Muster**
- `.catch()` muss an `fetch(...)` hängen, nicht an `JSON.stringify(...)`

---

### F5 — Mesh-Inbox und Pairing-Verbindungen sind schema-seitig falsch verdrahtet
**Severity:** Hoch  
**Kategorie:** Funktional

**Symptom**
- UI erwartet `data.inbox`
- API liefert `{"messages": [...]}`
- Dadurch werden empfangene Daten im UI nicht korrekt angezeigt

**Live-Evidenz**
- HTTP-Test: `GET /mesh/inbox/all -> 200 {"messages":[]}`
- Frontend-Code prüft explizit `data.inbox`

**Root Cause**
- Response-Schema des Backends passt nicht zur UI-Erwartung

**Code-Evidenz**
- Frontend Mesh-Inbox: `python/eidolon/web/index.html:973-988`
- Frontend Pairing-Inbox: `python/eidolon/web/index.html:1068-1083`
- Beobachtete API-Antwort: `{"messages":[]}`

---

### F6 — Mobile-Navigation hat keine Funktionsparität
**Severity:** Hoch  
**Kategorie:** Mobile / UX / Funktional

**Symptom**
- Unter `@media (max-width: 768px)` wird die Sidebar ausgeblendet
- Mobile Bottom Bar ist dann die primäre Navigation
- Diese Bottom Bar enthält aber **nicht alle Funktionsbereiche**

**Fehlende Bereiche auf Mobile**
- `Autonome Ziele`
- `Self-Healing`

**Root Cause**
- Mobile-Bar definiert nur:
  - Chat
  - Dashboard
  - Mesh
  - Code
  - Identity
  - Settings
- Es gibt keinen mobilen Zugriff auf Goals/Healing

**Code-Evidenz**
- Responsive-Schalter: `python/eidolon/web/index.html:295-304`
- Mobile-Bar: `python/eidolon/web/index.html:607-614`
- Desktop-Sidebar mit vollständiger Navigation: `python/eidolon/web/index.html:365-373`

---

### F7 — Code-Fix-UI behauptet „Patch applied“, obwohl das Backend nur einen Stub meldet
**Severity:** Hoch  
**Kategorie:** Truthfulness / UX / Funktional

**Symptom**
- UI präsentiert erfolgreiche Reparatur sehr stark als echten Patch
- Backend liefert aber nur einen Platzhalter-Stub

**Live-Evidenz**
- POST `/code/fix` liefert `200`, aber mit:
  - `"validation":"not_applied_runtime_stub"`
  - `"diff_summary":"konservativer Platzhalter-Fix ..."`
- `file_path` zeigt sogar auf das Projektroot statt auf eine konkret gepatchte Datei

**Root Cause**
- `SelfCodeGenerator.fix_issue()` ist aktuell nur Vertrags-Stubbing
- Frontend zeigt trotzdem „✅ Patch applied“

**Code-Evidenz**
- Backend-Stubs: `python/eidos/core/self_code_generator.py:26-34`
- Frontend-Erfolgsmeldung: `python/eidolon/web/index.html:1113-1127`

---

## Weitere Beobachtungen

### O1 — Desktop-Tab-Navigation funktioniert grundsätzlich
**Severity:** Info
- Live geprüft im Edge-Fenster:
  - Settings → Dashboard → Chat funktioniert sichtbar
- Der Verdacht „Buttons lösen vielleicht gar nichts aus“ trifft also **nicht pauschal** zu
- Aber mehrere Aktions-Buttons und Datenpfade sind trotzdem real defekt oder irreführend

### O2 — Backend-/Autonomy-Grundzustand ist größtenteils grün
**Severity:** Info
- `/health` meldet `ok`
- QUIC-Port 4434: `listening=true`
- `/integrations/status`: zeigt denselben ehrlichen API-Key-/Provider-Status wie `/llm/connection`; lokales OAuth wird nicht behauptet
- `data/autonomy/delegation_economy.json` existiert und enthält reale Scope/Capability-Stats
- `data/autonomy/strategy_memory.json` existiert und enthält reale Goal-Action-Stats

## Empfohlene Abarbeitungsreihenfolge

1. **F1 WebSocket fixen**
   - UI-Livezustand muss zuverlässig werden
2. **F2 Self-Reflect 500 fixen**
   - harter Defekt
3. **F3 Chat-Parsing fixen**
   - Kernfunktion UX kaputt trotz funktionierendem Backend
4. **F5 Inbox-Schema fixen**
   - Mesh/Pairing sichtbar machen
5. **F7 Truthful Code-Fix-UX herstellen**
   - keine falschen Erfolgsbehauptungen
6. **F4 Frontend-Error-Reporter fixen**
   - bessere Diagnostik für Restfehler
7. **F6 Mobile-Navigation auf vollständige Parität bringen**
   - Voraussetzung für saubere Mobile-UI-Überarbeitung

## Audit-Fazit

Eidolon ist **nicht grundsätzlich kaputt**, aber die aktuelle Web-/Mobile-Oberfläche ist in genau den kritischen Stellen inkonsistent, die Vertrauen erzeugen sollen:
- Livezustand
- Self-Repair
- Chat-Ausgabe
- Mesh-/Pairing-Sichtbarkeit
- Mobile-Parität

Für den nächsten Schritt sollte **nicht erst Design**, sondern zuerst die **funktionale Korrektheit der UI** hergestellt werden. Erst danach lohnt sich die visuelle Vereinheitlichung zu „schlicht, modern, übersichtlich, einheitlich“.

# ARCHITECTURE — Eidolon Central Agentic System

> Status: aktuelles Implementierungsbild des aktiven Produktkerns. Diese Datei beschreibt **Ist-Architektur**, nicht Wunschdenken.

## Architektur in einem Satz
Eidolon ist derzeit ein **Python-zentriertes agentisches System** mit FastAPI-Server, gemeinsamem Work-Context-Kern für Chat und Operate, Workspace-/Projektlogik, Rollenregister und modularisierter Web-Oberfläche; technische Nebenflächen wie Mesh, Healing und Code-Mutation existieren, sind aber produktlogisch nachgeordnet.

## Primäre Ebenen

### 1. Product / Conversation Layer
- `python/eidolon/chat_runtime.py`
- `python/eidolon/chat_route_support.py`
- Erzwingt arbeitsführenden Antwortvertrag
- `POST /chat` und `GET /chat/context` ziehen ihren Runtime-Kontext über denselben `session_payload`-Pfad
- Baut Runtime-Kontext aus Chat, Workspace und Operate-Snapshot auf Basis des `work_context_kernel`
- Fängt generische Assistentenantworten ab und fällt auf geerdete Richtung + Empfehlung + nächsten Schritt zurück

### 2. Operate Kernel
- `python/eidolon/operate/contracts.py`
- `python/eidolon/operate/service.py`
- `python/eidolon/operate/bridge.py`
- Modelliert Session, Objective, Run, Approval, Blocking Issue, Evidence, Transition, Next Action
- Dient als wahrheitsfähiger Arbeitskern für sichtbaren Fortschritt

### 3. Workspace / Project Layer
- `python/eidolon/workspaces/`
- Liefert Projekt-/Workspace-Zustand und Runtime-Payloads
- Workspace-Payload-, Context- und Assistance-Aufbereitung läuft über kleine Fassaden plus spezialisierte Hilfsmodule
- Bridge synchronisiert aktive Workspaces in den Operate-Kernel

### 4. Bot Role Layer
- `python/eidolon/bots/role_registry.py`
- Trennt aktive Rollen von definierten Vorlagen
- Erzwingt Freigabe für dauerhafte, freigabepflichtige Rollen

### 5. Application Layer
- `python/agent_server.py`
- Integrationspunkt für API, Produktlogik und UI-Auslieferung
- Runtime-Service-Erzeugung läuft über kleine Contracts-/Bootstrap-/Auth-Module statt über eine dichte Einzeldatei
- Live geprüft: 148 Routes im aktuellen App-Objekt

### 6. Web UI Layer
- `python/eidolon/web/index.html`
- `python/eidolon/web/app-shell.css`
- `python/eidolon/web/components/app-components.css`
- CSS ist nach Shell-, Chat- und Goals-Slices in Importdateien aufgeteilt
- Chat zeigt Runtime-Kontext
- Operate zeigt Run-/Approval-/Blocker-/Evidence-/Transition-Sicht

## Aktuelle Hauptschulden
- `python/agent_server.py` ist weiter ein großer Integrationspunkt
- `python/eidolon/web/index.html` bleibt groß und mischt Produktsemantik mit UI-Implementierung
- `python/eidolon/web/app-shell.js` bleibt ein großer SPA-Hotspot
- mehrere historische Dokumente im Repo können ohne Boundary-Regeln fehlgelesen werden, obwohl Archiv-/Finding-Readmes das jetzt explizit begrenzen

## Aktuelle Wahrheitsregel
- Produkt-Soll: `docs/eidolon-specification.md`
- Implementierungs-Ist: Live-Code + Tests + Endpoint-Antworten
- Aktive Fortschrittsquelle: `ROADMAP.md`
- Findings und Root-History sind Referenz, nicht Primärwahrheit
- Dieses Dokument dient der Einordnung der aktiven Struktur, nicht der Übersteuerung der Spezifikation

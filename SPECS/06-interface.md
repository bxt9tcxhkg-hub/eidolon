# SPEC 06: Interfaces & Device Mesh

## Ziel
Keine Drittanbieter-Kanäle. Der Agent kommuniziert direkt mit deinen Geräten über ein eigenes, sicheres Mesh-Netzwerk — ohne Cloud, ohne WhatsApp, Telegram oder Discord.

## 1. Grundprinzip

```
Dein PC  ←──Eidolon Mesh──→  Dein Phone
    ↓                              ↓
Agent Core                    Eidolon App
                               (Flutter)
    ↓                              ↓
Dein Smart Home                Deine Smart Watch
(Home Assistant)               (Watch OS)
```

**Keine zentrale Cloud. Keine Drittanbieter-APIs. Nur deine Geräte, dein Agent, deine Regeln.**

## 2. Interface-Archetypen

### 2.1 Terminal TUI (PC)
```
┌─ Eidolon ──────────────────────────────────────────────┐
│ > User: Was steht diese Woche an?                        │
│                                                           │
│ ✓ calendar-summarize   [████████████] 1.2s   12k Tokens │
│                                                           │
│ Diese Woche:                                              │
│ • Mo: Team-Sync 10:00                                    │
│ • Di: Projekt-Review 14:00                               │
│ • Do: Deadline Feature-X                                 │
│                                                           │
│ 💡 Proaktiv: Do ist auch dein Sohnes Fußballspiel. Soll  │
│    ich den Termin verschieben?                            │
│                                                           │
│ > _                                                       │
└───────────────────────────────────────────────────────────┘
```

### 2.2 Desktop Overlay (Windows/Mac/Linux)
- Tauri-basiertes, transparentes Overlay
- Global Hotkey (z.B. `Alt+Space`)
- Screenshot → Analyse → Aktion
- Clipboard-Integration
- Quick-Commands ohne Tippen

### 2.3 Mobile App (Phone/Tablet)
- Flutter-App (Cross-Platform: iOS, Android)
- Mesh-Client: verbindet sich automatisch mit dem heimischen Agenten
- Push via lokales Netzwerk (keine Cloud-Push-Dienste)
- Sprach-Chat, Text-Chat, Quick-Actions

### 2.4 Watch/Phone Widget
- Kompakte Ansicht fürNotifications
- Sprach-Chat direkt von der Uhr
- Schnelle Aktionen ("Erinner mich in 10min")

### 2.5 Smart Home Integration
- Direkte Anbindung an Home Assistant, openHAB, etc.
- Kein Cloud-Zwang, lokale APIs
- "Agent, schalte das Licht aus" → geht direkt

### 2.6 REST API + WebSocket
- Für Eigenentwicklungen, Scripts, Automationen
- `/api/v1/tasks`, `/api/v1/devices`, `/api/v1/stream`

## 3. Eidolon Mesh — Der Kommunikations-Stack

### 3.1 Übersicht

```
┌──────────────────────────────────────────────────────────┐
│                    Eidolon Mesh Stack                      │
├──────────────────────────────────────────────────────────┤
│  Application Layer                                        │
│  ┌────────────┐ ┌────────────┐ ┌────────────────────┐   │
│  │ Task Sync  │ │ Real-time  │ │ Device Discovery   │   │
│  │ (Aufträge) │ │ Chat/Media  │ │ (Geräte finden)    │   │
│  └─────┬──────┘ └─────┬──────┘ └─────────┬──────────┘   │
├────────┼──────────────┼──────────────────┼───────────────┤
│        │              │                  │               │
│  ┌─────▼──────┐ ┌─────▼──────┐ ┌────────▼──────────┐    │
│  │ QUIC/mTLS  │ │ WebRTC     │ │ mDNS + BLE        │    │
│  │ (Payload)  │ │ (Media)    │ │ (Discovery)       │    │
│  └─────┬──────┘ └─────┬──────┘ └────────┬──────────┘    │
├────────┼──────────────┼──────────────────┼───────────────┤
│  Transport Layer                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │  TCP/IP (LAN/WLAN)  │  BLE  │  Thread/Matter    │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

### 3.2 Transport-Protokolle

| Protokoll | Verwendung | Reichweite | Begründung |
|---|---|---|---|
| **QUIC/mTLS** | Hauptkommunikation (Tasks, Chat, Data) | LAN/WAN | Modern, schnell, eingebautes TLS, Multiplexing |
| **WebRTC** | Sprach/Video-Streaming | LAN/WAN | Peer-to-Peer, NAT-Traversal, niedrige Latenz |
| **mDNS** | Device Discovery im LAN | LAN | Standard, keine Konfiguration nötig |
| **Bluetooth LE** | Direkte Gerätekopplung, Discovery | 10-30m | Kein WLAN nötig, universell verfügbar |
| **Thread/Matter** | Smart Home Integration | Mesh-Netz | Herstellerübergreifend, zukunftssicher |

### 3.3 Eidolon Protocol (EEP) — Nachrichtenformat

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EidolonPacket {
    pub version: u8,              // Protokoll-Version
    pub packet_type: PacketType,  // Was für eine Art Nachricht
    pub source: DeviceId,         // Absender
    pub destination: DeviceId,    // Empfänger
    pub payload: Vec<u8>,         // Verschlüsselte Nutzdaten
    pub nonce: [u8; 12],          // AEAD Nonce
    pub tag: [u8; 16],            // AEAD Tag (Authentifizierung)
    pub timestamp: i64,           // Absendezeit (Replay-Schutz)
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum PacketType {
    // Device Management
    DeviceHello,          // Erste Verbindung / Kopplung
    DeviceGoodbye,        // Verbindung beenden
    DeviceHeartbeat,      // Lebt das Gerät noch?
    DeviceCapability,     // "Ich kann das und das"

    // Task Execution
    TaskRequest,          // "Mach das"
    TaskResponse,         // "Hier ist das Ergebnis"
    TaskProgress,         // "Bin bei 50%"
    TaskCancel,

    // Real-time Communication
    ChatMessage,          // Text-Nachricht
    VoiceFrame,           // Audio-Daten
    MediaFrame,           // Bilder, Screenshots

    // Discovery
    DeviceAnnounce,       // "Ich bin ein neues Gerät"
    ServiceQuery,         // "Wer kann das?"
    ServiceResponse,      // "Ich kann das!"

    // Agent-to-Agent
    AgentHello,
    AgentCapability,
    AgentTaskRequest,
    AgentTaskResponse,
}
```

### 3.4 mTLS-Identität

```rust
// Jedes Gerät bekommt bei der ersten Kopplung ein Geräte-Zertifikat
pub struct DeviceIdentity {
    pub device_id: DeviceId,
    pub name: String,
    pub device_type: DeviceType,
    pub certificate: X509Certificate,  // mTLS Client Cert
    pub public_key: PublicKey,
    pub paired_at: i64,
    pub last_seen: i64,
    pub capabilities: Vec<DeviceCapability>,
}

// Pairing-Flow:
// 1. Host startet "Pairing Mode" (zeigt Pairing-Code)
// 2. Gerät scannt mDNS/BLE → findet Host
// 3. Gerät zeigt Pairing-Code → User vergleicht
// 4. Host signiert Device-Certificate
// 5. Ab jetzt: mTLS-verschlüsselte Kommunikation
```

### 3.5 Discovery-Mechanismen

```rust
// mDNS: Automatisches Finden im lokalen Netzwerk
// → "_eidolon._tcp.local" Service Announcement

// BLE: Direkte Kopplung ohne WLAN
// → Advertisement: Eidolon Device ID + pairing-needed flag

// Thread/Matter: Smart Home Integration
// → Standardisierte Matter-Commissioning-Flow

pub struct DiscoveryEngine {
    mdns: MdnsScanner,
    ble: BleScanner,
    matter: MatterCommissioner,
}

impl DiscoveryEngine {
    pub async fn scan(&self) -> Vec<DiscoveredDevice> {
        // Alle drei Methoden parallel
        let (mdns_devices, ble_devices, matter_devices) = tokio::join!(
            self.mdns.scan(),
            self.ble.scan(),
            self.matter.scan()
        );
        // Zusammenführen, deduplizieren
        merge_devices(mdns_devices, ble_devices, matter_devices)
    }
}
```

### 3.6 Verbindungs-Typen

```rust
pub enum ConnectionType {
    // Direkt im gleichen LAN
    LocalLan {
        host: SocketAddr,
        latency_ms: u32,
    },

    // Direkt via Bluetooth LE (kein WLAN nötig)
    Ble {
        device_address: [u8; 6],
        rssi: i8,  // Signalstärke
    },

    // WebRTC Peer-to-Peer (auch über Internet möglich)
    WebRtc {
        peer_id: PeerId,
        connection_state: ConnectionState,
    },

    // Thread/Matter Mesh
    ThreadMesh {
        node_id: [u8; 16],
        hop_count: u8,
    },
}
```

## 4. Device Registry

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Device {
    pub id: DeviceId,
    pub name: String,
    pub device_type: DeviceType,
    pub connection: ConnectionType,
    pub capabilities: Vec<DeviceCapability>,
    pub status: DeviceStatus,
    pub paired_at: i64,
    pub last_seen: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum DeviceType {
    Host,           // Der PC auf dem der Agent läuft
    Phone,          // Smartphone
    Tablet,         // Tablet
    Watch,          // Smartwatch
    Speaker,        // Smart Speaker
    Display,        // Smart Display
    Sensor,         // Temperatur, Bewegung, etc.
    Appliance,      // Smart Home Geräte
    Custom(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum DeviceCapability {
    Display,        // Kann Inhalte anzeigen
    AudioIn,        // Hat Mikrofon
    AudioOut,       // Hat Lautsprecher
    Camera,         // Hat Kamera
    Haptic,         // Kann vibrieren
    Location,       // Hat GPS
    Sensors,        // Hat Sensoren (Temperatur, etc.)
    Actuator,       // Kann Dinge steuern (Licht, Steckdose)
    Compute,        // Kann berechnen (z.B. Phone als Edge-Device)
}
```

## 5. Konnektivitäts-Flow

```rust
// Beim Start des Agenten:
// 1. Discovery starten (mDNS + BLE + Matter)
// 2. Gefundene Geräte mit bekannten pairen
// 3. Geräteliste anzeigen
// 4. Neue Geräte anzeigen: "Neues Gerät gefunden: 'iPhone von Max' — Koppeln?"

// Pairing:
// 1. Host zeigt Pairing-Code (6-stellig)
// 2. Gerät zeigt selben Code
// 3. User bestätigt auf Host: "Ja, das ist mein Phone"
// 4. mTLS-Zertifikat wird ausgestellt
// 5. Gerät ist verbunden

// Kommunikation:
// 1. Device sendet EidolonPacket
// 2. mTLS-Handshake (falls nötig)
// 3. AEAD-Entschlüsselung
// 4. Payload verarbeiten
// 5. Antwort senden
```

## 6. Voice über Mesh

```rust
// Wake-Word auf dem Gerät selbst erkennen (Edge)
// → Gerät sendet "VoiceFrame" Paket an Host
// → Host transkribiert (Whisper lokal)
// → Host verarbeitet, generiert Antwort
// → Host sendet "VoiceFrame" zurück
// → Gerät spielt TTS ab
```

**Wichtig**: Sprachdaten bleiben lokal auf den Geräten. Keine Cloud-Sprachdienste.

## 7. Tech-Stack

| Komponente | Technologie |
|---|---|
| Mesh-Transport | QUIC (quinn/libp2p), WebRTC (WRTC) |
| mTLS | rustls + rcgen (Zertifikat-Generierung) |
| mDNS | mdns-sd (Rust) |
| BLE | btleplug (Rust) |
| Thread/Matter | matter-rs (Rust) |
| Mobile App | Flutter (Dart) |
| Desktop Overlay | Tauri (Rust + Web) |
| Voice STT | faster-whisper (lokal) |
| Voice TTS | Piper (lokal) |
| Wake-Word | Porcupine oder custom |

## 8. Sicherheit

| Aspekt | Maßnahme |
|---|---|
| Transport | mTLS (gegenseitige Authentifizierung) |
| Verschlüsselung | AES-256-GCM pro Paket |
| Pairing | Manuell via Code-Vergleich (kein "Scan zum Verbinden") |
| Replay-Schutz | Timestamp + Nonce pro Paket |
| Geräte-Identity | Hardware-gebundene Zertifikate |
| Revocation | Gerät kann sofort entzogen werden |

## 9. Checkliste

- [ ] Eidolon Protocol Format (EEP) definieren
- [ ] QUIC-Server + Client (Rust)
- [ ] WebRTC-Integration für Media
- [ ] mDNS-Scanner
- [ ] BLE-Scanner + Pairing
- [ ] mTLS-Handshake
- [ ] Device Registry
- [ ] Discovery Engine
- [ ] Pairing-Flow (Code-Vergleich)
- [ ] Flutter-App (Proof of Concept)
- [ ] Desktop Overlay (Tauri)
- [ ] Voice over Mesh
- [ ] Integration in Agent-Core
- [ ] Unit-Tests für Protokoll
- [ ] Integration-Test: PC ↔ Phone

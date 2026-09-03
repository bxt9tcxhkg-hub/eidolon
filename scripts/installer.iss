[Setup]
AppName=Eidolon Agent
AppVersion=1.0.0
DefaultDirName={autopf}\Eidolon
DefaultGroupName=Eidolon
OutputBaseFilename=Eidolon-Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "target\release\eidolon-cli.exe"; DestDir: "{app}"
Source: "python\*"; DestDir: "{app}\python"; Flags: recursesubdirs
Source: "data\*"; DestDir: "{app}\data"; Flags: recursesubdirs

[Icons]
Name: "{group}\Eidolon"; Filename: "{app}\eidolon-cli.exe"
Name: "{group}\Web-UI"; Filename: "http://localhost:8000"

[Run]
Filename: "{app}\eidolon-cli.exe"; Parameters: "serve"; Flags: runhidden

[Registry]
Root: HKCU; Subkey: "Software\Eidolon"; ValueType: string; ValueName: "InstallDir"; ValueData: "{app}"

[Tasks]
Name: "desktopicon"; Description: "Desktop-Verknüpfung erstellen"; GroupDescription: "Zusätzliche Aufgaben"

# Desktop Test - CachyOS Service Manager

## Übersicht

Dies ist ein funktionaler Desktop-Test der Service-Management-Funktionalität mit einer einfachen GTK4-GUI.

## Features

✅ **Service-Liste anzeigen**
- Vordefinierte Liste häufiger Services
- Echtzeit-Statusanzeige (Active/Inactive/Failed)
- Farbcodierte Status-Indikatoren

✅ **Service-Steuerung**
- **Start**: Service starten
- **Stop**: Service stoppen  
- **Restart**: Service neu starten
- Intelligente Button-Aktivierung basierend auf Status

✅ **Automatische Updates**
- Auto-Refresh alle 5 Sekunden
- Manueller Refresh-Button
- Live-Status-Updates nach Aktionen

✅ **Sicherheit**
- Verwendet `pkexec` für Privilege Escalation
- Root-Rechte nur bei Bedarf
- Timeout-Protection

## Installation

### Voraussetzungen

```bash
# Arch Linux / CachyOS
sudo pacman -S python python-gobject gtk4 libadwaita polkit
```

### Ausführen

```bash
# Im Repository-Verzeichnis
python desktop_test.py
```

Oder ausführbar machen:
```bash
chmod +x desktop_test.py
./desktop_test.py
```

## Verwendung

### Services testen

1. **Service starten**: Klicke auf den grünen "Start"-Button
2. **Service stoppen**: Klicke auf den roten "Stop"-Button
3. **Service neu starten**: Klicke auf "Restart"
4. **Status aktualisieren**: Klicke auf das Refresh-Symbol oben links

### Getestete Services

Der Test enthält folgende häufig verwendete Services:
- NetworkManager
- Bluetooth
- CUPS (Druckdienst)
- SSH Server
- Docker
- Nginx
- PostgreSQL
- Redis

**Hinweis**: Nicht installierte Services werden als "inactive" angezeigt.

## UI-Komponenten

### Status-Anzeige
- 🟢 **● Active** - Service läuft
- 🟠 **○ Inactive** - Service gestoppt
- 🔴 **✗ Failed** - Service fehlgeschlagen

### Buttons
- **Start** (Grün) - Nur aktiv wenn Service gestoppt
- **Stop** (Rot) - Nur aktiv wenn Service läuft
- **Restart** (Grau) - Nur aktiv wenn Service läuft

### Auto-Refresh
Die GUI aktualisiert alle Service-Status automatisch alle 5 Sekunden.

## Technische Details

### Architektur

```
ServiceManagerApp (Adw.Application)
    ↓
MainWindow (Adw.ApplicationWindow)
    ├── HeaderBar
    │   ├── Refresh Button
    │   └── About Button
    ├── ScrolledWindow
    │   └── Service List
    │       └── ServiceRow (für jeden Service)
    │           ├── Name Label
    │           ├── Status Label
    │           └── Action Buttons
    └── StatusBar
```

### Threading

- Service-Aktionen laufen in Background-Threads
- GUI bleibt während Operationen responsiv
- GLib.idle_add() für thread-sichere GUI-Updates

### systemctl Integration

```python
# Status abfragen
systemctl is-active <service>

# Service steuern (mit pkexec)
pkexec systemctl start <service>
pkexec systemctl stop <service>
pkexec systemctl restart <service>
```

## Bekannte Einschränkungen

1. **Root-Rechte erforderlich**: Service-Steuerung benötigt Root (via pkexec)
2. **Zeitverzögerung**: Status-Updates können 1-2 Sekunden dauern
3. **Feste Service-Liste**: Services sind hardcoded (für Test-Zwecke)

## Nächste Schritte

Für die finale Version geplant:
- [ ] Dynamische Service-Erkennung (alle systemd-Units)
- [ ] Service-Suche und Filter
- [ ] Detail-Ansicht mit Logs
- [ ] Service-Dependencies anzeigen
- [ ] CPU/Memory-Monitoring
- [ ] Service-Konfiguration bearbeiten

## Troubleshooting

### "pkexec: command not found"
```bash
sudo pacman -S polkit
```

### GUI startet nicht
```bash
# GTK4 installieren
sudo pacman -S gtk4 libadwaita

# Python-Bindings installieren
sudo pacman -S python-gobject
```

### "Permission denied" beim Service starten
- Normal! `pkexec` sollte nach Passwort fragen
- Stelle sicher, dass polkit installiert ist

## Entwicklung

### Code-Struktur

**ServiceRow**: Einzelne Service-Zeile
- Zeigt Service-Name und Status
- Enthält Start/Stop/Restart-Buttons
- Aktualisiert Status selbstständig

**MainWindow**: Hauptfenster
- Verwaltet Liste aller Services
- Koordiniert Service-Aktionen
- Zeigt Status-Meldungen

**ServiceManagerApp**: Anwendungs-Controller
- GTK/Adwaita Application
- Lifecycle-Management

### Anpassungen

Service-Liste ändern:
```python
self.test_services = [
    'dein-service.service',
    # ... weitere Services
]
```

Refresh-Intervall ändern:
```python
# In start_auto_refresh()
GLib.timeout_add_seconds(10, self.refresh_all_services)  # 10 Sekunden
```

## Screenshots

### Hauptansicht
![Desktop Test](docs/screenshots/desktop-test.png)
*Service-Liste mit Live-Status und Steuerungs-Buttons*

## Lizenz

GPL-3.0 - Siehe LICENSE-Datei

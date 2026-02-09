# CachyOS Service Manager

<div align="center">

![CSM Logo](https://user-gen-media-assets.s3.amazonaws.com/seedream_images/7a5e69cb-bffe-410b-80ca-4e9510e0efec.png)

# CSM - CachyOS Service Manager

**A modern, efficient service management tool for CachyOS**

Systemd integration · GUI & CLI · Real-time monitoring · **Service Groups** · **Full Service Control**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![CachyOS](https://img.shields.io/badge/CachyOS-Optimized-teal)](https://cachyos.org)
[![KDE Plasma](https://img.shields.io/badge/KDE-Plasma-1d99f3)](https://kde.org)
[![GTK4](https://img.shields.io/badge/GTK-4.0-4a90d9)](https://gtk.org)

</div>

## 📋 Übersicht

CachyOS Service Manager ist ein leistungsstarkes Werkzeug zur Verwaltung von systemd-Services unter CachyOS. Es bietet sowohl eine grafische Benutzeroberfläche als auch eine CLI für die effiziente Verwaltung von Systemdiensten.

### ✨ Features

- 🎯 **Vollständige Service-Verwaltung** - Zeige ALLE systemd Services an und steuere sie
- ⚡ **Service-Aktionen** - Start, Stop, Restart, Enable, Disable für jeden Service
- 📦 **Service-Gruppen** - Organisiere Services in Gruppen und steuere sie gemeinsam
- 🔍 **Suche & Filter** - Finde Services schnell mit Suchfunktion und Filtern
- 📊 **Echtzeit-Monitoring** - Live-Überwachung von Service-Status
- 📜 **Log-Viewer** - Integrierte Journal-Log-Anzeige mit 200 Zeilen Historie
- 📈 **Statistik-Dashboard** - Übersicht über aktive, inaktive und fehlerhafte Services
- ⚙️ **Service-Konfiguration** - Detaillierte Service-Informationen
- 🎨 **Dual UI** - KDE Plasma (Qt6) & GNOME (GTK4) Unterstützung
- 🔄 **Auto-Refresh** - Automatische Aktualisierung aller 30 Sekunden
- 🔐 **Sicherheit** - Polkit-Integration für Berechtigungen

## 🚀 Verfügbare Versionen

### 1. **Full Service Manager** (empfohlen für tägliche Nutzung)

**Komplette Service-Verwaltung mit allen Funktionen:**

```bash
# KDE Plasma Version
python full_service_manager_plasma.py

# GNOME/GTK4 Version
python full_service_manager_gtk.py
```

**Features:**
- ✅ Zeigt ALLE systemd Services an (nicht nur vordefinierte)
- ✅ Start/Stop/Restart/Enable/Disable Buttons für jeden Service
- ✅ Suche nach Services (Name oder Beschreibung)
- ✅ Filter: All, Active, Inactive, Failed, Enabled
- ✅ Live-Statistiken (Total, Active, Inactive, Failed, Enabled)
- ✅ Log-Viewer Tab mit vollständigen Service-Logs
- ✅ Tabellen-Ansicht mit Status-Indikatoren
- ✅ Auto-Refresh alle 30 Sekunden

### 2. **Service Groups Manager** (für Gruppen-Organisation)

**Verwaltung von Service-Gruppen:**

```bash
# KDE Plasma Version
python desktop_test_plasma_groups.py

# GNOME/GTK4 Version
python desktop_test_groups.py
```

**Features:**
- ✅ Erstelle Service-Gruppen
- ✅ Starte/Stoppe/Restarte ganze Gruppen
- ✅ Farbcodierung und Icons
- ✅ 6 vordefinierte Templates
- ✅ Collapsible Gruppen-Ansicht

### 3. **Basic Service Test** (für Entwicklung/Test)

```bash
# KDE Plasma Version
python desktop_test_plasma.py

# GNOME/GTK4 Version
python desktop_test.py
```

## 📦 Installation

### Voraussetzungen

- CachyOS (oder Arch Linux mit CachyOS-Kernel)
- Python 3.11+
- systemd
- polkit (für Berechtigungen)

**Für KDE Plasma (empfohlen):**
- PyQt6

**Für GNOME:**
- GTK4
- libadwaita
- python-gobject

### Schnellinstallation

git clone https://github.com/Goitonthefloor/cachyos-service-manager.git
cd cachyos-service-manager
pip install -e .


Aus AUR installieren 

```bash
# mit  yay
yay -S cachyos-service-manager

# mit paru
paru -S cachyos-service-manager
```

Verwendung
Nach der Installation kannst du die Anwendung starten:

Qt6 Version:

bash
cachyos-service-manager-qt
GTK4 Version:

bash
cachyos-service-manager-gtk
Oder finde es im Anwendungsmenü unter System → CachyOS Service Manager

Features im Überblick:**

1. **Alle Services anzeigen:**
   - Automatisches Laden aller systemd Services
   - Status-Indikatoren: 🟢 Aktiv, 🟡 Inaktiv, 🔴 Fehler
   - Beschreibung jedes Services
   - Enabled/Disabled Status

2. **Suchen & Filtern:**
   - 🔍 Suchleiste: Suche nach Name oder Beschreibung
   - Filter-Dropdown: All, Active, Inactive, Failed, Enabled
   - Checkbox: "Show Inactive" zum Ein-/Ausblenden inaktiver Services

3. **Service-Aktionen:**
   - ▶️ **Start** - Service starten
   - ⏹ **Stop** - Service stoppen
   - ⟳ **Restart** - Service neu starten
   - **Enable/Disable** - Autostart aktivieren/deaktivieren
   - 📜 **Logs** - Service-Logs anzeigen (200 Zeilen)

4. **Statistik-Dashboard:**
   - Total: Gesamtzahl der Services
   - Active: Anzahl aktiver Services
   - Inactive: Anzahl inaktiver Services
   - Failed: Anzahl fehlerhafter Services
   - Enabled: Anzahl beim Boot aktivierter Services

5. **Log-Viewer:**
   - Separater Tab für Service-Logs
   - 200 Zeilen Historie
   - Monospace-Font für bessere Lesbarkeit

### 📦 Service Groups verwalten

#### Im GUI:

1. **Neue Gruppe erstellen:**
   - Klicke auf "+ New Group"
   - Gib Name, Beschreibung und Icon ein
   - Wähle Farbe (optional)
   - Wähle Services aus der Liste
   - Klicke "Create" / "OK"

2. **Gruppen-Aktionen:**
   - **▶ Start All** - Alle Services der Gruppe starten
   - **⏹ Stop All** - Alle Services der Gruppe stoppen
   - **⟳ Restart All** - Alle Services der Gruppe neu starten

3. **Gruppen ein-/ausklappen:**
   - Klicke auf den Gruppennamen zum Ein-/Ausklappen
   - Status-Anzeige jedes einzelnen Services in der Gruppe

### 🎯 Service Groups - Vordefinierte Templates

1. 🌍 **Web Services** - nginx, apache2, php-fpm
2. 🗄️ **Database Services** - postgresql, mysql, redis, mongodb
3. 🛠️ **Development** - docker, containerd, sshd
4. 🌐 **Network Services** - NetworkManager, systemd-resolved, avahi-daemon
5. 🖥️ **Desktop Services** - bluetooth, cups, pulseaudio
6. ⚙️ **System Core** - systemd-journald, systemd-udevd, dbus

### 💡 Anwendungsbeispiele

**Web-Development Stack:**
```
Gruppe "Web Stack":
  ▶️ nginx.service
  ▶️ postgresql.service  
  ▶️ redis.service
  ▶️ php-fpm.service
  
→ Mit einem Klick: Gesamter Stack starten/stoppen
```

**Docker Development:**
```
Gruppe "Docker Dev":
  ▶️ docker.service
  ▶️ containerd.service
  ▶️ sshd.service
  
→ Restart All: Komplette Dev-Umgebung neu starten
```

### 🖥️ CLI-Befehle (in Entwicklung)

```bash
# Service-Status anzeigen
cachy-services status nginx

# Service starten/stoppen
cachy-services start nginx
cachy-services stop nginx
cachy-services restart nginx

# Alle Services auflisten
cachy-services list --all

# Logs anzeigen
cachy-services logs nginx --follow

# Service aktivieren/deaktivieren (autostart)
cachy-services enable nginx
cachy-services disable nginx

# Gruppen verwalten
cachy-services group create "Web Stack" nginx postgresql redis
cachy-services group start "Web Stack"
cachy-services group stop "Web Stack"
cachy-services group list
```

## 🏗️ Architektur

```
cachyos-service-manager/
├── src/
│   ├── core/              # Kern-Funktionalität
│   │   ├── systemd.py     # systemd API Wrapper
│   │   ├── service.py     # Service-Klassen
│   │   ├── service_manager.py # Vollständiger Service Manager
│   │   ├── service_group.py # Service-Gruppen Management
│   │   └── monitor.py     # Monitoring-Engine
│   ├── gui/               # GUI-Komponenten
│   │   ├── main_window.py # Hauptfenster
│   │   ├── service_view.py# Service-Liste
│   │   └── log_viewer.py  # Log-Anzeige
│   ├── cli/               # CLI-Interface
│   │   ├── commands.py    # CLI-Befehle
│   │   └── formatter.py   # Ausgabe-Formatierung
│   └── utils/             # Hilfsfunktionen
│       ├── config.py      # Konfiguration
│       └── logger.py      # Logging
├── full_service_manager_plasma.py # Vollständiger Manager (Qt6)
├── full_service_manager_gtk.py    # Vollständiger Manager (GTK4)
├── desktop_test_plasma_groups.py  # Gruppen-Manager (Qt6)
├── desktop_test_groups.py         # Gruppen-Manager (GTK4)
├── tests/                 # Unit & Integration Tests
├── docs/                  # Dokumentation
└── README.md             # Diese Datei
```

## 📊 Verfügbare Programme

| Datei | UI | Features | Verwendung |
|-------|-----|----------|------------|
| `full_service_manager_plasma.py` | Qt6/KDE | **Alle Services + Volle Kontrolle** | **Empfohlen für tägliche Nutzung** |
| `full_service_manager_gtk.py` | GTK4/GNOME | **Alle Services + Volle Kontrolle** | **Empfohlen für GNOME** |
| `desktop_test_plasma_groups.py` | Qt6/KDE | Service Groups | Gruppen-Verwaltung |
| `desktop_test_groups.py` | GTK4/GNOME | Service Groups | Gruppen-Verwaltung |
| `desktop_test_plasma.py` | Qt6/KDE | Basic Test | Entwicklung |
| `desktop_test.py` | GTK4/GNOME | Basic Test | Entwicklung |

## 📚 API-Dokumentation

### ServiceManager Klasse (NEU!)

```python
from cachyos_service_manager.core.service_manager import ServiceManager, ServiceType

manager = ServiceManager()

# Alle Services auflisten
services = manager.list_all_services(
    service_type=ServiceType.SERVICE,
    show_inactive=True
)

# Service-Status abrufen
service_info = manager.get_service_status('nginx')

# Service-Aktionen
success, msg = manager.start_service('nginx')
success, msg = manager.stop_service('nginx')
success, msg = manager.restart_service('nginx')
success, msg = manager.enable_service('nginx')
success, msg = manager.disable_service('nginx')

# Logs abrufen
logs = manager.get_service_logs('nginx', lines=100)

# Services suchen
filtered = manager.search_services('docker', services)

# Statistiken
stats = manager.get_stats(services)
# Returns: {'total': 150, 'active': 45, 'inactive': 100, 'failed': 5, 'enabled': 50}
```

### ServiceGroupManager Klasse

```python
from cachyos_service_manager.core.service_group import ServiceGroupManager, GroupAction

manager = ServiceGroupManager()

# Gruppe erstellen
group = manager.create_group(
    name="Web Stack",
    description="Development web stack",
    services=["nginx.service", "postgresql.service"],
    color="#27ae60",
    icon="🌍"
)

# Alle Gruppen auflisten
groups = manager.list_groups()

# Gruppe abrufen
group = manager.get_group("Web Stack")

# Vordefinierte Templates
templates = manager.get_predefined_groups()
```

Weitere Details in der [API-Dokumentation](docs/API.md).

## 🔧 Konfiguration

Die Hauptkonfiguration befindet sich in:
```
~/.config/cachyos-service-manager/
├── config.yaml          # Allgemeine Einstellungen
└── groups.json          # Service-Gruppen Definitionen
```

### Beispiel-Konfiguration (`config.yaml`)

```yaml
general:
  theme: dark
  auto_refresh: true
  refresh_interval: 30  # Sekunden
  
groups:
  enable_groups: true
  auto_load_templates: true
  default_color: "#3daee9"
  
monitoring:
  enable_cpu_monitoring: true
  enable_memory_monitoring: true
  history_length: 300  # Datenpunkte

cli:
  color_output: true
  verbose: false
  
security:
  require_sudo: true
  confirm_critical_actions: true
```

## 🛠️ Entwicklung

### Entwicklungsumgebung einrichten

```bash
# Repository klonen
git clone https://github.com/Goitonthefloor/cachyos-service-manager.git
cd cachyos-service-manager

# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Tests ausführen
pytest tests/

# Code-Qualität prüfen
ruff check src/
mypy src/
```

### Technologie-Stack

- **Backend**: Python 3.11+
- **GUI**: Qt6/PyQt6 (KDE Plasma) + GTK4/Adwaita (GNOME)
- **CLI**: Click + Rich
- **systemd-Integration**: python-systemd, dbus-python
- **Tests**: pytest
- **Code-Qualität**: ruff, mypy, black

## 🤝 Mitwirken

Beiträge sind willkommen! Bitte beachte:

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

### Richtlinien

- Code-Style: PEP 8
- Commit-Messages: Conventional Commits
- Tests für neue Features erforderlich
- Dokumentation aktualisieren

## 📄 Lizenz

Dieses Projekt ist unter der GPL-3.0 Lizenz lizenziert. Siehe [LICENSE](LICENSE) für Details.

## 🙏 Danksagungen

- [CachyOS Team](https://cachyos.org) - Für die großartige Distribution
- [systemd Project](https://systemd.io) - Für den Service Manager
- [KDE Project](https://kde.org) - Für das wunderbare Plasma Desktop Environment
- [GNOME Project](https://gnome.org) - Für GTK4 und Adwaita
- Alle Contributors und Tester

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Goitonthefloor/cachyos-service-manager/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Goitonthefloor/cachyos-service-manager/discussions)
- **CachyOS Forum**: [forum.cachyos.org](https://forum.cachyos.org)
- **Discord**: [CachyOS Discord](https://discord.gg/cachyos)

## 🗺️ Roadmap

- [x] Basis-CLI-Funktionalität
- [x] systemd-Integration
- [x] Desktop Test GUI (KDE Plasma & GNOME)
- [x] KDE Plasma Breeze Theme Support
- [x] **Service Groups Feature**
- [x] **Qt6 Groups GUI**
- [x] **GTK4 Groups GUI**
- [x] **Vordefinierte Gruppen-Templates**
- [x] **Vollständiger Service Manager (alle Services)**
- [x] **Service-Aktionen (Start/Stop/Restart/Enable/Disable)**
- [x] **Suche & Filter-Funktionalität**
- [x] **Log-Viewer Integration**
- [x] **Statistik-Dashboard**
- [x] **Qt6 Full Manager GUI**
- [x] **GTK4 Full Manager GUI**
- [ ] CLI Groups Support
- [ ] Erweiterte Monitoring-Features
- [ ] Service-Abhängigkeitsvisualisierung
- [ ] AUR-Package
- [ ] Timer-Verwaltung
- [ ] Socket-Verwaltung
- [ ] Backup/Restore von Service-Konfigurationen
- [ ] Performance-Profiling
- [ ] Multi-Language Support
- [ ] Import/Export von Gruppen
- [ ] Systemd Unit Editor

---

<div align="center">

**Entwickelt mit ❤️ für die CachyOS-Community**

[Website](https://cachyos.org) · [GitHub](https://github.com/CachyOS) · [Forum](https://forum.cachyos.org)

</div>

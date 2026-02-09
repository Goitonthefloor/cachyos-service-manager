# CachyOS Service Manager

<div align="center">

![CSM Logo](https://user-gen-media-assets.s3.amazonaws.com/seedream_images/7a5e69cb-bffe-410b-80ca-4e9510e0efec.png)

# CSM - CachyOS Service Manager

**A modern, efficient service management tool for CachyOS**

Systemd integration · GUI & CLI · Real-time monitoring · **Service Groups**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![CachyOS](https://img.shields.io/badge/CachyOS-Optimized-teal)](https://cachyos.org)
[![KDE Plasma](https://img.shields.io/badge/KDE-Plasma-1d99f3)](https://kde.org)
[![GTK4](https://img.shields.io/badge/GTK-4.0-4a90d9)](https://gtk.org)

</div>

## 📋 Übersicht

CachyOS Service Manager ist ein leistungsstarkes Werkzeug zur Verwaltung von systemd-Services unter CachyOS. Es bietet sowohl eine grafische Benutzeroberfläche als auch eine CLI für die effiziente Verwaltung von Systemdiensten.

### ✨ Features

- 🎯 **Intuitive Service-Verwaltung** - Start, Stop, Restart und Status-Abfrage von Services
- 📦 **Service-Gruppen** - Organisiere Services in Gruppen und steuere sie gemeinsam
- 📊 **Echtzeit-Monitoring** - Live-Überwachung von Service-Status und Ressourcenverbrauch
- 🔍 **Log-Analyse** - Integrierte Journal-Log-Anzeige mit Filteroptionen
- ⚙️ **Service-Konfiguration** - Bearbeitung von Service-Dateien mit Syntax-Highlighting
- 🚀 **Performance-Optimierung** - Ressourcen-Limits und CPU/Memory-Management
- 🔐 **Sicherheit** - Systemd-Hardening-Optionen und Sandbox-Konfiguration
- 🎨 **Dual UI** - KDE Plasma (Qt6) & GNOME (GTK4) Unterstützung
- 📦 **Dependency-Management** - Visualisierung von Service-Abhängigkeiten

## 🎯 Service Groups - NEU!

### Was sind Service Groups?

Service Groups ermöglichen es dir, mehrere zusammenhängende Services zu organisieren und gemeinsam zu verwalten:

- 📦 **Gruppierung** - Fasse logisch zusammengehörige Services zusammen
- ▶️ **Gruppen-Aktionen** - Starte, stoppe oder restarte alle Services einer Gruppe mit einem Klick
- 🎨 **Visuelle Organisation** - Farbcodierung und Icons für bessere Übersicht
- 💾 **Persistent** - Gruppen werden automatisch gespeichert
- 📋 **Vordefinierte Templates** - 6 vorgefertigte Gruppen für häufige Szenarien

### Vordefinierte Gruppen-Templates

1. 🌍 **Web Services** - nginx, apache2, php-fpm
2. 🗄️ **Database Services** - postgresql, mysql, redis, mongodb
3. 🛠️ **Development** - docker, containerd, sshd
4. 🌐 **Network Services** - NetworkManager, systemd-resolved, avahi-daemon
5. 🖥️ **Desktop Services** - bluetooth, cups, pulseaudio
6. ⚙️ **System Core** - systemd-journald, systemd-udevd, dbus

### Anwendungsbeispiele

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

## 🏗️ Architektur

```
cachyos-service-manager/
├── src/
│   ├── core/              # Kern-Funktionalität
│   │   ├── systemd.py     # systemd API Wrapper
│   │   ├── service.py     # Service-Klassen
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
├── tests/                 # Unit & Integration Tests
├── docs/                  # Dokumentation
├── config/                # Konfigurationsdateien
└── scripts/               # Build & Install Scripts
```

## 🚀 Installation

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

```bash
# Repository klonen
git clone https://github.com/Goitonthefloor/cachyos-service-manager.git
cd cachyos-service-manager

# Für KDE Plasma (empfohlen für CachyOS)
sudo pacman -S python python-pyqt6 polkit

# Oder für GNOME
sudo pacman -S python python-gobject gtk4 libadwaita polkit
```

### Aus AUR installieren (geplant)

```bash
yay -S cachyos-service-manager
```

## 💻 Verwendung

### 🎨 Desktop GUI

#### Basis-Version (einzelne Services)

```bash
# KDE Plasma Version
python desktop_test_plasma.py

# GNOME/GTK4 Version
python desktop_test.py
```

#### Service Groups Version (empfohlen)

```bash
# KDE Plasma mit Service Groups
python desktop_test_plasma_groups.py

# GNOME/GTK4 mit Service Groups
python desktop_test_groups.py
```

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

#### Konfigurationsdatei:

Gruppen werden automatisch gespeichert in:
```
~/.config/cachyos-service-manager/groups.json
```

Beispiel `groups.json`:
```json
{
  "groups": [
    {
      "name": "Web Stack",
      "description": "Complete web development stack",
      "services": [
        "nginx.service",
        "postgresql.service",
        "redis.service"
      ],
      "color": "#27ae60",
      "icon": "🌍",
      "auto_start_order": true
    }
  ]
}
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

# Service-Abhängigkeiten anzeigen
cachy-services deps nginx

# Gruppen verwalten
cachy-services group create "Web Stack" nginx postgresql redis
cachy-services group start "Web Stack"
cachy-services group stop "Web Stack"
cachy-services group list
```

## 📊 Screenshots

### KDE Plasma Version mit Service Groups
![Plasma Groups UI](docs/screenshots/plasma-groups.png)
*Service-Gruppen mit Breeze Dark Theme und Farbcodierung*

### GNOME Version mit Service Groups
![GTK Groups UI](docs/screenshots/gtk-groups.png)
*Service-Gruppen mit Adwaita Theme und Expandern*

### Basis-Version
![Plasma UI](docs/screenshots/plasma-main.png)
*Einzelne Service-Verwaltung*

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
  refresh_interval: 2  # Sekunden
  
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

### Test-Versionen

| Datei | UI | Features | Zweck |
|-------|-----|----------|-------|
| `desktop_test_plasma.py` | Qt6/KDE | Basis-Service-Management | KDE Test |
| `desktop_test.py` | GTK4/GNOME | Basis-Service-Management | GNOME Test |
| `desktop_test_plasma_groups.py` | Qt6/KDE | **Service Groups** | KDE Groups Test |
| `desktop_test_groups.py` | GTK4/GNOME | **Service Groups** | GNOME Groups Test |

## 📚 API-Dokumentation

### SystemdManager Klasse

```python
from cachyos_service_manager.core import SystemdManager

manager = SystemdManager()

# Service-Status abrufen
status = manager.get_service_status('nginx')

# Service starten
manager.start_service('nginx')

# Logs abrufen
logs = manager.get_logs('nginx', lines=100)

# Ressourcen-Limits setzen
manager.set_resource_limits('nginx', cpu_quota='50%', memory_limit='512M')
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
- [ ] Vollständige GUI-Implementierung
- [ ] CLI Groups Support
- [ ] Echtzeit-Monitoring
- [ ] Service-Abhängigkeitsvisualisierung
- [ ] AUR-Package
- [ ] Timer-Verwaltung
- [ ] Socket-Verwaltung
- [ ] Backup/Restore von Service-Konfigurationen
- [ ] Performance-Profiling
- [ ] Multi-Language Support
- [ ] Import/Export von Gruppen

---

<div align="center">

**Entwickelt mit ❤️ für die CachyOS-Community**

[Website](https://cachyos.org) · [GitHub](https://github.com/CachyOS) · [Forum](https://forum.cachyos.org)

</div>
# CachyOS Service Manager

<div align="center">

![CSM Logo](https://user-gen-media-assets.s3.amazonaws.com/seedream_images/7a5e69cb-bffe-410b-80ca-4e9510e0efec.png)

# CSM - CachyOS Service Manager

**A modern, efficient service management tool for CachyOS**

Systemd integration · GUI & CLI · Real-time monitoring

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![CachyOS](https://img.shields.io/badge/CachyOS-Optimized-teal)](https://cachyos.org)
[![KDE Plasma](https://img.shields.io/badge/KDE-Plasma-1d99f3)](https://kde.org)

</div>

## 📋 Übersicht

CachyOS Service Manager ist ein leistungsstarkes Werkzeug zur Verwaltung von systemd-Services unter CachyOS. Es bietet sowohl eine grafische Benutzeroberfläche als auch eine CLI für die effiziente Verwaltung von Systemdiensten.

### ✨ Features

- 🎯 **Intuitive Service-Verwaltung** - Start, Stop, Restart und Status-Abfrage von Services
- 📊 **Echtzeit-Monitoring** - Live-Überwachung von Service-Status und Ressourcenverbrauch
- 🔍 **Log-Analyse** - Integrierte Journal-Log-Anzeige mit Filteroptionen
- ⚙️ **Service-Konfiguration** - Bearbeitung von Service-Dateien mit Syntax-Highlighting
- 🚀 **Performance-Optimierung** - Ressourcen-Limits und CPU/Memory-Management
- 🔐 **Sicherheit** - Systemd-Hardening-Optionen und Sandbox-Konfiguration
- 🎨 **Dual UI** - KDE Plasma (Qt6) & GNOME (GTK4) Unterstützung
- 📦 **Dependency-Management** - Visualisierung von Service-Abhängigkeiten

## 🏗️ Architektur

```
cachyos-service-manager/
├── src/
│   ├── core/              # Kern-Funktionalität
│   │   ├── systemd.py     # systemd API Wrapper
│   │   ├── service.py     # Service-Klassen
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
- **Qt6/PyQt6** (für KDE Plasma GUI - empfohlen) oder GTK4 (für GNOME)

### Aus AUR installieren (geplant)

```bash
yay -S cachyos-service-manager
```

### Aus Quellen installieren

```bash
git clone https://github.com/Goitonthefloor/cachyos-service-manager.git
cd cachyos-service-manager

# Für KDE Plasma (empfohlen für CachyOS)
sudo pacman -S python python-pyqt6 polkit
python desktop_test_plasma.py

# Oder für GNOME
sudo pacman -S python python-gobject gtk4 libadwaita polkit
python desktop_test.py
```

## 💻 Verwendung

### Desktop Test

```bash
# KDE Plasma Version (empfohlen)
python desktop_test_plasma.py

# GNOME Version
python desktop_test.py
```

### CLI-Befehle (in Entwicklung)

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

# Ressourcen-Limits setzen
cachy-services limit nginx --cpu 50 --memory 512M
```

## 📊 Screenshots

### KDE Plasma Version
![Plasma UI](docs/screenshots/plasma-main.png)
*Service-Übersicht mit Breeze Dark Theme*

### GNOME Version
![GTK UI](docs/screenshots/gnome-main.png)
*Service-Übersicht mit Adwaita Theme*

## 🔧 Konfiguration

Die Hauptkonfiguration befindet sich in:
```
~/.config/cachyos-service-manager/config.yaml
```

### Beispiel-Konfiguration

```yaml
general:
  theme: dark
  auto_refresh: true
  refresh_interval: 2  # Sekunden
  
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
- [ ] Vollständige GUI-Implementierung
- [ ] Echtzeit-Monitoring
- [ ] Service-Abhängigkeitsvisualisierung
- [ ] AUR-Package
- [ ] Timer-Verwaltung
- [ ] Socket-Verwaltung
- [ ] Backup/Restore von Service-Konfigurationen
- [ ] Performance-Profiling
- [ ] Multi-Language Support

---

<div align="center">

**Entwickelt mit ❤️ für die CachyOS-Community**

[Website](https://cachyos.org) · [GitHub](https://github.com/CachyOS) · [Forum](https://forum.cachyos.org)

</div>
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
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-34%20passing-brightgreen)](tests/)

</div>

## 📋 Übersicht

CachyOS Service Manager ist ein leistungsstarkes Werkzeug zur Verwaltung von systemd-Services unter CachyOS. Es bietet sowohl eine grafische Benutzeroberfläche (Qt6 für KDE Plasma, GTK4 für GNOME) als auch eine vollständige CLI für die effiziente Verwaltung von Systemdiensten.

### ✨ Features

- 🎯 **Vollständige Service-Verwaltung** - Zeige ALLE systemd Services an und steuere sie
- ⚡ **Service-Aktionen** - Start, Stop, Restart, Enable, Disable für jeden Service
- 📦 **Service-Gruppen** - Organisiere Services in Gruppen und steuere sie gemeinsam
- 🔍 **Suche & Filter** - Finde Services schnell mit Suchfunktion und Filtern
- 📊 **Echtzeit-Monitoring** - Live-Überwachung von CPU/RAM pro Service (alle 5s)
- 📜 **Log-Viewer** - Integrierte Journal-Log-Anzeige mit 200 Zeilen Historie
- 📈 **Statistik-Dashboard** - Übersicht über aktive, inaktive und fehlerhafte Services
- ⚙️ **Service-Konfiguration** - Detaillierte Service-Informationen (PID, Memory, CPU)
- 🎨 **Dual UI** - KDE Plasma (Qt6) & GNOME (GTK4) Unterstützung
- 🔄 **Auto-Refresh** - Automatische Service-Liste Aktualisierung aller 30s
- 🔐 **Sicherheit** - Polkit-Integration für Berechtigungen
- ⚡ **Performance** - Intelligentes Caching (2s TTL), Batch-PID-Fetching, QTableWidgetItem-Reuse
- 📝 **Strukturiertes Logging** - Ersetzt alle print()-Statements
- ✅ **34 Unit Tests** - Vollständige Testabdeckung der Kernfunktionalität

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
git clone https://github.com/Goitonthefloor/cachyos-service-manager.git
cd cachyos-service-manager
pip install -e .
```

### Aus AUR installieren

**Yay**
```bash
yay -S cachyos-service-manager
```

**Paru**
```bash
paru -S cachyos-service-manager
```

### Verwendung

Nach der Installation kannst du die Anwendung starten:

**Qt6 Version (KDE Plasma):**
```bash
cachy-service-manager
# oder
cachy-service-manager-qt
```

**GTK4 Version (GNOME):**
```bash
cachy-service-manager-gtk
```

**CLI:**
```bash
cachy-services --help
```

Oder finde es im Anwendungsmenü unter **System → CachyOS Service Manager**

## 🖥️ GUI-Features im Detail

### 1. Alle Services anzeigen
- Automatisches Laden aller systemd Services
- Status-Indikatoren: 🟢 Aktiv, 🟡 Inaktiv, 🔴 Fehler
- Beschreibung jedes Services
- Enabled/Disabled Status

### 2. Suchen & Filtern
- 🔍 Suchleiste: Suche nach Name oder Beschreibung
- Filter-Dropdown: All, Active, Inactive, Failed, Enabled
- Checkbox: "Show Inactive" zum Ein-/Ausblenden inaktiver Services

### 3. Service-Aktionen (pro Service)
- ▶️ **Start** - Service starten
- ⏹ **Stop** - Service stoppen
- ⟳ **Restart** - Service neu starten
- **Enable/Disable** - Autostart aktivieren/deaktivieren
- 📜 **Logs** - Service-Logs anzeigen (200 Zeilen)

### 4. Echtzeit-Ressourcen-Monitoring
- **CPU %** pro Service (Farbcodiert: 🟢 <20%, 🟡 20-50%, 🔴 >50%)
- **RAM MB** pro Service (Farbcodiert: 🟢 <100MB, 🟡 100-500MB, 🔴 >500MB)
- Automatische Aktualisierung aller 5 Sekunden für sichtbare Services
- Batch-Abfrage aller PIDs in **einem** systemctl-Aufruf

### 5. Statistik-Dashboard
- **Total**: Gesamtzahl der Services
- **Active**: Anzahl aktiver Services
- **Inactive**: Anzahl inaktiver Services
- **Failed**: Anzahl fehlerhafter Services
- **Enabled**: Anzahl beim Boot aktivierter Services

### 6. Log-Viewer
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

#### 🎯 Vordefinierte Templates (aus `config/group_templates.json`)
1. 🌍 **Web Services** - nginx, apache2, php-fpm
2. 🗄️ **Database Services** - postgresql, mysql, redis, mongodb
3. 🛠️ **Development** - docker, containerd, sshd
4. 🌐 **Network Services** - NetworkManager, systemd-resolved, avahi-daemon
5. 🖥️ **Desktop Services** - bluetooth, cups, pulseaudio
6. ⚙️ **System Core** - systemd-journald, systemd-udevd, dbus

**Eigene Templates:** Erstelle `~/.config/cachyos-service-manager/group_templates.json` für benutzerdefinierte Vorlagen.

#### 💡 Anwendungsbeispiele

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

## ⌨️ CLI-Befehle

```bash
# Version anzeigen
cachy-services --version

# Service-Status anzeigen
cachy-services status nginx

# Service starten/stoppen
cachy-services start nginx
cachy-services stop nginx
cachy-services restart nginx

# Alle Services auflisten
cachy-services list --all

# Nur aktive Services
cachy-services list

# Nach Typ filtern
cachy-services list --type timer
cachy-services list --type socket

# Logs anzeigen
cachy-services logs nginx
cachy-services logs nginx --lines 100

# Service aktivieren/deaktivieren (autostart)
cachy-services enable nginx
cachy-services disable nginx

# Gruppen verwalten (in Entwicklung)
cachy-services group create "Web Stack" nginx postgresql redis
cachy-services group start "Web Stack"
cachy-services group stop "Web Stack"
cachy-services group list
```

## 🏗️ Architektur

```
cachyos-service-manager/
├── config/
│   └── group_templates.json      # Externe Gruppen-Templates
├── src/
│   ├── cachyos_service_manager/
│   │   ├── gui/                  # Qt6 GUI (KDE Plasma)
│   │   │   └── main.py           # Hauptfenster mit Resource Monitoring
│   │   └── cli/
│   │       └── main.py           # Click-basierte CLI
│   ├── core/                     # Kern-Funktionalität
│   │   ├── systemd.py            # Async systemd D-Bus API Wrapper
│   │   ├── service.py            # Service Dataclasses & ServiceState Enum
│   │   ├── service_manager.py    # Sync ServiceManager (subprocess-based)
│   │   ├── service_group.py      # ServiceGroup & ServiceGroupManager
│   │   ├── resource_monitor.py   # CPU/RAM Monitoring (psutil + batch PID)
│   │   ├── monitor.py            # Async MonitoringEngine (D-Bus)
│   │   └── __init__.py
│   ├── cli/                      # CLI-Modul (Legacy)
│   └── utils/                    # Hilfsfunktionen
├── tests/
│   └── test_core.py              # 34 Unit Tests
├── pyproject.toml                # Package-Konfiguration
├── requirements.txt              # Dependencies
└── README.md
```

## 📚 API-Dokumentation

### ServiceManager Klasse (Sync, subprocess-basiert)

```python
from core.service_manager import ServiceManager, ServiceType

manager = ServiceManager(
    timeout=5.0,           # Timeout für list/status Operationen
    action_timeout=10.0,   # Timeout für Start/Stop/Restart/Enable/Disable
    cache_ttl=2.0          # Cache TTL in Sekunden
)

# Alle Services auflisten (mit Caching!)
services = manager.list_all_services(
    service_type=ServiceType.SERVICE,
    show_inactive=True
)

# Service-Status abrufen (detailliert)
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

# Health Check
if manager.check_systemd_accessible():
    print("systemd ist erreichbar")
```

### ServiceGroupManager Klasse

```python
from core.service_group import ServiceGroupManager
from pathlib import Path

# Mit benutzerdefinierten Template-Datei
manager = ServiceGroupManager(
    config_path=Path("~/.config/cachyos-service-manager/groups.json"),
    templates_path=Path("config/group_templates.json")
)

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

# Vordefinierte Templates laden (aus JSON!)
templates = manager.get_predefined_groups()

# Gruppe aus Template erstellen
group = manager.create_group_from_template("Web Services")
```

### ResourceMonitor Klasse

```python
from core.resource_monitor import ResourceMonitor

monitor = ResourceMonitor()

# Einzelner Service
resources = monitor.get_service_resources("nginx.service")
# Returns: ServiceResources(cpu_percent=5.2, memory_mb=45.3, memory_percent=1.2, process_count=3)

# Mehrere Services (BATCH - 1 systemctl Aufruf!)
resources = monitor.get_multiple_resources([
    "nginx.service",
    "postgresql.service",
    "redis.service"
])
# Returns: Dict[str, ServiceResources]
```

## 🔧 Konfiguration

Die Hauptkonfiguration befindet sich in:
```
~/.config/cachyos-service-manager/
├── config.yaml          # Allgemeine Einstellungen (geplant)
├── groups.json          # Service-Gruppen Definitionen
└── group_templates.json # Benutzerdefinierte Templates (optional)
```

### Externe Templates (`config/group_templates.json`)

```json
{
  "templates": [
    {
      "name": "My Custom Stack",
      "description": "Mein Entwicklungssetup",
      "services": ["docker.service", "redis.service", "nginx.service"],
      "color": "#9b59b6",
      "icon": "🛠️"
    }
  ]
}
```

### Beispiel-Konfiguration (`config.yaml`) - Geplant

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
  resource_refresh_interval: 5  # Sekunden
  max_services_to_monitor: 10

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

# Package im Editiermodus installieren
pip install -e .

# Tests ausführen
pytest tests/ -v

# Code-Qualität prüfen
ruff check src/
mypy src/
```

### Tests

```bash
# Alle Tests
pytest tests/

# Mit Coverage
pytest tests/ --cov=core --cov-report=html

# Einzelnen Test
pytest tests/test_core.py::TestServiceManager::test_map_state -v
```

**Test-Ergebnisse:** 34 Tests passing ✅

### Technologie-Stack

| Kategorie | Technologie |
|-----------|-------------|
| **Backend** | Python 3.11+ |
| **GUI (KDE)** | Qt6/PyQt6 |
| **GUI (GNOME)** | GTK4/Adwaita |
| **CLI** | Click + Rich |
| **systemd (Sync)** | subprocess + systemctl |
| **systemd (Async)** | dbus-python |
| **Monitoring** | psutil |
| **Tests** | pytest + pytest-cov |
| **Code-Qualität** | ruff, mypy, black |
| **Packaging** | setuptools (src-layout) |

## 📊 Performance-Optimierungen (v0.2.2+)

| Optimierung | Vorher | Nachher |
|-------------|--------|---------|
| **CPU-Messung** | `cpu_percent(interval=0)` → immer 0% | Zwei-Sample-Methode → korrekte Werte |
| **PID-Abfrage** | N subprocess-Aufrufe | **1 Batch-Aufruf** für alle Services |
| **Service-Liste** | Immer frisch von systemd | **2s TTL Cache** |
| **GUI Tabellen-Update** | Neue QTableWidgetItems alle 5s | **Items wiederverwenden** (in-place update) |
| **Memory Leak** | MonitoringEngine sammelte stale Services | **cleanup_stale_services()** im Loop |

## 🤝 Mitwirken

Beiträge sind willkommen! Bitte beachte:

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

### Richtlinien

- **Code-Style:** PEP 8 (ruff)
- **Type Hints:** mypy strict mode
- **Commit-Messages:** Conventional Commits (`feat:`, `fix:`, `perf:`, `docs:`, etc.)
- **Tests:** Für neue Features erforderlich
- **Dokumentation:** README und Docstrings aktualisieren

## 📄 Lizenz

Dieses Projekt ist unter der **GPL-3.0-or-later** Lizenz lizenziert. Siehe [LICENSE](LICENSE) für Details.

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
- [x] systemd-Integration (Sync + Async)
- [x] Dual GUI (Qt6/KDE + GTK4/GNOME)
- [x] **Service Groups Feature** mit externen Templates
- [x] **Vollständiger Service Manager** (alle Services + volle Kontrolle)
- [x] **Echtzeit-Ressourcen-Monitoring** (CPU/RAM)
- [x] **Suche & Filter-Funktionalität**
- [x] **Log-Viewer Integration**
- [x] **Statistik-Dashboard**
- [x] **Performance-Optimierungen** (Caching, Batch, Reuse)
- [x] **Strukturiertes Logging**
- [x] **34 Unit Tests**
- [x] **AUR-Package**
- [ ] CLI Groups Support (vollständig)
- [ ] Service-Abhängigkeitsvisualisierung
- [ ] Timer-Verwaltung
- [ ] Socket-Verwaltung
- [ ] Backup/Restore von Service-Konfigurationen
- [ ] Multi-Language Support (i18n)
- [ ] Import/Export von Gruppen
- [ ] Systemd Unit Editor
- [ ] systemd-analyze Integration

---

<div align="center">

**Entwickelt mit ❤️ für die CachyOS-Community**

[Website](https://cachyos.org) · [GitHub](https://github.com/CachyOS) · [Forum](https://forum.cachyos.org)

</div>
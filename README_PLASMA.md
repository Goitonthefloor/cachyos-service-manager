# Desktop Test - CachyOS Service Manager (KDE Plasma Edition)

## Übersicht

KDE Plasma-styled Desktop-Test mit Qt6/PyQt6 für die Service-Management-Funktionalität.

## Features

✅ **KDE Plasma Design**
- Breeze Dark Theme
- Native KDE-Farbpalette
- Plasma-styled Buttons und Widgets
- Moderne Qt6-Oberfläche

✅ **Service-Verwaltung**
- Service-Liste mit Echtzeit-Status
- Start/Stop/Restart-Funktionen
- Farbcodierte Status-Indikatoren
- Intelligente Button-Aktivierung

✅ **Plasma-Features**
- Breeze-Farbschema (Grün/Rot/Blau)
- Toolbar mit Aktions-Buttons
- Status-Bar für Feedback
- Responsive Design

## Installation

### Voraussetzungen

```bash
# Arch Linux / CachyOS
sudo pacman -S python python-pyqt6 polkit
```

### Ausführen

```bash
# Im Repository-Verzeichnis
python desktop_test_plasma.py
```

Oder ausführbar machen:
```bash
chmod +x desktop_test_plasma.py
./desktop_test_plasma.py
```

## Design-System

### Breeze Dark Farbpalette

**Hintergrund:**
- Primary: `#232629` (Dark)
- Secondary: `#31363b` (Medium Dark)
- Elevated: `#3daee9` (Plasma Blue)

**Text:**
- Primary: `#eff0f1` (White)
- Secondary: `#bdc3c7` (Light Gray)

**Aktionsfarben:**
- Success/Active: `#27ae60` (Breeze Green)
- Danger/Stop: `#da4453` (Breeze Red)
- Info/Restart: `#3daee9` (Breeze Blue)
- Warning: `#f39c12` (Orange)

### UI-Komponenten

#### Service-Widget
```
┌─────────────────────────────────────────────┐
│ ServiceName.service              [Colored]  │
│ ● Status                                    │
│                   [▶ Start] [■ Stop] [⟳ Re] │
└─────────────────────────────────────────────┘
```

#### Header-Toolbar
```
┌─────────────────────────────────────────────┐
│ ⚙ CachyOS Service Manager  [🔄 Refresh] [ℹ] │
└─────────────────────────────────────────────┘
```

#### Status-Anzeige
- 🟢 **● Active** - Service läuft (grün)
- 🟡 **○ Inactive** - Service gestoppt (orange)
- 🔴 **✗ Failed** - Service fehlgeschlagen (rot)

## Vergleich: GTK vs Qt

### GTK4/Adwaita Version
- GNOME-Integration
- Adwaita-Widgets
- Native für GNOME Shell
- `desktop_test.py`

### Qt6/KDE Plasma Version
- KDE-Integration
- Breeze-Theme
- Native für KDE Plasma
- `desktop_test_plasma.py`

**Beide Versionen bieten identische Funktionalität!**

## Technische Details

### Architektur

```
QApplication
    ↓
MainWindow (QMainWindow)
    ├── Header (QFrame)
    │   ├── Title (QLabel)
    │   ├── Refresh Button
    │   └── About Button
    ├── Scroll Area (QScrollArea)
    │   └── Services Layout
    │       └── ServiceWidget (für jeden Service)
    │           ├── Info Layout
    │           │   ├── Name Label
    │           │   └── Status Label
    │           └── Button Layout
    │               ├── Start Button
    │               ├── Stop Button
    │               └── Restart Button
    └── StatusBar (QStatusBar)
```

### Threading & Signals

```python
class ServiceSignals(QObject):
    status_updated = pyqtSignal(str, str)
    action_completed = pyqtSignal(str, str, bool)
```

- Thread-sichere Kommunikation via Qt Signals
- Background-Threads für systemctl-Aufrufe
- Non-blocking GUI

### Styling-System

Inline Qt StyleSheets für Plasma-Look:

```python
button.setStyleSheet("""
    QPushButton {
        background-color: #27ae60;
        color: white;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #229954;
    }
""")
```

## Verwendung

### Services testen

1. **Service starten**: Klick auf "▶ Start" (grün)
2. **Service stoppen**: Klick auf "■ Stop" (rot)
3. **Service neu starten**: Klick auf "⟳ Restart" (blau)
4. **Alle aktualisieren**: Klick auf "🔄 Refresh" im Header

### Automatische Updates

- Alle 5 Sekunden automatische Status-Aktualisierung
- Manuell via Refresh-Button
- Nach jeder Aktion

## Anpassungen

### Service-Liste ändern

```python
self.test_services = [
    'dein-service.service',
    'weiterer-service.service',
]
```

### Farbschema anpassen

```python
# In apply_plasma_theme()
palette.setColor(QPalette.ColorRole.Highlight, QColor(61, 174, 233))
```

### Refresh-Intervall ändern

```python
# In start_auto_refresh()
self.refresh_timer.start(10000)  # 10 Sekunden
```

## Vorteile der Qt-Version

✅ **Native KDE-Integration**
- Folgt KDE Human Interface Guidelines
- Breeze-Theme automatisch
- System-Farbschema-Support

✅ **Performance**
- Qt6 ist hochperformant
- Effizientes Rendering
- Geringer Ressourcenverbrauch

✅ **Plattform-Übergreifend**
- Linux, Windows, macOS
- Konsistentes Design
- Native Look & Feel

✅ **Rich Widget-Set**
- Umfangreiche Qt-Widgets
- Flexible Layouts
- Einfache Anpassung

## Bekannte Einschränkungen

1. **Root-Rechte**: pkexec erforderlich für Service-Kontrolle
2. **Zeitverzögerung**: Status-Updates 1-2 Sekunden
3. **Feste Liste**: Services hardcoded (für Tests)

## Troubleshooting

### "No module named 'PyQt6'"
```bash
sudo pacman -S python-pyqt6
```

### "QApplication: invalid style override passed"
Normal - Qt verwendet Fallback-Style

### Design sieht nicht wie Plasma aus
```bash
# Breeze-Theme installieren
sudo pacman -S breeze breeze-icons
```

### Buttons reagieren nicht
- Stelle sicher, dass polkit installiert ist
- pkexec sollte nach Passwort fragen

## Nächste Schritte

Für die finale Version:
- [ ] KDE Frameworks Integration
- [ ] Native KConfig-Unterstützung
- [ ] KNotifications für Events
- [ ] Plasma-Applet/Widget
- [ ] System Tray Integration

## Vergleich der beiden Versionen

| Feature | GTK4/Adwaita | Qt6/Plasma |
|---------|--------------|------------|
| **Desktop** | GNOME | KDE Plasma |
| **Theme** | Adwaita | Breeze Dark |
| **Sprache** | Python + PyGObject | Python + PyQt6 |
| **Dateigröße** | ~250 Zeilen | ~400 Zeilen |
| **Performance** | Sehr gut | Exzellent |
| **Anpassbar** | Gut | Sehr gut |
| **Native Look** | GNOME | KDE |

## Empfehlung

**CachyOS verwendet KDE Plasma als Standard-Desktop:**
- ✅ Verwende `desktop_test_plasma.py` für natives KDE-Erlebnis
- ✅ Breeze-Theme passt perfekt zu CachyOS
- ✅ Qt6 ist schnell und effizient

**Für GNOME-Nutzer:**
- Verwende `desktop_test.py` (GTK4/Adwaita Version)

## Lizenz

GPL-3.0 - Siehe LICENSE-Datei

## Links

- [KDE Human Interface Guidelines](https://develop.kde.org/hig/)
- [Breeze Theme](https://github.com/KDE/breeze)
- [Qt6 Documentation](https://doc.qt.io/qt-6/)
- [PyQt6 Reference](https://www.riverbankcomputing.com/static/Docs/PyQt6/)

# CachyOS Service Manager - Architektur-Dokumentation

## Übersicht

Dieses Dokument beschreibt die technische Architektur des CachyOS Service Managers, ein modernes Tool zur Verwaltung von systemd-Services unter CachyOS/Arch Linux.

## Architektur-Prinzipien

### 1. Modulare Struktur
- **Separation of Concerns**: Klare Trennung zwischen GUI, CLI und Core-Logik
- **Dependency Injection**: Lose Kopplung zwischen Komponenten
- **Plugin-System**: Erweiterbarkeit durch Plugin-Architektur

### 2. Performance
- **Asynchrone Operationen**: Nicht-blockierende systemd-Interaktion
- **Caching**: Intelligentes Caching von Service-Status und Metadaten
- **Lazy Loading**: Ressourcen werden nur bei Bedarf geladen

### 3. Sicherheit
- **Privilege Separation**: Minimale Rechte für Operationen
- **Input Validation**: Strikte Validierung aller Eingaben
- **Audit Logging**: Protokollierung kritischer Aktionen

## System-Komponenten

### Core Layer

Die Core-Schicht bildet das Herzstück der Anwendung und kapselt die gesamte systemd-Interaktion.

#### SystemdManager
```python
class SystemdManager:
    """
    Zentrale Schnittstelle zu systemd über D-Bus.
    
    Verantwortlichkeiten:
    - systemd D-Bus API Wrapper
    - Service-Lifecycle-Management
    - Unit-Datei-Manipulation
    - Status-Überwachung
    """
    
    def __init__(self):
        self.bus = SystemBus()
        self.systemd = self.bus.get('org.freedesktop.systemd1')
        self.cache = ServiceCache()
    
    async def list_services(self) -> List[Service]:
        """Listet alle Services auf"""
        
    async def get_service(self, name: str) -> Service:
        """Ruft einen einzelnen Service ab"""
        
    async def start_service(self, name: str) -> bool:
        """Startet einen Service"""
        
    async def stop_service(self, name: str) -> bool:
        """Stoppt einen Service"""
```

#### Service Model
```python
@dataclass
class Service:
    """
    Repräsentiert einen systemd-Service.
    """
    name: str
    description: str
    state: ServiceState  # active, inactive, failed, etc.
    sub_state: str  # running, dead, exited, etc.
    load_state: str  # loaded, not-found, masked
    active_state: str
    
    # Resource Information
    memory_current: int
    cpu_usage: float
    
    # Configuration
    unit_file: Path
    enabled: bool
    preset: str
    
    # Dependencies
    requires: List[str]
    wants: List[str]
    before: List[str]
    after: List[str]
    
    # Runtime
    main_pid: Optional[int]
    control_pid: Optional[int]
    
    def is_active(self) -> bool:
        return self.state == ServiceState.ACTIVE
    
    def is_enabled(self) -> bool:
        return self.enabled
```

#### MonitoringEngine
```python
class MonitoringEngine:
    """
    Überwacht Service-Metriken in Echtzeit.
    
    Features:
    - CPU-Nutzung pro Service
    - Speicherverbrauch
    - I/O-Statistiken
    - Historische Daten
    """
    
    def __init__(self, interval: float = 2.0):
        self.interval = interval
        self.metrics_history = defaultdict(deque)
        
    async def start_monitoring(self, services: List[str]):
        """Startet Monitoring für angegebene Services"""
        
    async def get_current_metrics(self, service: str) -> Metrics:
        """Ruft aktuelle Metriken ab"""
        
    def get_history(self, service: str, duration: int) -> List[Metrics]:
        """Ruft historische Metriken ab"""
```

Siehe [vollständige Dokumentation](ARCHITECTURE.md) für weitere Details zu GUI Layer, CLI Layer, Datenfluss, Technologie-Entscheidungen, Performance-Optimierungen, Sicherheitskonzepten, Testing-Strategie, Deployment und Erweiterbarkeit.

---

**Version:** 1.0.0  
**Letztes Update:** Februar 2026  
**Autor:** Rolf Greger
# API Documentation

## SystemdManager

### Methods

#### `list_services() -> List[Service]`
Lists all available services.

#### `get_service(name: str) -> Service`
Retrieve information about a specific service.

#### `start_service(name: str) -> bool`
Start a service. Returns True on success.

#### `stop_service(name: str) -> bool`
Stop a service. Returns True on success.

#### `restart_service(name: str) -> bool`
Restart a service. Returns True on success.

#### `enable_service(name: str) -> bool`
Enable a service (autostart). Returns True on success.

#### `disable_service(name: str) -> bool`
Disable a service (no autostart). Returns True on success.

## Service Model

```python
@dataclass
class Service:
    name: str
    description: str
    state: ServiceState
    sub_state: str
    load_state: str
    active_state: str
    memory_current: int
    cpu_usage: float
    unit_file: Optional[Path]
    enabled: bool
    preset: str
    requires: List[str]
    wants: List[str]
    before: List[str]
    after: List[str]
    main_pid: Optional[int]
    control_pid: Optional[int]
```

## MonitoringEngine

### Methods

#### `start_monitoring(services: List[str])`
Start monitoring specified services.

#### `stop_monitoring()`
Stop monitoring.

#### `get_current_metrics(service: str) -> Metrics`
Get current metrics for a service.

#### `get_history(service: str, duration: int) -> List[Metrics]`
Get historical metrics for specified duration.
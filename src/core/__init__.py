"""Core functionality for CachyOS Service Manager."""

from .service import Service, ServiceState
from .service_manager import ServiceManager, ServiceType, ServiceInfo
from .i18n import _, set_language, get_language, init_i18n, I18nMixin

# Optional imports - may not be available on all platforms (e.g., Windows)
try:
    from .systemd import SystemdManager
except ImportError:
    SystemdManager = None

try:
    from .monitor import MonitoringEngine
except ImportError:
    MonitoringEngine = None

try:
    from .service_group import ServiceGroup, ServiceGroupManager
except ImportError:
    ServiceGroup = None
    ServiceGroupManager = None

__all__ = [
    'Service', 
    'ServiceState', 
    'ServiceManager', 
    'ServiceType', 
    'ServiceInfo',
    'SystemdManager', 
    'MonitoringEngine', 
    'ServiceGroup', 
    'ServiceGroupManager',
    # i18n
    '_', 'set_language', 'get_language', 'init_i18n', 'I18nMixin'
]
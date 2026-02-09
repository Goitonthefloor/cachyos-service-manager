"""Complete service manager with full systemd integration."""

import subprocess
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ServiceState(Enum):
    """Service states."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    ACTIVATING = "activating"
    DEACTIVATING = "deactivating"
    UNKNOWN = "unknown"


class ServiceType(Enum):
    """Service types."""
    SERVICE = "service"
    SOCKET = "socket"
    TIMER = "timer"
    TARGET = "target"
    PATH = "path"
    MOUNT = "mount"
    DEVICE = "device"


@dataclass
class ServiceInfo:
    """Information about a systemd service."""
    name: str
    display_name: str
    state: ServiceState
    enabled: bool
    description: str
    loaded: bool
    active_state: str
    sub_state: str
    pid: Optional[int] = None
    memory: Optional[str] = None
    cpu: Optional[str] = None
    
    @property
    def status_color(self) -> str:
        """Get color for status."""
        if self.state == ServiceState.ACTIVE:
            return "#26a269"  # Green
        elif self.state == ServiceState.INACTIVE:
            return "#f6d32d"  # Yellow
        elif self.state == ServiceState.FAILED:
            return "#c01c28"  # Red
        else:
            return "#9a9996"  # Gray


class ServiceManager:
    """Manager for systemd services."""
    
    def __init__(self):
        """Initialize service manager."""
        self._cache: Dict[str, ServiceInfo] = {}
        self._filter_type: Optional[ServiceType] = None
    
    def list_all_services(self, service_type: Optional[ServiceType] = None,
                          show_inactive: bool = True) -> List[ServiceInfo]:
        """List all systemd services.
        
        Args:
            service_type: Filter by service type
            show_inactive: Include inactive services
            
        Returns:
            List of ServiceInfo objects
        """
        try:
            # Get list of all units
            type_filter = service_type.value if service_type else "service"
            cmd = ['systemctl', 'list-units', f'--type={type_filter}', 
                   '--all' if show_inactive else '', '--no-pager', '--no-legend']
            cmd = [c for c in cmd if c]  # Remove empty strings
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                return []
            
            services = []
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                
                parts = line.split(None, 4)
                if len(parts) >= 4:
                    name = parts[0]
                    loaded = parts[1]
                    active = parts[2]
                    sub = parts[3]
                    desc = parts[4] if len(parts) > 4 else ""
                    
                    # Get enabled status
                    enabled = self._is_enabled(name)
                    
                    # Map state
                    state = self._map_state(active)
                    
                    service_info = ServiceInfo(
                        name=name,
                        display_name=name.replace('.service', ''),
                        state=state,
                        enabled=enabled,
                        description=desc,
                        loaded=loaded == "loaded",
                        active_state=active,
                        sub_state=sub
                    )
                    
                    services.append(service_info)
                    self._cache[name] = service_info
            
            return sorted(services, key=lambda s: s.display_name.lower())
            
        except Exception as e:
            print(f"Error listing services: {e}")
            return []
    
    def get_service_status(self, service_name: str) -> Optional[ServiceInfo]:
        """Get detailed status of a service.
        
        Args:
            service_name: Service name
            
        Returns:
            ServiceInfo or None
        """
        try:
            # Ensure .service suffix
            if not service_name.endswith('.service'):
                service_name += '.service'
            
            # Get status
            result = subprocess.run(
                ['systemctl', 'status', service_name],
                capture_output=True, text=True, timeout=2
            )
            
            # Get show output for more details
            show_result = subprocess.run(
                ['systemctl', 'show', service_name],
                capture_output=True, text=True, timeout=2
            )
            
            # Parse show output
            show_data = {}
            for line in show_result.stdout.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    show_data[key] = value
            
            state = self._map_state(show_data.get('ActiveState', 'unknown'))
            enabled = show_data.get('UnitFileState', 'disabled') in ['enabled', 'static']
            
            service_info = ServiceInfo(
                name=service_name,
                display_name=service_name.replace('.service', ''),
                state=state,
                enabled=enabled,
                description=show_data.get('Description', ''),
                loaded=show_data.get('LoadState', 'not-found') == 'loaded',
                active_state=show_data.get('ActiveState', 'unknown'),
                sub_state=show_data.get('SubState', 'unknown'),
                pid=int(show_data.get('MainPID', '0')) or None,
                memory=show_data.get('MemoryCurrent', None),
                cpu=show_data.get('CPUUsageNSec', None)
            )
            
            self._cache[service_name] = service_info
            return service_info
            
        except Exception as e:
            print(f"Error getting service status: {e}")
            return None
    
    def start_service(self, service_name: str) -> Tuple[bool, str]:
        """Start a service.
        
        Args:
            service_name: Service name
            
        Returns:
            Tuple of (success, message)
        """
        return self._execute_action(service_name, 'start')
    
    def stop_service(self, service_name: str) -> Tuple[bool, str]:
        """Stop a service.
        
        Args:
            service_name: Service name
            
        Returns:
            Tuple of (success, message)
        """
        return self._execute_action(service_name, 'stop')
    
    def restart_service(self, service_name: str) -> Tuple[bool, str]:
        """Restart a service.
        
        Args:
            service_name: Service name
            
        Returns:
            Tuple of (success, message)
        """
        return self._execute_action(service_name, 'restart')
    
    def enable_service(self, service_name: str) -> Tuple[bool, str]:
        """Enable a service (autostart).
        
        Args:
            service_name: Service name
            
        Returns:
            Tuple of (success, message)
        """
        return self._execute_action(service_name, 'enable')
    
    def disable_service(self, service_name: str) -> Tuple[bool, str]:
        """Disable a service (no autostart).
        
        Args:
            service_name: Service name
            
        Returns:
            Tuple of (success, message)
        """
        return self._execute_action(service_name, 'disable')
    
    def get_service_logs(self, service_name: str, lines: int = 100) -> str:
        """Get service logs.
        
        Args:
            service_name: Service name
            lines: Number of lines to retrieve
            
        Returns:
            Log content
        """
        try:
            if not service_name.endswith('.service'):
                service_name += '.service'
            
            result = subprocess.run(
                ['journalctl', '-u', service_name, '-n', str(lines), '--no-pager'],
                capture_output=True, text=True, timeout=5
            )
            
            return result.stdout
        except Exception as e:
            return f"Error retrieving logs: {e}"
    
    def search_services(self, query: str, services: List[ServiceInfo]) -> List[ServiceInfo]:
        """Search services by name or description.
        
        Args:
            query: Search query
            services: List of services to search
            
        Returns:
            Filtered list of services
        """
        query = query.lower()
        return [
            s for s in services
            if query in s.display_name.lower() or query in s.description.lower()
        ]
    
    def _execute_action(self, service_name: str, action: str) -> Tuple[bool, str]:
        """Execute systemctl action.
        
        Args:
            service_name: Service name
            action: Action (start, stop, restart, enable, disable)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not service_name.endswith('.service'):
                service_name += '.service'
            
            result = subprocess.run(
                ['pkexec', 'systemctl', action, service_name],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                return True, f"Successfully {action}ed {service_name}"
            else:
                return False, f"Failed to {action} {service_name}: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, f"Timeout executing {action} on {service_name}"
        except Exception as e:
            return False, f"Error: {e}"
    
    def _is_enabled(self, service_name: str) -> bool:
        """Check if service is enabled.
        
        Args:
            service_name: Service name
            
        Returns:
            True if enabled
        """
        try:
            result = subprocess.run(
                ['systemctl', 'is-enabled', service_name],
                capture_output=True, text=True, timeout=1
            )
            return result.stdout.strip() in ['enabled', 'static']
        except:
            return False
    
    def _map_state(self, state_str: str) -> ServiceState:
        """Map systemd state to ServiceState enum.
        
        Args:
            state_str: State string from systemd
            
        Returns:
            ServiceState enum value
        """
        state_map = {
            'active': ServiceState.ACTIVE,
            'inactive': ServiceState.INACTIVE,
            'failed': ServiceState.FAILED,
            'activating': ServiceState.ACTIVATING,
            'deactivating': ServiceState.DEACTIVATING,
        }
        return state_map.get(state_str.lower(), ServiceState.UNKNOWN)
    
    def get_stats(self, services: List[ServiceInfo]) -> Dict[str, int]:
        """Get statistics about services.
        
        Args:
            services: List of services
            
        Returns:
            Dictionary with statistics
        """
        return {
            'total': len(services),
            'active': sum(1 for s in services if s.state == ServiceState.ACTIVE),
            'inactive': sum(1 for s in services if s.state == ServiceState.INACTIVE),
            'failed': sum(1 for s in services if s.state == ServiceState.FAILED),
            'enabled': sum(1 for s in services if s.enabled)
        }

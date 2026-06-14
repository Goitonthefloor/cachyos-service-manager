"""Complete service manager with full systemd integration."""

import subprocess
import time
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .service import ServiceState

logger = logging.getLogger(__name__)


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

    DEFAULT_TIMEOUT = 5.0
    DEFAULT_ACTION_TIMEOUT = 10.0
    DEFAULT_CACHE_TTL = 2.0  # seconds

    def __init__(self, timeout: float = DEFAULT_TIMEOUT, action_timeout: float = DEFAULT_ACTION_TIMEOUT, cache_ttl: float = DEFAULT_CACHE_TTL):
        """Initialize service manager.

        Args:
            timeout: Timeout for list/status operations in seconds
            action_timeout: Timeout for start/stop/restart/enable/disable operations
            cache_ttl: Cache time-to-live for service listings in seconds
        """
        self._cache: Dict[str, ServiceInfo] = {}
        self._cache_timestamp = 0.0
        self._cache_ttl = cache_ttl
        self._filter_type: Optional[ServiceType] = None
        self._timeout = timeout
        self._action_timeout = action_timeout

    def list_all_services(self, service_type: Optional[ServiceType] = None,
                          show_inactive: bool = True) -> List[ServiceInfo]:
        """List all systemd services.

        Args:
            service_type: Filter by service type
            show_inactive: Include inactive services

        Returns:
            List of ServiceInfo objects
        """
        # Check cache first
        now = time.time()
        if now - self._cache_timestamp < self._cache_ttl and self._cache:
            logger.debug("Returning cached service list")
            return sorted(self._cache.values(), key=lambda s: s.display_name.lower())

        try:
            # Get list of all units
            type_filter = service_type.value if service_type else "service"
            cmd = ['systemctl', 'list-units', f'--type={type_filter}',
                   '--all' if show_inactive else '', '--no-pager', '--no-legend']
            cmd = [c for c in cmd if c]  # Remove empty strings

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self._timeout)

            if result.returncode != 0:
                logger.warning(f"systemctl list-units failed: {result.stderr}")
                return []

            # Batch fetch enabled states in ONE subprocess call instead of N+1
            enabled_map = self._get_all_enabled_states()

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

                    # Use batch lookup instead of per-service subprocess
                    enabled = enabled_map.get(name, False)

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

            self._cache_timestamp = now
            logger.debug(f"Loaded {len(services)} services from systemd")
            return sorted(services, key=lambda s: s.display_name.lower())

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout listing services after {self._timeout}s")
            return []
        except Exception as e:
            logger.error(f"Error listing services: {e}")
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
                capture_output=True, text=True, timeout=self._timeout
            )

            # Get show output for more details
            show_result = subprocess.run(
                ['systemctl', 'show', service_name],
                capture_output=True, text=True, timeout=self._timeout
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

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout getting status for {service_name} after {self._timeout}s")
            return None
        except Exception as e:
            logger.error(f"Error getting service status for {service_name}: {e}")
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
                capture_output=True, text=True, timeout=self._timeout
            )

            return result.stdout
        except Exception as e:
            logger.error(f"Error retrieving logs for {service_name}: {e}")
            return f"Error retrieving logs: {e}"

    def get_timer_status(self, timer_name: str) -> Optional[ServiceInfo]:
        """Get detailed status of a timer.

        Args:
            timer_name: Timer name (e.g., 'apt-daily.timer')

        Returns:
            ServiceInfo or None
        """
        try:
            if not timer_name.endswith('.timer'):
                timer_name += '.timer'

            show_result = subprocess.run(
                ['systemctl', 'show', timer_name],
                capture_output=True, text=True, timeout=self._timeout
            )

            show_data = {}
            for line in show_result.stdout.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    show_data[key] = value

            state = self._map_state(show_data.get('ActiveState', 'unknown'))
            enabled = show_data.get('UnitFileState', 'disabled') in ['enabled', 'static']

            service_info = ServiceInfo(
                name=timer_name,
                display_name=timer_name.replace('.timer', ''),
                state=state,
                enabled=enabled,
                description=show_data.get('Description', ''),
                loaded=show_data.get('LoadState', 'not-found') == 'loaded',
                active_state=show_data.get('ActiveState', 'unknown'),
                sub_state=show_data.get('SubState', 'unknown'),
                pid=None,
                memory=None,
                cpu=None
            )

            self._cache[timer_name] = service_info
            return service_info

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout getting timer status for {timer_name} after {self._timeout}s")
            return None
        except Exception as e:
            logger.error(f"Error getting timer status for {timer_name}: {e}")
            return None

    def get_socket_status(self, socket_name: str) -> Optional[ServiceInfo]:
        """Get detailed status of a socket.

        Args:
            socket_name: Socket name (e.g., 'docker.socket')

        Returns:
            ServiceInfo or None
        """
        try:
            if not socket_name.endswith('.socket'):
                socket_name += '.socket'

            show_result = subprocess.run(
                ['systemctl', 'show', socket_name],
                capture_output=True, text=True, timeout=self._timeout
            )

            show_data = {}
            for line in show_result.stdout.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    show_data[key] = value

            state = self._map_state(show_data.get('ActiveState', 'unknown'))
            enabled = show_data.get('UnitFileState', 'disabled') in ['enabled', 'static']

            service_info = ServiceInfo(
                name=socket_name,
                display_name=socket_name.replace('.socket', ''),
                state=state,
                enabled=enabled,
                description=show_data.get('Description', ''),
                loaded=show_data.get('LoadState', 'not-found') == 'loaded',
                active_state=show_data.get('ActiveState', 'unknown'),
                sub_state=show_data.get('SubState', 'unknown'),
                pid=None,
                memory=None,
                cpu=None
            )

            self._cache[socket_name] = service_info
            return service_info

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout getting socket status for {socket_name} after {self._timeout}s")
            return None
        except Exception as e:
            logger.error(f"Error getting socket status for {socket_name}: {e}")
            return None

    def list_timers(self, show_inactive: bool = True) -> List[ServiceInfo]:
        """List all systemd timers."""
        return self.list_all_services(service_type=ServiceType.TIMER, show_inactive=show_inactive)

    def list_sockets(self, show_inactive: bool = True) -> List[ServiceInfo]:
        """List all systemd sockets."""
        return self.list_all_services(service_type=ServiceType.SOCKET, show_inactive=show_inactive)

    def get_next_timer_activations(self) -> List[Dict[str, str]]:
        """Get next activation times for all timers."""
        try:
            result = subprocess.run(
                ['systemctl', 'list-timers', '--all', '--no-pager', '--no-legend'],
                capture_output=True, text=True, timeout=self._timeout
            )
            if result.returncode != 0:
                return []

            timers = []
            for line in result.stdout.strip().split('\n'):
                if not line.strip() or 'NEXT' in line:
                    continue
                parts = line.split()
                if len(parts) >= 5:
                    timers.append({
                        'next': parts[0],
                        'left': parts[1],
                        'last': parts[2],
                        'passed': parts[3],
                        'unit': parts[4],
                        'activates': parts[5] if len(parts) > 5 else ''
                    })
            return timers
        except Exception as e:
            logger.error(f"Error getting timer activations: {e}")
            return []

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
                capture_output=True, text=True, timeout=self._action_timeout
            )

            if result.returncode == 0:
                logger.info(f"Successfully {action}ed {service_name}")
                # Invalidate cache after successful action
                self._cache_timestamp = 0
                return True, f"Successfully {action}ed {service_name}"
            else:
                logger.warning(f"Failed to {action} {service_name}: {result.stderr}")
                return False, f"Failed to {action} {service_name}: {result.stderr}"

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout executing {action} on {service_name} after {self._action_timeout}s")
            return False, f"Timeout executing {action} on {service_name}"
        except Exception as e:
            logger.error(f"Error executing {action} on {service_name}: {e}")
            return False, f"Error: {e}"

    def _get_all_enabled_states(self) -> Dict[str, bool]:
        """Batch-fetch enabled states for all services in one subprocess call.

        Returns:
            Dictionary mapping service name -> enabled state
        """
        enabled_map: Dict[str, bool] = {}
        try:
            result = subprocess.run(
                ['systemctl', 'list-unit-files', '--type=service', '--no-pager', '--no-legend'],
                capture_output=True, text=True, timeout=self._timeout
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if not line.strip():
                        continue
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        state = parts[1]
                        enabled_map[name] = state in ('enabled', 'static')
        except Exception as e:
            logger.warning(f"Failed to fetch enabled states: {e}")
        return enabled_map

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
        except Exception:
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

    def check_systemd_accessible(self) -> bool:
        """Check if systemd is accessible.

        Returns:
            True if systemd is accessible, False otherwise
        """
        try:
            subprocess.run(
                ['systemctl', 'status'],
                timeout=2,
                capture_output=True
            )
            return True
        except Exception as e:
            logger.error(f"Systemd not accessible: {e}")
            return False

    def backup_services(self, service_names: List[str], output_path: str) -> Tuple[bool, str]:
        """Backup service configurations to a file.

        Args:
            service_names: List of service names to backup
            output_path: Path to output backup file

        Returns:
            Tuple of (success, message)
        """
        import json
        try:
            backup_data = {
                'version': '1.0',
                'services': {}
            }

            for service_name in service_names:
                if not service_name.endswith('.service'):
                    service_name += '.service'

                # Get unit file content
                result = subprocess.run(
                    ['systemctl', 'cat', service_name],
                    capture_output=True, text=True, timeout=self._timeout
                )

                if result.returncode == 0:
                    backup_data['services'][service_name] = {
                        'unit_file': result.stdout,
                        'enabled': self._is_enabled(service_name)
                    }

            with open(output_path, 'w') as f:
                json.dump(backup_data, f, indent=2)

            logger.info(f"Backed up {len(backup_data['services'])} services to {output_path}")
            return True, f"Successfully backed up {len(backup_data['services'])} services to {output_path}"

        except Exception as e:
            logger.error(f"Error backing up services: {e}")
            return False, f"Error backing up services: {e}"

    def restore_services(self, input_path: str) -> Tuple[bool, str]:
        """Restore service configurations from a backup file.

        Args:
            input_path: Path to backup file

        Returns:
            Tuple of (success, message)
        """
        import json
        try:
            with open(input_path, 'r') as f:
                backup_data = json.load(f)

            restored = 0
            for service_name, data in backup_data.get('services', {}).items():
                unit_file = data.get('unit_file', '')
                if not unit_file:
                    continue

                # Write unit file
                unit_path = Path(f"/etc/systemd/system/{service_name}")
                try:
                    unit_path.write_text(unit_file)
                except PermissionError:
                    # Try user directory
                    user_unit_dir = Path.home() / '.config' / 'systemd' / 'user'
                    user_unit_dir.mkdir(parents=True, exist_ok=True)
                    unit_path = user_unit_dir / service_name
                    unit_path.write_text(unit_file)

                # Reload systemd
                subprocess.run(['systemctl', 'daemon-reload'], capture_output=True)

                # Restore enabled state
                if data.get('enabled', False):
                    subprocess.run(['systemctl', 'enable', service_name], capture_output=True)

                restored += 1

            logger.info(f"Restored {restored} services from {input_path}")
            return True, f"Successfully restored {restored} services from {input_path}"

        except Exception as e:
            logger.error(f"Error restoring services: {e}")
            return False, f"Error restoring services: {e}"

    def get_unit_file(self, service_name: str) -> Optional[str]:
        """Get the unit file content for a service.

        Args:
            service_name: Service name

        Returns:
            Unit file content or None
        """
        try:
            if not service_name.endswith('.service'):
                service_name += '.service'

            result = subprocess.run(
                ['systemctl', 'cat', service_name],
                capture_output=True, text=True, timeout=self._timeout
            )

            if result.returncode == 0:
                return result.stdout
            return None
        except Exception as e:
            logger.error(f"Error getting unit file for {service_name}: {e}")
            return None
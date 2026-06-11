"""Service monitoring engine."""

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import List, Optional
import asyncio
import time


@dataclass
class Metrics:
    """Service metrics."""
    timestamp: float
    cpu_usage: float
    memory_usage: int
    io_read: int = 0
    io_write: int = 0


class MonitoringEngine:
    """Monitors service metrics in real-time.
    
    Features:
    - CPU usage per service
    - Memory consumption
    - I/O statistics
    - Historical data
    """
    
    def __init__(self, interval: float = 2.0):
        """Initialize monitoring engine.
        
        Args:
            interval: Monitoring interval in seconds
        """
        self.interval = interval
        self.metrics_history = defaultdict(lambda: deque(maxlen=300))
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        from .systemd import SystemdManager
        self.systemd_manager = SystemdManager()
    
    async def start_monitoring(self, services: List[str]):
        """Start monitoring for specified services."""
        if self._monitoring:
            return
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop(services))
    
    async def stop_monitoring(self):
        """Stop monitoring."""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
    
    async def _monitor_loop(self, services: List[str]):
        """Main monitoring loop."""
        while self._monitoring:
            try:
                for service in services:
                    metrics = await self.get_current_metrics(service)
                    if metrics:
                        self.metrics_history[service].append(metrics)
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.interval)
    
    async def get_current_metrics(self, service: str) -> Optional[Metrics]:
        """Get current metrics for a service."""
        try:
            # Get service object to access properties
            if not service.endswith('.service'):
                service_name = f"{service}.service"
            else:
                service_name = service
            
            # Get the unit path
            unit_path = self.systemd_manager.manager_interface.GetUnit(service_name)
            
            # Get the unit object
            unit_object = self.systemd_manager.bus.get_object('org.freedesktop.systemd1', unit_path)
            
            # Get properties interface
            props_interface = dbus.Interface(unit_object, 'org.freedesktop.DBus.Properties')
            
            # Try to get CPU usage (UserTime + SystemTime)
            cpu_usage = 0.0
            try:
                # Get CPU usage in microseconds, convert to percentage-like value
                user_time = props_interface.Get('org.freedesktop.systemd1.Service', 'UserTime')
                system_time = props_interface.Get('org.freedesktop.systemd1.Service', 'SystemTime')
                # Convert to seconds and normalize (this is a simplified approach)
                cpu_usage = (float(user_time) + float(system_time)) / 1000000.0  # microseconds to seconds
            except Exception:
                # If we can't get detailed CPU time, use a placeholder
                cpu_usage = 0.0
            
            # Try to get memory usage
            memory_usage = 0
            try:
                # Get memory usage in bytes
                memory = props_interface.Get('org.freedesktop.systemd1.Service', 'MemoryCurrent')
                memory_usage = int(memory)
            except Exception:
                # If we can't get memory, use 0
                memory_usage = 0
            
            # Try to get I/O statistics (simplified)
            io_read = 0
            io_write = 0
            try:
                # These might not be available on all systems
                io_read_bytes = props_interface.Get('org.freedesktop.systemd1.Service', 'IOReadBytes')
                io_write_bytes = props_interface.Get('org.freedesktop.systemd1.Service', 'IOWriteBytes')
                io_read = int(io_read_bytes)
                io_write = int(io_write_bytes)
            except Exception:
                # If I/O stats aren't available, leave as 0
                pass
            
            return Metrics(
                timestamp=time.time(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                io_read=io_read,
                io_write=io_write
            )
        except Exception as e:
            # Service might not exist or other error
            print(f"Error getting metrics for service {service}: {e}")
            return None
    
    def get_history(self, service: str, duration: int = 60) -> List[Metrics]:
        """Get historical metrics.
        
        Args:
            service: Service name
            duration: Duration in seconds
            
        Returns:
            List of historical metrics
        """
        history = self.metrics_history.get(service, [])
        # Return last 'duration' seconds of data
        return list(history)
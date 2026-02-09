# src/core/resource_monitor.py
"""Resource monitoring for systemd services"""

import psutil
import subprocess
from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class ServiceResources:
    """Resource usage of a service"""
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    memory_percent: float = 0.0
    process_count: int = 0


class ResourceMonitor:
    """Monitor resource usage of systemd services"""
    
    def __init__(self):
        self._cache: Dict[str, ServiceResources] = {}
    
    def get_service_resources(self, service_name: str) -> ServiceResources:
        """Get resource usage for a specific service"""
        try:
            # Get MainPID from systemd
            result = subprocess.run(
                ['systemctl', 'show', service_name, '--property=MainPID'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode != 0:
                return ServiceResources()
            
            # Parse MainPID
            main_pid_str = result.stdout.strip().split('=')[1]
            if not main_pid_str or main_pid_str == '0':
                return ServiceResources()
            
            main_pid = int(main_pid_str)
            
            # Get process and all children
            try:
                process = psutil.Process(main_pid)
                processes = [process] + process.children(recursive=True)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return ServiceResources()
            
            # Calculate total resources
            total_cpu = 0.0
            total_mem = 0.0
            process_count = len(processes)
            
            for proc in processes:
                try:
                    total_cpu += proc.cpu_percent(interval=0)
                    total_mem += proc.memory_info().rss / (1024 * 1024)  # MB
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            total_mem_system = psutil.virtual_memory().total / (1024 * 1024)
            mem_percent = (total_mem / total_mem_system) * 100 if total_mem_system > 0 else 0
            
            resources = ServiceResources(
                cpu_percent=round(total_cpu, 1),
                memory_mb=round(total_mem, 1),
                memory_percent=round(mem_percent, 2),
                process_count=process_count
            )
            
            # Cache result
            self._cache[service_name] = resources
            return resources
            
        except Exception:
            # Return cached value or empty
            return self._cache.get(service_name, ServiceResources())
    
    def get_multiple_resources(self, service_names: List[str]) -> Dict[str, ServiceResources]:
        """Get resources for multiple services at once"""
        results = {}
        for service_name in service_names:
            results[service_name] = self.get_service_resources(service_name)
        return results
    
    def clear_cache(self):
        """Clear cached resource data"""
        self._cache.clear()

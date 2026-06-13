# src/core/resource_monitor.py
"""Resource monitoring for systemd services"""

import psutil
import subprocess
import time
import threading
from typing import Dict, Optional, List
from dataclasses import dataclass
from functools import lru_cache


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
        self._cache_lock = threading.Lock()
        self._last_cpu_times: Dict[int, float] = {}  # pid -> last cpu_time
        self._last_check_time: Dict[int, float] = {}  # pid -> last check time

    def get_service_resources(self, service_name: str) -> ServiceResources:
        """Get resource usage for a specific service"""
        # Check cache first (thread-safe)
        with self._cache_lock:
            cached = self._cache.get(service_name)
            if cached:
                return cached

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

            # Calculate total resources with proper CPU measurement
            total_cpu = 0.0
            total_mem = 0.0
            process_count = len(processes)

            current_time = time.time()
            for proc in processes:
                try:
                    # Fix: Use two-sample method for accurate CPU%
                    # First call initializes, second call returns actual percentage
                    cpu1 = proc.cpu_percent(interval=None)
                    # Small delay for accurate measurement
                    time.sleep(0.05)
                    cpu2 = proc.cpu_percent(interval=None)
                    total_cpu += cpu2

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

            # Cache result (thread-safe)
            with self._cache_lock:
                self._cache[service_name] = resources
            return resources

        except Exception:
            # Return cached value or empty
            with self._cache_lock:
                return self._cache.get(service_name, ServiceResources())

    def get_multiple_resources(self, service_names: List[str]) -> Dict[str, ServiceResources]:
        """Get resources for multiple services at once - batch PID fetching"""
        if not service_names:
            return {}

        results = {}

        # Batch fetch all MainPIDs in ONE subprocess call
        cmd = ['systemctl', 'show', '--property=MainPID'] + service_names
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                # Fallback to individual calls if batch fails
                return {name: self.get_service_resources(name) for name in service_names}

            # Parse all PIDs from output
            pid_map: Dict[str, Optional[int]] = {}
            for line in result.stdout.strip().split('\n'):
                if '=' in line:
                    name, pid_str = line.split('=', 1)
                    if pid_str and pid_str != '0':
                        try:
                            pid_map[name] = int(pid_str)
                        except ValueError:
                            pid_map[name] = None
                    else:
                        pid_map[name] = None

            # Now get resources for each service using the fetched PIDs
            for service_name in service_names:
                pid = pid_map.get(service_name)
                if pid and pid > 0:
                    results[service_name] = self._get_resources_for_pid(service_name, pid)
                else:
                    results[service_name] = ServiceResources()

        except Exception:
            # Fallback to individual calls
            return {name: self.get_service_resources(name) for name in service_names}

        return results

    def _get_resources_for_pid(self, service_name: str, main_pid: int) -> ServiceResources:
        """Get resources for a service given its MainPID (internal helper)"""
        try:
            process = psutil.Process(main_pid)
            processes = [process] + process.children(recursive=True)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return ServiceResources()

        total_cpu = 0.0
        total_mem = 0.0
        process_count = len(processes)

        for proc in processes:
            try:
                # Two-sample method for accurate CPU%
                cpu1 = proc.cpu_percent(interval=None)
                time.sleep(0.05)
                cpu2 = proc.cpu_percent(interval=None)
                total_cpu += cpu2

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

        # Cache result (thread-safe)
        with self._cache_lock:
            self._cache[service_name] = resources
        return resources

    def clear_cache(self):
        """Clear cached resource data"""
        with self._cache_lock:
            self._cache.clear()
"""Unit tests for CachyOS Service Manager core functionality."""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Mock dbus for testing on Windows
sys.modules['dbus'] = MagicMock()
sys.modules['dbus.mainloop'] = MagicMock()
sys.modules['dbus.mainloop.glib'] = MagicMock()
sys.modules['dbus.service'] = MagicMock()
sys.modules['dbus.exceptions'] = MagicMock()

from core.service import Service, ServiceState
from core.service_manager import ServiceManager, ServiceInfo, ServiceType
from core.service_group import ServiceGroup, ServiceGroupManager
from core.resource_monitor import ResourceMonitor, ServiceResources


class TestServiceState:
    """Tests for ServiceState enum."""

    def test_service_state_values(self):
        assert ServiceState.ACTIVE.value == "active"
        assert ServiceState.INACTIVE.value == "inactive"
        assert ServiceState.FAILED.value == "failed"
        assert ServiceState.ACTIVATING.value == "activating"
        assert ServiceState.DEACTIVATING.value == "deactivating"
        assert ServiceState.UNKNOWN.value == "unknown"


class TestService:
    """Tests for Service dataclass."""

    def test_service_creation(self):
        service = Service(
            name="test.service",
            description="Test service",
            state=ServiceState.ACTIVE,
            sub_state="running",
            load_state="loaded",
            active_state="active"
        )
        assert service.name == "test.service"
        assert service.state == ServiceState.ACTIVE
        assert service.is_active() is True

    def test_service_inactive(self):
        service = Service(
            name="test.service",
            description="Test service",
            state=ServiceState.INACTIVE,
            sub_state="dead",
            load_state="loaded",
            active_state="inactive"
        )
        assert service.is_active() is False

    def test_service_defaults(self):
        service = Service(
            name="test.service",
            description="Test service",
            state=ServiceState.ACTIVE,
            sub_state="running",
            load_state="loaded",
            active_state="active"
        )
        assert service.requires == []
        assert service.wants == []
        assert service.before == []
        assert service.after == []
        assert service.enabled is False


class TestServiceInfo:
    """Tests for ServiceInfo dataclass."""

    def test_service_info_creation(self):
        info = ServiceInfo(
            name="test.service",
            display_name="test",
            state=ServiceState.ACTIVE,
            enabled=True,
            description="Test service",
            loaded=True,
            active_state="active",
            sub_state="running"
        )
        assert info.name == "test.service"
        assert info.display_name == "test"
        assert info.state == ServiceState.ACTIVE
        assert info.enabled is True

    def test_status_color_active(self):
        info = ServiceInfo(
            name="test.service",
            display_name="test",
            state=ServiceState.ACTIVE,
            enabled=True,
            description="Test",
            loaded=True,
            active_state="active",
            sub_state="running"
        )
        assert info.status_color == "#26a269"

    def test_status_color_inactive(self):
        info = ServiceInfo(
            name="test.service",
            display_name="test",
            state=ServiceState.INACTIVE,
            enabled=False,
            description="Test",
            loaded=True,
            active_state="inactive",
            sub_state="dead"
        )
        assert info.status_color == "#f6d32d"

    def test_status_color_failed(self):
        info = ServiceInfo(
            name="test.service",
            display_name="test",
            state=ServiceState.FAILED,
            enabled=False,
            description="Test",
            loaded=True,
            active_state="failed",
            sub_state="failed"
        )
        assert info.status_color == "#c01c28"

    def test_status_color_unknown(self):
        info = ServiceInfo(
            name="test.service",
            display_name="test",
            state=ServiceState.UNKNOWN,
            enabled=False,
            description="Test",
            loaded=False,
            active_state="unknown",
            sub_state="unknown"
        )
        assert info.status_color == "#9a9996"


class TestServiceManager:
    """Tests for ServiceManager class."""

    def test_map_state(self):
        mgr = ServiceManager()
        assert mgr._map_state("active") == ServiceState.ACTIVE
        assert mgr._map_state("inactive") == ServiceState.INACTIVE
        assert mgr._map_state("failed") == ServiceState.FAILED
        assert mgr._map_state("activating") == ServiceState.ACTIVATING
        assert mgr._map_state("deactivating") == ServiceState.DEACTIVATING
        assert mgr._map_state("unknown_state") == ServiceState.UNKNOWN

    def test_map_state_case_insensitive(self):
        mgr = ServiceManager()
        assert mgr._map_state("ACTIVE") == ServiceState.ACTIVE
        assert mgr._map_state("Active") == ServiceState.ACTIVE
        assert mgr._map_state("FaIlEd") == ServiceState.FAILED

    def test_get_stats(self):
        mgr = ServiceManager()
        services = [
            ServiceInfo(name="a.service", display_name="a", state=ServiceState.ACTIVE, enabled=True, description="", loaded=True, active_state="active", sub_state="running"),
            ServiceInfo(name="b.service", display_name="b", state=ServiceState.INACTIVE, enabled=False, description="", loaded=True, active_state="inactive", sub_state="dead"),
            ServiceInfo(name="c.service", display_name="c", state=ServiceState.FAILED, enabled=True, description="", loaded=True, active_state="failed", sub_state="failed"),
            ServiceInfo(name="d.service", display_name="d", state=ServiceState.ACTIVE, enabled=False, description="", loaded=True, active_state="active", sub_state="running"),
        ]
        stats = mgr.get_stats(services)
        assert stats['total'] == 4
        assert stats['active'] == 2
        assert stats['inactive'] == 1
        assert stats['failed'] == 1
        assert stats['enabled'] == 2

    def test_search_services(self):
        mgr = ServiceManager()
        services = [
            ServiceInfo(name="nginx.service", display_name="nginx", state=ServiceState.ACTIVE, enabled=True, description="Web server", loaded=True, active_state="active", sub_state="running"),
            ServiceInfo(name="postgresql.service", display_name="postgresql", state=ServiceState.ACTIVE, enabled=True, description="Database server", loaded=True, active_state="active", sub_state="running"),
        ]
        results = mgr.search_services("web", services)
        assert len(results) == 1
        assert results[0].display_name == "nginx"

        results = mgr.search_services("server", services)
        assert len(results) == 2

        results = mgr.search_services("nonexistent", services)
        assert len(results) == 0

    def test_init_with_custom_timeouts(self):
        mgr = ServiceManager(timeout=10.0, action_timeout=30.0, cache_ttl=5.0)
        assert mgr._timeout == 10.0
        assert mgr._action_timeout == 30.0
        assert mgr._cache_ttl == 5.0


class TestServiceGroup:
    """Tests for ServiceGroup dataclass."""

    def test_service_group_creation(self):
        group = ServiceGroup(
            name="Test Group",
            description="Test description",
            services=["a.service", "b.service"],
            color="#ff0000",
            icon="🧪"
        )
        assert group.name == "Test Group"
        assert group.services == ["a.service", "b.service"]
        assert group.color == "#ff0000"
        assert group.icon == "🧪"

    def test_add_service(self):
        group = ServiceGroup(name="Test", services=["a.service"])
        group.add_service("b.service")
        assert "b.service" in group.services
        assert len(group.services) == 2

    def test_add_duplicate_service(self):
        group = ServiceGroup(name="Test", services=["a.service"])
        group.add_service("a.service")  # Should not add duplicate
        assert len(group.services) == 1

    def test_remove_service(self):
        group = ServiceGroup(name="Test", services=["a.service", "b.service"])
        group.remove_service("a.service")
        assert "a.service" not in group.services
        assert len(group.services) == 1

    def test_has_service(self):
        group = ServiceGroup(name="Test", services=["a.service"])
        assert group.has_service("a.service") is True
        assert group.has_service("b.service") is False

    def test_to_dict(self):
        group = ServiceGroup(
            name="Test",
            description="Desc",
            services=["a.service"],
            color="#123456",
            icon="⭐",
            auto_start_order=False
        )
        data = group.to_dict()
        assert data['name'] == "Test"
        assert data['description'] == "Desc"
        assert data['services'] == ["a.service"]
        assert data['color'] == "#123456"
        assert data['icon'] == "⭐"
        assert data['auto_start_order'] is False

    def test_from_dict(self):
        data = {
            'name': 'Test',
            'description': 'Desc',
            'services': ['a.service'],
            'color': '#123456',
            'icon': '⭐',
            'auto_start_order': False
        }
        group = ServiceGroup.from_dict(data)
        assert group.name == "Test"
        assert group.services == ["a.service"]
        assert group.auto_start_order is False


class TestServiceGroupManager:
    """Tests for ServiceGroupManager class."""

    @pytest.fixture
    def temp_config(self, tmp_path):
        return tmp_path / "groups.json"

    @pytest.fixture
    def temp_templates(self, tmp_path):
        templates_file = tmp_path / "templates.json"
        templates_file.write_text('{"templates": [{"name": "Test Template", "description": "Test", "services": ["test.service"], "color": "#123", "icon": "🧪"}]}')
        return templates_file

    def test_create_group(self, temp_config):
        mgr = ServiceGroupManager(config_path=temp_config)
        group = mgr.create_group("Test Group", "Description", ["a.service"])
        assert group.name == "Test Group"
        assert group.services == ["a.service"]
        assert mgr.get_group("Test Group") == group

    def test_create_duplicate_group_raises(self, temp_config):
        mgr = ServiceGroupManager(config_path=temp_config)
        mgr.create_group("Test Group", services=["a.service"])
        with pytest.raises(ValueError, match="already exists"):
            mgr.create_group("Test Group", services=["b.service"])

    def test_delete_group(self, temp_config):
        mgr = ServiceGroupManager(config_path=temp_config)
        mgr.create_group("Test Group", services=["a.service"])
        mgr.delete_group("Test Group")
        assert mgr.get_group("Test Group") is None

    def test_update_group(self, temp_config):
        mgr = ServiceGroupManager(config_path=temp_config)
        mgr.create_group("Test Group", services=["a.service"], color="#ff0000")
        mgr.update_group("Test Group", color="#00ff00", description="New desc")
        group = mgr.get_group("Test Group")
        assert group.color == "#00ff00"
        assert group.description == "New desc"

    def test_update_nonexistent_group_raises(self, temp_config):
        mgr = ServiceGroupManager(config_path=temp_config)
        with pytest.raises(ValueError, match="not found"):
            mgr.update_group("Nonexistent", color="#000000")

    def test_list_groups(self, temp_config):
        mgr = ServiceGroupManager(config_path=temp_config)
        mgr.create_group("Group 1", services=["a.service"])
        mgr.create_group("Group 2", services=["b.service"])
        groups = mgr.list_groups()
        assert len(groups) == 2

    def test_get_groups_for_service(self, temp_config):
        mgr = ServiceGroupManager(config_path=temp_config)
        mgr.create_group("Group 1", services=["a.service", "b.service"])
        mgr.create_group("Group 2", services=["b.service", "c.service"])
        groups = mgr.get_groups_for_service("b.service")
        assert len(groups) == 2


class TestResourceMonitor:
    """Tests for ResourceMonitor class."""

    def test_service_resources_creation(self):
        res = ServiceResources(cpu_percent=10.5, memory_mb=100.0, memory_percent=5.0, process_count=3)
        assert res.cpu_percent == 10.5
        assert res.memory_mb == 100.0
        assert res.memory_percent == 5.0
        assert res.process_count == 3

    def test_service_resources_defaults(self):
        res = ServiceResources()
        assert res.cpu_percent == 0.0
        assert res.memory_mb == 0.0
        assert res.memory_percent == 0.0
        assert res.process_count == 0

    @patch('subprocess.run')
    def test_get_service_resources_no_pid(self, mock_run):
        mock_run.return_value = Mock(returncode=0, stdout="MainPID=0")
        monitor = ResourceMonitor()
        res = monitor.get_service_resources("test.service")
        assert res.cpu_percent == 0.0
        assert res.process_count == 0

    @patch('subprocess.run')
    def test_get_service_resources_failed_command(self, mock_run):
        mock_run.return_value = Mock(returncode=1, stderr="error")
        monitor = ResourceMonitor()
        res = monitor.get_service_resources("test.service")
        assert res.cpu_percent == 0.0

    def test_clear_cache(self):
        monitor = ResourceMonitor()
        monitor._cache["test.service"] = ServiceResources(cpu_percent=10.0)
        monitor.clear_cache()
        assert len(monitor._cache) == 0


class TestServiceType:
    """Tests for ServiceType enum."""

    def test_service_type_values(self):
        assert ServiceType.SERVICE.value == "service"
        assert ServiceType.SOCKET.value == "socket"
        assert ServiceType.TIMER.value == "timer"
        assert ServiceType.TARGET.value == "target"
        assert ServiceType.PATH.value == "path"
        assert ServiceType.MOUNT.value == "mount"
        assert ServiceType.DEVICE.value == "device"
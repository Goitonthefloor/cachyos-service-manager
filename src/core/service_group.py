"""Service group management."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import json
from pathlib import Path


class GroupAction(Enum):
    """Actions that can be performed on groups."""
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    ENABLE = "enable"
    DISABLE = "disable"


@dataclass
class ServiceGroup:
    """Represents a group of services."""
    
    name: str
    description: str = ""
    services: List[str] = field(default_factory=list)
    color: str = "#3daee9"  # Default: Plasma blue
    icon: str = "⚙️"  # Default: gear icon
    auto_start_order: bool = True  # Start services in order
    
    def add_service(self, service_name: str) -> None:
        """Add a service to the group."""
        if service_name not in self.services:
            self.services.append(service_name)
    
    def remove_service(self, service_name: str) -> None:
        """Remove a service from the group."""
        if service_name in self.services:
            self.services.remove(service_name)
    
    def has_service(self, service_name: str) -> bool:
        """Check if service is in group."""
        return service_name in self.services
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'services': self.services,
            'color': self.color,
            'icon': self.icon,
            'auto_start_order': self.auto_start_order
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ServiceGroup':
        """Create from dictionary."""
        return cls(
            name=data['name'],
            description=data.get('description', ''),
            services=data.get('services', []),
            color=data.get('color', '#3daee9'),
            icon=data.get('icon', '⚙️'),
            auto_start_order=data.get('auto_start_order', True)
        )


class ServiceGroupManager:
    """Manages service groups."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize group manager.
        
        Args:
            config_path: Path to groups configuration file
        """
        if config_path is None:
            config_dir = Path.home() / '.config' / 'cachyos-service-manager'
            config_dir.mkdir(parents=True, exist_ok=True)
            config_path = config_dir / 'groups.json'
        
        self.config_path = config_path
        self.groups: Dict[str, ServiceGroup] = {}
        self._load_groups()
    
    def _load_groups(self) -> None:
        """Load groups from configuration file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    for group_data in data.get('groups', []):
                        group = ServiceGroup.from_dict(group_data)
                        self.groups[group.name] = group
            except Exception as e:
                print(f"Error loading groups: {e}")
    
    def _save_groups(self) -> None:
        """Save groups to configuration file."""
        try:
            data = {
                'groups': [group.to_dict() for group in self.groups.values()]
            }
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving groups: {e}")
    
    def create_group(self, name: str, description: str = "", 
                    services: List[str] = None, color: str = "#3daee9",
                    icon: str = "⚙️") -> ServiceGroup:
        """Create a new service group.
        
        Args:
            name: Group name
            description: Group description
            services: List of service names
            color: Group color (hex)
            icon: Group icon (emoji or symbol)
            
        Returns:
            Created ServiceGroup
        """
        if name in self.groups:
            raise ValueError(f"Group '{name}' already exists")
        
        group = ServiceGroup(
            name=name,
            description=description,
            services=services or [],
            color=color,
            icon=icon
        )
        self.groups[name] = group
        self._save_groups()
        return group
    
    def delete_group(self, name: str) -> None:
        """Delete a service group.
        
        Args:
            name: Group name
        """
        if name in self.groups:
            del self.groups[name]
            self._save_groups()
    
    def get_group(self, name: str) -> Optional[ServiceGroup]:
        """Get a service group by name.
        
        Args:
            name: Group name
            
        Returns:
            ServiceGroup or None if not found
        """
        return self.groups.get(name)
    
    def list_groups(self) -> List[ServiceGroup]:
        """List all service groups.
        
        Returns:
            List of ServiceGroup objects
        """
        return list(self.groups.values())
    
    def update_group(self, name: str, **kwargs) -> None:
        """Update a service group.
        
        Args:
            name: Group name
            **kwargs: Attributes to update
        """
        if name not in self.groups:
            raise ValueError(f"Group '{name}' not found")
        
        group = self.groups[name]
        for key, value in kwargs.items():
            if hasattr(group, key):
                setattr(group, key, value)
        
        self._save_groups()
    
    def get_groups_for_service(self, service_name: str) -> List[ServiceGroup]:
        """Get all groups containing a specific service.
        
        Args:
            service_name: Service name
            
        Returns:
            List of ServiceGroup objects
        """
        return [group for group in self.groups.values() 
                if group.has_service(service_name)]
    
    def get_predefined_groups(self) -> List[Dict[str, any]]:
        """Get list of predefined group templates.
        
        Returns:
            List of group templates
        """
        return [
            {
                'name': 'Web Services',
                'description': 'Web server and related services',
                'services': ['nginx.service', 'apache2.service', 'php-fpm.service'],
                'color': '#27ae60',
                'icon': '🌍'
            },
            {
                'name': 'Database Services',
                'description': 'Database servers',
                'services': ['postgresql.service', 'mysql.service', 'redis.service', 'mongodb.service'],
                'color': '#e67e22',
                'icon': '🗄️'
            },
            {
                'name': 'Development',
                'description': 'Development tools and services',
                'services': ['docker.service', 'containerd.service', 'sshd.service'],
                'color': '#9b59b6',
                'icon': '🛠️'
            },
            {
                'name': 'Network Services',
                'description': 'Network and connectivity',
                'services': ['NetworkManager.service', 'systemd-resolved.service', 'avahi-daemon.service'],
                'color': '#3498db',
                'icon': '🌐'
            },
            {
                'name': 'Desktop Services',
                'description': 'Desktop environment services',
                'services': ['bluetooth.service', 'cups.service', 'pulseaudio.service'],
                'color': '#f39c12',
                'icon': '🖥️'
            },
            {
                'name': 'System Core',
                'description': 'Essential system services',
                'services': ['systemd-journald.service', 'systemd-udevd.service', 'dbus.service'],
                'color': '#e74c3c',
                'icon': '⚙️'
            }
        ]

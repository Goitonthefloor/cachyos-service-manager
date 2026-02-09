"""Service data models."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional


class ServiceState(Enum):
    """Service states."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    ACTIVATING = "activating"
    DEACTIVATING = "deactivating"


@dataclass
class Service:
    """Represents a systemd service."""
    
    name: str
    description: str
    state: ServiceState
    sub_state: str
    load_state: str
    active_state: str
    
    # Resource Information
    memory_current: int = 0
    cpu_usage: float = 0.0
    
    # Configuration
    unit_file: Optional[Path] = None
    enabled: bool = False
    preset: str = "disabled"
    
    # Dependencies
    requires: List[str] = None
    wants: List[str] = None
    before: List[str] = None
    after: List[str] = None
    
    # Runtime
    main_pid: Optional[int] = None
    control_pid: Optional[int] = None
    
    def __post_init__(self):
        """Initialize lists if None."""
        if self.requires is None:
            self.requires = []
        if self.wants is None:
            self.wants = []
        if self.before is None:
            self.before = []
        if self.after is None:
            self.after = []
    
    def is_active(self) -> bool:
        """Check if service is active."""
        return self.state == ServiceState.ACTIVE
    
    def is_enabled(self) -> bool:
        """Check if service is enabled."""
        return self.enabled
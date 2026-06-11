"""systemd D-Bus API wrapper."""

from typing import List, Optional
import asyncio
import dbus
import dbus.exceptions
import dbus.service
import dbus.mainloop.glib


class SystemdManager:
    """Central interface to systemd via D-Bus.
    
    Responsibilities:
    - systemd D-Bus API wrapper
    - Service lifecycle management
    - Unit file manipulation
    - Status monitoring
    """
    
    def __init__(self):
        """Initialize SystemdManager."""
        self._initialize_dbus()
    
    def _initialize_dbus(self):
        """Initialize the D-Bus connection to systemd."""
        try:
            # Set up the D-Bus main loop
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            
            # Connect to the system bus
            self.bus = dbus.SystemBus()
            
            # Get the systemd manager object
            self.systemd_object = self.bus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
            
            # Get the manager interface
            self.manager_interface = dbus.Interface(self.systemd_object, 'org.freedesktop.systemd1.Manager')
            
        except Exception as e:
            print(f"Failed to initialize D-Bus connection: {e}")
            # Leave as None, methods will handle this gracefully
            self.bus = None
            self.systemd_object = None
            self.manager_interface = None
    
    async def list_services(self) -> List['Service']:
        """List all services."""
        if not self.manager_interface:
            return []
        
        try:
            # Get list of all units
            units = self.manager_interface.ListUnits()
            
            # Filter for service units and convert to Service objects
            services = []
            for unit in units:
                unit_name, unit_description, load_state, active_state, sub_state, \
                followed_unit, unit_object_path, job_id, job_type, job_object_path = unit
                
                if unit_name.endswith('.service'):
                    service = Service(
                        name=unit_name,
                        description=unit_description or "",
                        load_state=load_state,
                        active_state=active_state,
                        sub_state=sub_state,
                        can_start=False,  # Will be set when getting specific service
                        can_stop=False    # Will be set when getting specific service
                    )
                    services.append(service)
            
            return services
        except Exception as e:
            print(f"Error listing services: {e}")
            return []
    
    async def get_service(self, name: str) -> 'Service':
        """Get a single service."""
        if not self.manager_interface:
            return None
        
        try:
            # Ensure the name ends with .service
            if not name.endswith('.service'):
                name = f"{name}.service"
            
            # Get the unit
            unit_path = self.manager_interface.GetUnit(name)
            
            # Get the unit object
            unit_object = self.bus.get_object('org.freedesktop.systemd1', unit_path)
            
            # Get properties interface
            props_interface = dbus.Interface(unit_object, 'org.freedesktop.DBus.Properties')
            
            # Get service properties
            description = props_interface.Get('org.freedesktop.systemd1.Unit', 'Description')
            load_state = props_interface.Get('org.freedesktop.systemd1.Unit', 'LoadState')
            active_state = props_interface.Get('org.freedesktop.systemd1.Unit', 'ActiveState')
            sub_state = props_interface.Get('org.freedesktop.systemd1.Unit', 'SubState')
            try:
                can_start = props_interface.Get('org.freedesktop.systemd1.Service', 'CanStart')
            except Exception:
                can_start = False
            try:
                can_stop = props_interface.Get('org.freedesktop.systemd1.Service', 'CanStop')
            except Exception:
                can_stop = False
            
            return Service(
                name=name,
                description=str(description),
                load_state=str(load_state),
                active_state=str(active_state),
                sub_state=str(sub_state),
                can_start=bool(can_start),
                can_stop=bool(can_stop)
            )
        except Exception as e:
            print(f"Error getting service {name}: {e}")
            return None
    
    async def start_service(self, name: str) -> bool:
        """Start a service."""
        if not self.manager_interface:
            return False
        
        try:
            # Ensure the name ends with .service
            if not name.endswith('.service'):
                name = f"{name}.service"
            
            # Start the service
            self.manager_interface.StartUnit(name, 'replace')
            return True
        except Exception as e:
            print(f"Error starting service {name}: {e}")
            return False
    
    async def stop_service(self, name: str) -> bool:
        """Stop a service."""
        if not self.manager_interface:
            return False
        
        try:
            # Ensure the name ends with .service
            if not name.endswith('.service'):
                name = f"{name}.service"
            
            # Stop the service
            self.manager_interface.StopUnit(name, 'replace')
            return True
        except Exception as e:
            print(f"Error stopping service {name}: {e}")
            return False
    
    async def restart_service(self, name: str) -> bool:
        """Restart a service."""
        if not self.manager_interface:
            return False
        
        try:
            # Ensure the name ends with .service
            if not name.endswith('.service'):
                name = f"{name}.service"
            
            # Restart the service
            self.manager_interface.RestartUnit(name, 'replace')
            return True
        except Exception as e:
            print(f"Error restarting service {name}: {e}")
            return False
    
    async def enable_service(self, name: str) -> bool:
        """Enable a service (autostart)."""
        if not self.manager_interface:
            return False
        
        try:
            # Ensure the name ends with .service
            if not name.endswith('.service'):
                name = f"{name}.service"
            
            # Enable the service
            self.manager_interface.EnableUnitFiles([name], False, True)
            return True
        except Exception as e:
            print(f"Error enabling service {name}: {e}")
            return False
    
    async def disable_service(self, name: str) -> bool:
        """Disable a service (no autostart)."""
        if not self.manager_interface:
            return False
        
        try:
            # Ensure the name ends with .service
            if not name.endswith('.service'):
                name = f"{name}.service"
            
            # Disable the service
            self.manager_interface.DisableUnitFiles([name])
            return True
        except Exception as e:
            print(f"Error disabling service {name}: {e}")
            return False


class Service:
    """Represents a systemd service."""
    
    def __init__(self, name: str, description: str, load_state: str, 
                 active_state: str, sub_state: str, can_start: bool, can_stop: bool):
        self.name = name
        self.description = description
        self.load_state = load_state
        self.active_state = active_state
        self.sub_state = sub_state
        self.can_start = can_start
        self.can_stop = can_stop
    
    def __str__(self):
        return f"Service(name={self.name}, description='{self.description}', load={self.load_state}, active={self.active_state}, sub={self.sub_state})"
    
    def __repr__(self):
        return self.__str__()
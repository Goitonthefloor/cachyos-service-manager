#!/usr/bin/env python3
"""Desktop test with Service Groups - GTK4/Adwaita Edition.

GTK4/Adwaita GUI with service group management:
- Create and manage service groups
- Start/Stop/Restart entire groups
- Visual group organization
- Collapsible group sections with Gtk.Expander
"""

import sys
import subprocess
import threading
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gdk

from core.service_group import ServiceGroup, ServiceGroupManager, GroupAction


class ServiceRow(Gtk.Box):
    """Row widget for displaying a single service."""
    
    def __init__(self, service_name):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.service_name = service_name
        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(4)
        self.set_margin_bottom(4)
        
        # Status indicator
        self.status_label = Gtk.Label(label="●")
        self.status_label.add_css_class("dim-label")
        
        # Service name
        name_label = Gtk.Label(label=service_name)
        name_label.set_xalign(0)
        name_label.set_hexpand(True)
        
        self.append(self.status_label)
        self.append(name_label)
        
        self.update_status()
    
    def update_status(self):
        """Update service status."""
        def check():
            try:
                result = subprocess.run(
                    ['systemctl', 'is-active', self.service_name],
                    capture_output=True, text=True, timeout=2
                )
                status = result.stdout.strip()
                GLib.idle_add(self._update_ui, status)
            except:
                GLib.idle_add(self._update_ui, "unknown")
        threading.Thread(target=check, daemon=True).start()
    
    def _update_ui(self, status):
        """Update UI with status."""
        if status == 'active':
            self.status_label.set_markup('<span foreground="#26a269">●</span>')
        elif status == 'inactive':
            self.status_label.set_markup('<span foreground="#f6d32d">●</span>')
        else:
            self.status_label.set_markup('<span foreground="#c01c28">●</span>')


class GroupExpander(Gtk.Expander):
    """Expander widget for a service group."""
    
    def __init__(self, group: ServiceGroup, parent_window):
        super().__init__()
        self.group = group
        self.parent_window = parent_window
        self.service_rows = {}
        
        self.set_expanded(True)
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.set_margin_start(12)
        self.set_margin_end(12)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        # Label with icon and name
        label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        icon_label = Gtk.Label(label=self.group.icon)
        name_label = Gtk.Label(label=self.group.name)
        name_label.add_css_class("heading")
        label_box.append(icon_label)
        label_box.append(name_label)
        self.set_label_widget(label_box)
        
        # Content box
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        content.set_margin_top(8)
        content.set_margin_bottom(8)
        content.set_margin_start(12)
        content.set_margin_end(12)
        
        # Description
        if self.group.description:
            desc = Gtk.Label(label=self.group.description)
            desc.set_xalign(0)
            desc.add_css_class("dim-label")
            desc.add_css_class("caption")
            content.append(desc)
        
        # Control buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_box.set_margin_top(8)
        btn_box.set_margin_bottom(8)
        
        start_btn = Gtk.Button(label="▶ Start All")
        start_btn.add_css_class("suggested-action")
        start_btn.connect("clicked", lambda _: self.execute_group_action(GroupAction.START))
        
        stop_btn = Gtk.Button(label="⏹ Stop All")
        stop_btn.add_css_class("destructive-action")
        stop_btn.connect("clicked", lambda _: self.execute_group_action(GroupAction.STOP))
        
        restart_btn = Gtk.Button(label="⟳ Restart All")
        restart_btn.connect("clicked", lambda _: self.execute_group_action(GroupAction.RESTART))
        
        btn_box.append(start_btn)
        btn_box.append(stop_btn)
        btn_box.append(restart_btn)
        content.append(btn_box)
        
        # Services list
        services_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        services_box.set_margin_top(8)
        
        for service_name in self.group.services:
            row = ServiceRow(service_name)
            self.service_rows[service_name] = row
            services_box.append(row)
        
        content.append(services_box)
        
        # Frame for content
        frame = Gtk.Frame()
        frame.set_child(content)
        self.set_child(frame)
        
        # Apply group color as CSS class
        self.add_css_class("group-expander")
    
    def execute_group_action(self, action: GroupAction):
        """Execute action on all services in group."""
        def run():
            success_count = 0
            total = len(self.group.services)
            
            for service in self.group.services:
                try:
                    result = subprocess.run(
                        ['pkexec', 'systemctl', action.value, service],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0:
                        success_count += 1
                    time.sleep(0.2)
                except:
                    pass
            
            success = success_count == total
            msg = f"{action.value.capitalize()} group '{self.group.name}': {success_count}/{total} successful"
            GLib.idle_add(self.parent_window.show_toast, msg)
            
            time.sleep(0.5)
            GLib.idle_add(self.refresh_services)
        
        threading.Thread(target=run, daemon=True).start()
    
    def refresh_services(self):
        """Refresh all service statuses."""
        for row in self.service_rows.values():
            row.update_status()


class CreateGroupDialog(Adw.Window):
    """Dialog for creating new service groups."""
    
    def __init__(self, available_services, parent, callback):
        super().__init__()
        self.available_services = available_services
        self.callback = callback
        self.selected_color = "#3584e4"
        
        self.set_title("Create Service Group")
        self.set_default_size(500, 600)
        self.set_transient_for(parent)
        self.set_modal(True)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # Header
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Create Service Group"))
        
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda _: self.close())
        header.pack_start(cancel_btn)
        
        create_btn = Gtk.Button(label="Create")
        create_btn.add_css_class("suggested-action")
        create_btn.connect("clicked", self.on_create)
        header.pack_end(create_btn)
        
        # Content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)
        
        # Name
        content.append(Gtk.Label(label="Group Name:", xalign=0))
        self.name_entry = Gtk.Entry()
        content.append(self.name_entry)
        
        # Description
        content.append(Gtk.Label(label="Description:", xalign=0))
        self.desc_entry = Gtk.Entry()
        content.append(self.desc_entry)
        
        # Icon
        content.append(Gtk.Label(label="Icon (emoji):", xalign=0))
        self.icon_entry = Gtk.Entry()
        self.icon_entry.set_text("⚙️")
        content.append(self.icon_entry)
        
        # Services
        content.append(Gtk.Label(label="Select Services:", xalign=0))
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_min_content_height(200)
        
        services_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.service_checks = {}
        
        for service in self.available_services:
            check = Gtk.CheckButton(label=service)
            self.service_checks[service] = check
            services_box.append(check)
        
        scrolled.set_child(services_box)
        content.append(scrolled)
        
        # Scrolled content
        scrolled_main = Gtk.ScrolledWindow()
        scrolled_main.set_child(content)
        scrolled_main.set_vexpand(True)
        
        box.append(header)
        box.append(scrolled_main)
        self.set_content(box)
    
    def on_create(self, button):
        """Handle create button."""
        name = self.name_entry.get_text()
        description = self.desc_entry.get_text()
        icon = self.icon_entry.get_text() or "⚙️"
        
        services = [service for service, check in self.service_checks.items() 
                   if check.get_active()]
        
        if name and services:
            self.callback(name, description, icon, self.selected_color, services)
            self.close()


class MainWindow(Adw.ApplicationWindow):
    """Main window with service groups."""
    
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("CachyOS Service Manager - Groups")
        self.set_default_size(900, 700)
        
        self.test_services = [
            'NetworkManager.service', 'bluetooth.service', 'cups.service',
            'sshd.service', 'docker.service', 'nginx.service',
            'postgresql.service', 'redis.service',
        ]
        
        self.group_manager = ServiceGroupManager()
        self.group_expanders = {}
        
        self.setup_ui()
        self.load_groups()
        self.start_auto_refresh()
    
    def setup_ui(self):
        """Setup UI."""
        # Toast overlay
        self.toast_overlay = Adw.ToastOverlay()
        
        # Main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # Header bar
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="📦 Service Groups Manager"))
        
        # Menu button
        menu_btn = Gtk.Button()
        menu_btn.set_icon_name("open-menu-symbolic")
        header.pack_end(menu_btn)
        
        # New group button
        new_btn = Gtk.Button(label="+ New Group")
        new_btn.add_css_class("suggested-action")
        new_btn.connect("clicked", self.on_new_group)
        header.pack_start(new_btn)
        
        # Refresh button
        refresh_btn = Gtk.Button()
        refresh_btn.set_icon_name("view-refresh-symbolic")
        refresh_btn.set_tooltip_text("Refresh All")
        refresh_btn.connect("clicked", lambda _: self.refresh_all())
        header.pack_start(refresh_btn)
        
        # Scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        
        # Groups box
        self.groups_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.groups_box.set_margin_top(12)
        self.groups_box.set_margin_bottom(12)
        
        scrolled.set_child(self.groups_box)
        
        main_box.append(header)
        main_box.append(scrolled)
        
        self.toast_overlay.set_child(main_box)
        self.set_content(self.toast_overlay)
    
    def load_groups(self):
        """Load all groups."""
        for group in self.group_manager.list_groups():
            self.add_group_widget(group)
    
    def add_group_widget(self, group: ServiceGroup):
        """Add group widget to UI."""
        expander = GroupExpander(group, self)
        self.group_expanders[group.name] = expander
        self.groups_box.append(expander)
    
    def on_new_group(self, button):
        """Show create group dialog."""
        dialog = CreateGroupDialog(
            self.test_services,
            self,
            self.create_group
        )
        dialog.present()
    
    def create_group(self, name, description, icon, color, services):
        """Create new group."""
        try:
            group = self.group_manager.create_group(
                name=name,
                description=description,
                icon=icon,
                color=color,
                services=services
            )
            self.add_group_widget(group)
            self.show_toast(f"✓ Created group: {name}")
        except Exception as e:
            self.show_toast(f"✗ Error: {str(e)}")
    
    def refresh_all(self):
        """Refresh all groups."""
        for expander in self.group_expanders.values():
            expander.refresh_services()
        self.show_toast("🔄 Refreshed all groups")
    
    def start_auto_refresh(self):
        """Start auto-refresh timer."""
        def refresh():
            self.refresh_all()
            return True
        GLib.timeout_add_seconds(10, refresh)
    
    def show_toast(self, message):
        """Show toast notification."""
        toast = Adw.Toast.new(message)
        toast.set_timeout(3)
        self.toast_overlay.add_toast(toast)


class ServiceManagerApp(Adw.Application):
    """Application class."""
    
    def __init__(self):
        super().__init__(application_id='org.cachyos.ServiceManager.Groups')
    
    def do_activate(self):
        win = MainWindow(self)
        win.present()


def main():
    app = ServiceManagerApp()
    return app.run(sys.argv)


if __name__ == '__main__':
    sys.exit(main())

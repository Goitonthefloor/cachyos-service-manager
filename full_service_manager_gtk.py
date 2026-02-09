#!/usr/bin/env python3
"""Complete Service Manager - GTK4/Adwaita Edition.

Full-featured systemd service manager:
- View ALL systemd services
- Start/Stop/Restart/Enable/Disable services
- Search and filter services
- View service logs
- Statistics dashboard
"""

import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Pango

from core.service_manager import ServiceManager, ServiceInfo, ServiceState, ServiceType
from core.service_group import ServiceGroupManager


class ServiceRow(Gtk.Box):
    """Row widget for a service in the list."""
    
    def __init__(self, service: ServiceInfo, parent_window):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.service = service
        self.parent_window = parent_window
        
        self.set_margin_start(8)
        self.set_margin_end(8)
        self.set_margin_top(4)
        self.set_margin_bottom(4)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        # Status indicator
        status_label = Gtk.Label(label="●")
        status_label.set_markup(f'<span foreground="{self.service.status_color}">●</span>')
        
        # Service info box
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        info_box.set_hexpand(True)
        
        name_label = Gtk.Label(label=self.service.display_name)
        name_label.set_xalign(0)
        name_label.add_css_class("heading")
        
        desc_label = Gtk.Label(label=self.service.description[:80] + "..." if len(self.service.description) > 80 else self.service.description)
        desc_label.set_xalign(0)
        desc_label.add_css_class("dim-label")
        desc_label.add_css_class("caption")
        desc_label.set_ellipsize(Pango.EllipsizeMode.END)
        
        info_box.append(name_label)
        info_box.append(desc_label)
        
        # State badge
        state_label = Gtk.Label(label=self.service.active_state)
        state_label.add_css_class("caption")
        if self.service.state == ServiceState.ACTIVE:
            state_label.add_css_class("success")
        elif self.service.state == ServiceState.FAILED:
            state_label.add_css_class("error")
        
        # Enabled badge
        enabled_label = Gtk.Label(label="✓ Enabled" if self.service.enabled else "○ Auto")
        enabled_label.add_css_class("caption")
        enabled_label.add_css_class("dim-label")
        
        # Action buttons
        actions_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        
        start_btn = Gtk.Button(label="▶")
        start_btn.add_css_class("circular")
        start_btn.set_tooltip_text("Start")
        start_btn.connect("clicked", lambda _: self.parent_window.start_service(self.service))
        
        stop_btn = Gtk.Button(label="■")
        stop_btn.add_css_class("circular")
        stop_btn.set_tooltip_text("Stop")
        stop_btn.connect("clicked", lambda _: self.parent_window.stop_service(self.service))
        
        restart_btn = Gtk.Button(label="⟳")
        restart_btn.add_css_class("circular")
        restart_btn.set_tooltip_text("Restart")
        restart_btn.connect("clicked", lambda _: self.parent_window.restart_service(self.service))
        
        logs_btn = Gtk.Button(label="📜")
        logs_btn.add_css_class("circular")
        logs_btn.set_tooltip_text("View Logs")
        logs_btn.connect("clicked", lambda _: self.parent_window.show_logs(self.service))
        
        actions_box.append(start_btn)
        actions_box.append(stop_btn)
        actions_box.append(restart_btn)
        actions_box.append(logs_btn)
        
        # Add all to main box
        self.append(status_label)
        self.append(info_box)
        self.append(state_label)
        self.append(enabled_label)
        self.append(actions_box)


class MainWindow(Adw.ApplicationWindow):
    """Main window with complete service management."""
    
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("CachyOS Service Manager - Full Control")
        self.set_default_size(1100, 750)
        
        self.service_manager = ServiceManager()
        self.group_manager = ServiceGroupManager()
        
        self.all_services = []
        self.filtered_services = []
        
        self.setup_ui()
        self.load_services()
        self.start_auto_refresh()
    
    def setup_ui(self):
        """Setup UI."""
        # Toast overlay
        self.toast_overlay = Adw.ToastOverlay()
        
        # Main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # Header
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="⚙️ CachyOS Service Manager"))
        
        # Refresh button
        refresh_btn = Gtk.Button()
        refresh_btn.set_icon_name("view-refresh-symbolic")
        refresh_btn.set_tooltip_text("Refresh Services")
        refresh_btn.connect("clicked", lambda _: self.load_services())
        header.pack_end(refresh_btn)
        
        # Stats label
        self.stats_label = Gtk.Label(label="")
        self.stats_label.add_css_class("caption")
        header.pack_start(self.stats_label)
        
        main_box.append(header)
        
        # Toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        toolbar.set_margin_start(12)
        toolbar.set_margin_end(12)
        toolbar.set_margin_top(12)
        toolbar.set_margin_bottom(8)
        
        # Search
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("🔍 Search services...")
        self.search_entry.set_hexpand(True)
        self.search_entry.connect("search-changed", lambda _: self.filter_services())
        
        # Filter dropdown
        filter_label = Gtk.Label(label="Filter:")
        self.filter_dropdown = Gtk.DropDown.new_from_strings(
            ["All", "Active", "Inactive", "Failed", "Enabled"]
        )
        self.filter_dropdown.connect("notify::selected", lambda *_: self.filter_services())
        
        # Show inactive checkbox
        self.show_inactive_check = Gtk.CheckButton(label="Show Inactive")
        self.show_inactive_check.set_active(True)
        self.show_inactive_check.connect("toggled", lambda _: self.load_services())
        
        toolbar.append(self.search_entry)
        toolbar.append(filter_label)
        toolbar.append(self.filter_dropdown)
        toolbar.append(self.show_inactive_check)
        
        main_box.append(toolbar)
        
        # Notebook for tabs
        self.notebook = Gtk.Notebook()
        self.notebook.set_vexpand(True)
        
        # Services tab
        services_scrolled = Gtk.ScrolledWindow()
        services_scrolled.set_vexpand(True)
        
        self.services_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.services_box.set_margin_top(8)
        self.services_box.set_margin_bottom(8)
        
        services_scrolled.set_child(self.services_box)
        self.notebook.append_page(services_scrolled, Gtk.Label(label="📋 Services"))
        
        # Logs tab
        logs_scrolled = Gtk.ScrolledWindow()
        logs_scrolled.set_vexpand(True)
        
        self.logs_text = Gtk.TextView()
        self.logs_text.set_editable(False)
        self.logs_text.set_monospace(True)
        self.logs_text.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.logs_text.set_margin_start(12)
        self.logs_text.set_margin_end(12)
        self.logs_text.set_margin_top(12)
        self.logs_text.set_margin_bottom(12)
        
        logs_scrolled.set_child(self.logs_text)
        self.notebook.append_page(logs_scrolled, Gtk.Label(label="📜 Logs"))
        
        main_box.append(self.notebook)
        
        # Status bar
        self.status_label = Gtk.Label(label="Ready")
        self.status_label.set_margin_start(12)
        self.status_label.set_margin_end(12)
        self.status_label.set_margin_top(4)
        self.status_label.set_margin_bottom(4)
        self.status_label.set_xalign(0)
        self.status_label.add_css_class("dim-label")
        self.status_label.add_css_class("caption")
        
        main_box.append(Gtk.Separator())
        main_box.append(self.status_label)
        
        self.toast_overlay.set_child(main_box)
        self.set_content(self.toast_overlay)
    
    def load_services(self):
        """Load all services."""
        self.status_label.set_text("Loading services...")
        
        def load():
            show_inactive = self.show_inactive_check.get_active()
            services = self.service_manager.list_all_services(
                service_type=ServiceType.SERVICE,
                show_inactive=show_inactive
            )
            GLib.idle_add(self.on_services_loaded, services)
        
        threading.Thread(target=load, daemon=True).start()
    
    def on_services_loaded(self, services):
        """Handle services loaded."""
        self.all_services = services
        self.filtered_services = services
        self.filter_services()
        
        # Update stats
        stats = self.service_manager.get_stats(services)
        self.stats_label.set_text(
            f"Total: {stats['total']} | Active: {stats['active']} | "
            f"Inactive: {stats['inactive']} | Failed: {stats['failed']}"
        )
        
        self.status_label.set_text(f"Loaded {len(services)} services")
    
    def filter_services(self):
        """Filter services."""
        services = self.all_services
        
        # Search filter
        search = self.search_entry.get_text().strip()
        if search:
            services = self.service_manager.search_services(search, services)
        
        # State filter
        filter_idx = self.filter_dropdown.get_selected()
        filter_types = ["All", "Active", "Inactive", "Failed", "Enabled"]
        filter_type = filter_types[filter_idx]
        
        if filter_type == "Active":
            services = [s for s in services if s.state == ServiceState.ACTIVE]
        elif filter_type == "Inactive":
            services = [s for s in services if s.state == ServiceState.INACTIVE]
        elif filter_type == "Failed":
            services = [s for s in services if s.state == ServiceState.FAILED]
        elif filter_type == "Enabled":
            services = [s for s in services if s.enabled]
        
        self.filtered_services = services
        self.display_services(services)
    
    def display_services(self, services):
        """Display services in list."""
        # Clear existing
        while True:
            child = self.services_box.get_first_child()
            if child is None:
                break
            self.services_box.remove(child)
        
        # Add service rows
        for service in services:
            row = ServiceRow(service, self)
            frame = Gtk.Frame()
            frame.set_child(row)
            frame.set_margin_start(12)
            frame.set_margin_end(12)
            frame.set_margin_top(2)
            frame.set_margin_bottom(2)
            self.services_box.append(frame)
    
    def start_service(self, service: ServiceInfo):
        """Start service."""
        def run():
            success, msg = self.service_manager.start_service(service.name)
            GLib.idle_add(self.on_action_completed, success, msg)
        threading.Thread(target=run, daemon=True).start()
    
    def stop_service(self, service: ServiceInfo):
        """Stop service."""
        def run():
            success, msg = self.service_manager.stop_service(service.name)
            GLib.idle_add(self.on_action_completed, success, msg)
        threading.Thread(target=run, daemon=True).start()
    
    def restart_service(self, service: ServiceInfo):
        """Restart service."""
        def run():
            success, msg = self.service_manager.restart_service(service.name)
            GLib.idle_add(self.on_action_completed, success, msg)
        threading.Thread(target=run, daemon=True).start()
    
    def show_logs(self, service: ServiceInfo):
        """Show service logs."""
        self.notebook.set_current_page(1)
        buffer = self.logs_text.get_buffer()
        buffer.set_text(f"Loading logs for {service.display_name}...")
        
        def load():
            logs = self.service_manager.get_service_logs(service.name, lines=200)
            GLib.idle_add(self.on_logs_loaded, logs)
        threading.Thread(target=load, daemon=True).start()
    
    def on_logs_loaded(self, logs):
        """Handle logs loaded."""
        buffer = self.logs_text.get_buffer()
        buffer.set_text(logs)
    
    def on_action_completed(self, success, msg):
        """Handle action completed."""
        toast = Adw.Toast.new(msg)
        toast.set_timeout(3)
        self.toast_overlay.add_toast(toast)
        
        # Refresh after action
        GLib.timeout_add(1000, self.load_services)
    
    def start_auto_refresh(self):
        """Start auto-refresh."""
        def refresh():
            self.load_services()
            return True
        GLib.timeout_add_seconds(30, refresh)


class ServiceManagerApp(Adw.Application):
    """Application class."""
    
    def __init__(self):
        super().__init__(application_id='org.cachyos.ServiceManager.Full')
    
    def do_activate(self):
        win = MainWindow(self)
        win.present()


def main():
    app = ServiceManagerApp()
    return app.run(sys.argv)


if __name__ == '__main__':
    sys.exit(main())

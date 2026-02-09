#!/usr/bin/env python3
"""Desktop test for CachyOS Service Manager.

Simple GUI to test service management functionality:
- List systemd services
- Start/Stop/Restart services
- Real-time status display
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
import subprocess
import threading
import time


class ServiceRow(Gtk.Box):
    """Row widget for displaying a service."""
    
    def __init__(self, service_name, on_action_callback):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.service_name = service_name
        self.on_action = on_action_callback
        
        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(6)
        self.set_margin_bottom(6)
        
        # Service name and status
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        info_box.set_hexpand(True)
        
        self.name_label = Gtk.Label(label=service_name)
        self.name_label.set_halign(Gtk.Align.START)
        self.name_label.add_css_class("title-4")
        
        self.status_label = Gtk.Label(label="Checking...")
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.add_css_class("dim-label")
        self.status_label.add_css_class("caption")
        
        info_box.append(self.name_label)
        info_box.append(self.status_label)
        
        # Action buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        self.start_btn = Gtk.Button(label="Start")
        self.start_btn.add_css_class("suggested-action")
        self.start_btn.connect("clicked", lambda _: self.on_action(service_name, "start"))
        
        self.stop_btn = Gtk.Button(label="Stop")
        self.stop_btn.add_css_class("destructive-action")
        self.stop_btn.connect("clicked", lambda _: self.on_action(service_name, "stop"))
        
        self.restart_btn = Gtk.Button(label="Restart")
        self.restart_btn.connect("clicked", lambda _: self.on_action(service_name, "restart"))
        
        button_box.append(self.start_btn)
        button_box.append(self.stop_btn)
        button_box.append(self.restart_btn)
        
        self.append(info_box)
        self.append(button_box)
        
        # Initial status update
        self.update_status()
    
    def update_status(self):
        """Update service status display."""
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', self.service_name],
                capture_output=True,
                text=True,
                timeout=2
            )
            status = result.stdout.strip()
            
            # Update label
            if status == 'active':
                self.status_label.set_markup("<span foreground='#2ec27e'>● Active</span>")
                self.start_btn.set_sensitive(False)
                self.stop_btn.set_sensitive(True)
                self.restart_btn.set_sensitive(True)
            elif status == 'inactive':
                self.status_label.set_markup("<span foreground='#c64600'>○ Inactive</span>")
                self.start_btn.set_sensitive(True)
                self.stop_btn.set_sensitive(False)
                self.restart_btn.set_sensitive(False)
            elif status == 'failed':
                self.status_label.set_markup("<span foreground='#e01b24'>✗ Failed</span>")
                self.start_btn.set_sensitive(True)
                self.stop_btn.set_sensitive(True)
                self.restart_btn.set_sensitive(True)
            else:
                self.status_label.set_text(f"Status: {status}")
                
        except subprocess.TimeoutExpired:
            self.status_label.set_text("Timeout")
        except Exception as e:
            self.status_label.set_text(f"Error: {str(e)}")


class MainWindow(Adw.ApplicationWindow):
    """Main application window."""
    
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("CachyOS Service Manager - Desktop Test")
        self.set_default_size(800, 600)
        
        # Common services to test with
        self.test_services = [
            'NetworkManager.service',
            'bluetooth.service',
            'cups.service',
            'sshd.service',
            'docker.service',
            'nginx.service',
            'postgresql.service',
            'redis.service',
        ]
        
        self.service_rows = {}
        
        self.setup_ui()
        self.start_auto_refresh()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Header bar
        header = Adw.HeaderBar()
        
        # Refresh button
        refresh_btn = Gtk.Button(icon_name="view-refresh-symbolic")
        refresh_btn.set_tooltip_text("Refresh all services")
        refresh_btn.connect("clicked", self.on_refresh_clicked)
        header.pack_start(refresh_btn)
        
        # Info button
        info_btn = Gtk.Button(icon_name="help-about-symbolic")
        info_btn.set_tooltip_text("About")
        info_btn.connect("clicked", self.show_about_dialog)
        header.pack_end(info_btn)
        
        main_box.append(header)
        
        # Content area with scrolling
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        # Service list
        self.service_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.service_list.set_margin_start(12)
        self.service_list.set_margin_end(12)
        self.service_list.set_margin_top(12)
        self.service_list.set_margin_bottom(12)
        
        # Add services
        for service_name in self.test_services:
            row = ServiceRow(service_name, self.on_service_action)
            self.service_rows[service_name] = row
            
            # Add separator
            if self.service_list.get_first_child() is not None:
                separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                separator.set_margin_top(6)
                separator.set_margin_bottom(6)
                self.service_list.append(separator)
            
            self.service_list.append(row)
        
        scrolled.set_child(self.service_list)
        main_box.append(scrolled)
        
        # Status bar
        self.status_bar = Gtk.Label(label="Ready")
        self.status_bar.set_margin_start(12)
        self.status_bar.set_margin_end(12)
        self.status_bar.set_margin_top(6)
        self.status_bar.set_margin_bottom(6)
        self.status_bar.add_css_class("dim-label")
        main_box.append(self.status_bar)
        
        self.set_content(main_box)
    
    def on_service_action(self, service_name, action):
        """Handle service action (start/stop/restart)."""
        self.status_bar.set_text(f"Executing: {action} {service_name}...")
        
        def run_action():
            try:
                # Use pkexec for privilege escalation
                result = subprocess.run(
                    ['pkexec', 'systemctl', action, service_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    GLib.idle_add(self.status_bar.set_text, 
                                f"Success: {action} {service_name}")
                else:
                    GLib.idle_add(self.status_bar.set_text, 
                                f"Failed: {result.stderr.strip()}")
                
                # Wait a moment for systemd to update
                time.sleep(0.5)
                
                # Refresh status
                GLib.idle_add(self.refresh_service, service_name)
                
            except subprocess.TimeoutExpired:
                GLib.idle_add(self.status_bar.set_text, "Timeout: Operation took too long")
            except Exception as e:
                GLib.idle_add(self.status_bar.set_text, f"Error: {str(e)}")
        
        # Run in background thread
        thread = threading.Thread(target=run_action, daemon=True)
        thread.start()
    
    def refresh_service(self, service_name):
        """Refresh a single service status."""
        if service_name in self.service_rows:
            self.service_rows[service_name].update_status()
    
    def refresh_all_services(self):
        """Refresh all service statuses."""
        for row in self.service_rows.values():
            row.update_status()
        self.status_bar.set_text("Refreshed all services")
        return True  # Continue timeout
    
    def on_refresh_clicked(self, button):
        """Handle refresh button click."""
        self.refresh_all_services()
    
    def start_auto_refresh(self):
        """Start automatic refresh every 5 seconds."""
        GLib.timeout_add_seconds(5, self.refresh_all_services)
    
    def show_about_dialog(self, button):
        """Show about dialog."""
        dialog = Adw.AboutWindow(transient_for=self)
        dialog.set_application_name("CachyOS Service Manager")
        dialog.set_version("0.1.0 (Desktop Test)")
        dialog.set_developer_name("Rolf Greger")
        dialog.set_license_type(Gtk.License.GPL_3_0)
        dialog.set_comments("Desktop test for systemd service management")
        dialog.set_website("https://github.com/Goitonthefloor/cachyos-service-manager")
        dialog.set_issue_url("https://github.com/Goitonthefloor/cachyos-service-manager/issues")
        dialog.present()


class ServiceManagerApp(Adw.Application):
    """Main application."""
    
    def __init__(self):
        super().__init__(application_id="org.cachyos.servicemanager.test")
    
    def do_activate(self):
        """Activate the application."""
        win = MainWindow(self)
        win.present()


def main():
    """Main entry point."""
    app = ServiceManagerApp()
    return app.run(None)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Desktop test with Service Groups - KDE Plasma Edition.

Qt6/KDE Plasma GUI with service group management:
- Create and manage service groups
- Start/Stop/Restart entire groups
- Visual group organization
- Collapsible group sections
"""

import sys
import subprocess
import threading
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QLabel, QPushButton, QFrame, QStatusBar, QMessageBox,
    QDialog, QLineEdit, QTextEdit, QListWidget, QDialogButtonBox,
    QGroupBox, QCheckBox, QColorDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor

from core.service_group import ServiceGroup, ServiceGroupManager, GroupAction


class ServiceSignals(QObject):
    """Signals for thread-safe communication."""
    status_updated = pyqtSignal(str, str)
    action_completed = pyqtSignal(str, str, bool)
    group_action_completed = pyqtSignal(str, str, bool)


class ServiceWidget(QFrame):
    """Widget for displaying a single service."""
    
    def __init__(self, service_name, parent=None):
        super().__init__(parent)
        self.service_name = service_name
        self.signals = ServiceSignals()
        self.signals.status_updated.connect(self._update_status_ui)
        
        self.setup_ui()
        self.update_status()
    
    def setup_ui(self):
        """Setup UI."""
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Service name
        self.name_label = QLabel(self.service_name)
        font = QFont()
        font.setPointSize(10)
        self.name_label.setFont(font)
        
        # Status
        self.status_label = QLabel("•")
        status_font = QFont()
        status_font.setPointSize(16)
        self.status_label.setFont(status_font)
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.name_label, stretch=1)
    
    def update_status(self):
        """Update status."""
        def check():
            try:
                result = subprocess.run(
                    ['systemctl', 'is-active', self.service_name],
                    capture_output=True, text=True, timeout=2
                )
                self.signals.status_updated.emit(self.service_name, result.stdout.strip())
            except:
                self.signals.status_updated.emit(self.service_name, "unknown")
        threading.Thread(target=check, daemon=True).start()
    
    def _update_status_ui(self, service, status):
        """Update UI."""
        if service != self.service_name:
            return
        if status == 'active':
            self.status_label.setStyleSheet("color: #27ae60;")
        elif status == 'inactive':
            self.status_label.setStyleSheet("color: #f39c12;")
        else:
            self.status_label.setStyleSheet("color: #e74c3c;")


class GroupWidget(QGroupBox):
    """Widget for displaying a service group."""
    
    def __init__(self, group: ServiceGroup, parent=None):
        super().__init__(parent)
        self.group = group
        self.service_widgets = {}
        self.signals = ServiceSignals()
        self.signals.group_action_completed.connect(parent.on_group_action_completed if parent else lambda *args: None)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        self.setTitle(f"{self.group.icon} {self.group.name}")
        self.setCheckable(True)
        self.setChecked(True)
        
        main_layout = QVBoxLayout(self)
        
        # Description
        if self.group.description:
            desc = QLabel(self.group.description)
            desc.setStyleSheet("color: #7f8c8d; font-style: italic;")
            main_layout.addWidget(desc)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        start_all_btn = QPushButton("▶ Start All")
        start_all_btn.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; 
                         border: none; border-radius: 4px; padding: 6px 12px; }
            QPushButton:hover { background-color: #229954; }
        """)
        start_all_btn.clicked.connect(lambda: self.execute_group_action(GroupAction.START))
        
        stop_all_btn = QPushButton("■ Stop All")
        stop_all_btn.setStyleSheet("""
            QPushButton { background-color: #da4453; color: white; 
                         border: none; border-radius: 4px; padding: 6px 12px; }
            QPushButton:hover { background-color: #c0392b; }
        """)
        stop_all_btn.clicked.connect(lambda: self.execute_group_action(GroupAction.STOP))
        
        restart_all_btn = QPushButton("⟳ Restart All")
        restart_all_btn.setStyleSheet("""
            QPushButton { background-color: #3daee9; color: white; 
                         border: none; border-radius: 4px; padding: 6px 12px; }
            QPushButton:hover { background-color: #2980b9; }
        """)
        restart_all_btn.clicked.connect(lambda: self.execute_group_action(GroupAction.RESTART))
        
        btn_layout.addWidget(start_all_btn)
        btn_layout.addWidget(stop_all_btn)
        btn_layout.addWidget(restart_all_btn)
        btn_layout.addStretch()
        
        main_layout.addLayout(btn_layout)
        
        # Services
        for service_name in self.group.services:
            widget = ServiceWidget(service_name)
            self.service_widgets[service_name] = widget
            main_layout.addWidget(widget)
        
        # Style
        self.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {self.group.color};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 16px;
                background-color: rgba(49, 54, 59, 0.5);
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
                color: {self.group.color};
                font-weight: bold;
                font-size: 12pt;
            }}
        """)
    
    def execute_group_action(self, action: GroupAction):
        """Execute action on all services in group."""
        def run():
            success_count = 0
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
            
            success = success_count == len(self.group.services)
            self.signals.group_action_completed.emit(self.group.name, action.value, success)
            
            time.sleep(0.5)
            for widget in self.service_widgets.values():
                widget.update_status()
        
        threading.Thread(target=run, daemon=True).start()
    
    def refresh_services(self):
        """Refresh all service statuses."""
        for widget in self.service_widgets.values():
            widget.update_status()


class CreateGroupDialog(QDialog):
    """Dialog for creating new service groups."""
    
    def __init__(self, available_services, parent=None):
        super().__init__(parent)
        self.available_services = available_services
        self.selected_color = "#3daee9"
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI."""
        self.setWindowTitle("Create Service Group")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Name
        layout.addWidget(QLabel("Group Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        
        # Description
        layout.addWidget(QLabel("Description:"))
        self.desc_input = QLineEdit()
        layout.addWidget(self.desc_input)
        
        # Icon
        layout.addWidget(QLabel("Icon (emoji):"))
        self.icon_input = QLineEdit("⚙️")
        layout.addWidget(self.icon_input)
        
        # Color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        self.color_btn = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self.choose_color)
        self.color_preview = QLabel("  ")
        self.color_preview.setStyleSheet(f"background-color: {self.selected_color}; border: 1px solid #fff;")
        color_layout.addWidget(self.color_btn)
        color_layout.addWidget(self.color_preview)
        color_layout.addStretch()
        layout.addLayout(color_layout)
        
        # Services
        layout.addWidget(QLabel("Select Services:"))
        self.services_list = QListWidget()
        self.services_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        for service in self.available_services:
            self.services_list.addItem(service)
        layout.addWidget(self.services_list)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def choose_color(self):
        """Choose group color."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color.name()
            self.color_preview.setStyleSheet(f"background-color: {self.selected_color}; border: 1px solid #fff;")
    
    def get_group_data(self):
        """Get group data from inputs."""
        selected_services = [item.text() for item in self.services_list.selectedItems()]
        return {
            'name': self.name_input.text(),
            'description': self.desc_input.text(),
            'icon': self.icon_input.text() or "⚙️",
            'color': self.selected_color,
            'services': selected_services
        }


class MainWindow(QMainWindow):
    """Main window with service groups."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CachyOS Service Manager - Groups")
        self.setMinimumSize(1000, 800)
        
        self.test_services = [
            'NetworkManager.service', 'bluetooth.service', 'cups.service',
            'sshd.service', 'docker.service', 'nginx.service',
            'postgresql.service', 'redis.service',
        ]
        
        self.group_manager = ServiceGroupManager()
        self.group_widgets = {}
        
        self.setup_ui()
        self.apply_plasma_theme()
        self.load_groups()
        self.start_auto_refresh()
    
    def setup_ui(self):
        """Setup UI."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QFrame()
        header.setStyleSheet("""
            QFrame { background-color: #31363b; border-bottom: 2px solid #3daee9; padding: 8px; }
        """)
        header_layout = QHBoxLayout(header)
        
        title = QLabel("📦 Service Groups Manager")
        title.setStyleSheet("color: white; font-size: 14pt; font-weight: bold; border: none;")
        
        new_group_btn = QPushButton("+ New Group")
        new_group_btn.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; border: none; 
                         border-radius: 4px; padding: 6px 16px; font-weight: bold; }
            QPushButton:hover { background-color: #229954; }
        """)
        new_group_btn.clicked.connect(self.create_new_group)
        
        templates_btn = QPushButton("📋 Templates")
        templates_btn.setStyleSheet("""
            QPushButton { background-color: #3daee9; color: white; border: none; 
                         border-radius: 4px; padding: 6px 16px; font-weight: bold; }
            QPushButton:hover { background-color: #2980b9; }
        """)
        templates_btn.clicked.connect(self.show_templates)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton { background-color: #3daee9; color: white; border: none; 
                         border-radius: 4px; padding: 6px 16px; font-weight: bold; }
            QPushButton:hover { background-color: #2980b9; }
        """)
        refresh_btn.clicked.connect(self.refresh_all)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(templates_btn)
        header_layout.addWidget(new_group_btn)
        header_layout.addWidget(refresh_btn)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        scroll_widget = QWidget()
        self.groups_layout = QVBoxLayout(scroll_widget)
        self.groups_layout.setContentsMargins(16, 16, 16, 16)
        self.groups_layout.setSpacing(16)
        self.groups_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar { background-color: #31363b; color: #eff0f1; border-top: 1px solid #3daee9; }
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        main_layout.addWidget(header)
        main_layout.addWidget(scroll, stretch=1)
    
    def apply_plasma_theme(self):
        """Apply Breeze Dark theme."""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(49, 54, 59))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(239, 240, 241))
        QApplication.setPalette(palette)
        self.setStyleSheet("QMainWindow { background-color: #232629; }")
    
    def load_groups(self):
        """Load all groups."""
        for group in self.group_manager.list_groups():
            self.add_group_widget(group)
    
    def add_group_widget(self, group: ServiceGroup):
        """Add group widget to UI."""
        widget = GroupWidget(group, self)
        self.group_widgets[group.name] = widget
        self.groups_layout.insertWidget(self.groups_layout.count() - 1, widget)
    
    def create_new_group(self):
        """Create new group dialog."""
        dialog = CreateGroupDialog(self.test_services, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_group_data()
            if data['name'] and data['services']:
                try:
                    group = self.group_manager.create_group(**data)
                    self.add_group_widget(group)
                    self.status_bar.showMessage(f"Created group: {data['name']}", 3000)
                except Exception as e:
                    QMessageBox.warning(self, "Error", str(e))
    
    def show_templates(self):
        """Show predefined group templates."""
        templates = self.group_manager.get_predefined_groups()
        msg = "Predefined Group Templates:\n\n"
        for t in templates:
            msg += f"{t['icon']} {t['name']}: {t['description']}\n"
        QMessageBox.information(self, "Group Templates", msg)
    
    def refresh_all(self):
        """Refresh all groups."""
        for widget in self.group_widgets.values():
            widget.refresh_services()
        self.status_bar.showMessage("Refreshed all groups", 2000)
    
    def start_auto_refresh(self):
        """Start auto-refresh timer."""
        timer = QTimer()
        timer.timeout.connect(self.refresh_all)
        timer.start(10000)
    
    def on_group_action_completed(self, group_name, action, success):
        """Handle group action completion."""
        if success:
            self.status_bar.showMessage(f"✓ {action.capitalize()} group '{group_name}' completed", 3000)
        else:
            self.status_bar.showMessage(f"✗ Failed to {action} group '{group_name}'", 3000)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CachyOS Service Manager - Groups")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Complete Service Manager - KDE Plasma Edition.

Full-featured systemd service manager:
- View ALL systemd services
- Start/Stop/Restart/Enable/Disable services
- Search and filter services
- View service logs
- Statistics dashboard
- Service Groups integration
"""

import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QLabel, QPushButton, QFrame, QStatusBar, QMessageBox,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QTextEdit, QComboBox, QCheckBox, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor

from core.service_manager import ServiceManager, ServiceInfo, ServiceState, ServiceType
from core.service_group import ServiceGroupManager


class ServiceSignals(QObject):
    """Signals for async operations."""
    services_loaded = pyqtSignal(list)
    action_completed = pyqtSignal(bool, str)
    logs_loaded = pyqtSignal(str)


class ServiceTable(QTableWidget):
    """Table widget for displaying services."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.services = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup table UI."""
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels([
            "Status", "Service", "State", "Enabled", "Description", "Actions"
        ])
        
        # Column widths
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        
        self.setColumnWidth(0, 60)
        self.setColumnWidth(5, 280)
        
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    
    def load_services(self, services: list):
        """Load services into table."""
        self.services = services
        self.setRowCount(len(services))
        
        for row, service in enumerate(services):
            # Status indicator
            status_widget = QLabel("●")
            status_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = QFont()
            font.setPointSize(16)
            status_widget.setFont(font)
            status_widget.setStyleSheet(f"color: {service.status_color};")
            self.setCellWidget(row, 0, status_widget)
            
            # Service name
            name_item = QTableWidgetItem(service.display_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 1, name_item)
            
            # State
            state_item = QTableWidgetItem(service.active_state)
            state_item.setFlags(state_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if service.state == ServiceState.ACTIVE:
                state_item.setForeground(QColor("#27ae60"))
            elif service.state == ServiceState.FAILED:
                state_item.setForeground(QColor("#e74c3c"))
            self.setItem(row, 2, state_item)
            
            # Enabled
            enabled_item = QTableWidgetItem("✓" if service.enabled else "○")
            enabled_item.setFlags(enabled_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            enabled_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(row, 3, enabled_item)
            
            # Description
            desc_item = QTableWidgetItem(service.description)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 4, desc_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 2, 4, 2)
            actions_layout.setSpacing(4)
            
            start_btn = QPushButton("▶")
            start_btn.setFixedSize(30, 24)
            start_btn.setStyleSheet("background-color: #27ae60; color: white; border: none; border-radius: 3px;")
            start_btn.clicked.connect(lambda checked, s=service: self.parent().start_service(s))
            
            stop_btn = QPushButton("■")
            stop_btn.setFixedSize(30, 24)
            stop_btn.setStyleSheet("background-color: #da4453; color: white; border: none; border-radius: 3px;")
            stop_btn.clicked.connect(lambda checked, s=service: self.parent().stop_service(s))
            
            restart_btn = QPushButton("⟳")
            restart_btn.setFixedSize(30, 24)
            restart_btn.setStyleSheet("background-color: #3daee9; color: white; border: none; border-radius: 3px;")
            restart_btn.clicked.connect(lambda checked, s=service: self.parent().restart_service(s))
            
            enable_btn = QPushButton("Enable" if not service.enabled else "Disable")
            enable_btn.setFixedSize(60, 24)
            enable_btn.setStyleSheet("background-color: #9b59b6; color: white; border: none; border-radius: 3px;")
            if not service.enabled:
                enable_btn.clicked.connect(lambda checked, s=service: self.parent().enable_service(s))
            else:
                enable_btn.clicked.connect(lambda checked, s=service: self.parent().disable_service(s))
            
            logs_btn = QPushButton("Logs")
            logs_btn.setFixedSize(45, 24)
            logs_btn.setStyleSheet("background-color: #f39c12; color: white; border: none; border-radius: 3px;")
            logs_btn.clicked.connect(lambda checked, s=service: self.parent().show_logs(s))
            
            actions_layout.addWidget(start_btn)
            actions_layout.addWidget(stop_btn)
            actions_layout.addWidget(restart_btn)
            actions_layout.addWidget(enable_btn)
            actions_layout.addWidget(logs_btn)
            
            self.setCellWidget(row, 5, actions_widget)


class MainWindow(QMainWindow):
    """Main window with complete service management."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CachyOS Service Manager - Full Control")
        self.setMinimumSize(1200, 800)
        
        self.service_manager = ServiceManager()
        self.group_manager = ServiceGroupManager()
        self.signals = ServiceSignals()
        self.signals.services_loaded.connect(self.on_services_loaded)
        self.signals.action_completed.connect(self.on_action_completed)
        self.signals.logs_loaded.connect(self.on_logs_loaded)
        
        self.all_services = []
        self.filtered_services = []
        
        self.setup_ui()
        self.apply_plasma_theme()
        self.load_services()
        self.start_auto_refresh()
    
    def setup_ui(self):
        """Setup UI."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Services tab
        services_tab = self.create_services_tab()
        self.tabs.addTab(services_tab, "📋 All Services")
        
        # Logs tab
        logs_tab = self.create_logs_tab()
        self.tabs.addTab(logs_tab, "📜 Service Logs")
        
        layout.addWidget(self.tabs)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar { background-color: #31363b; color: #eff0f1; border-top: 1px solid #3daee9; }
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def create_header(self):
        """Create header."""
        header = QFrame()
        header.setStyleSheet("""
            QFrame { background-color: #31363b; border-bottom: 2px solid #3daee9; padding: 8px; }
        """)
        layout = QHBoxLayout(header)
        
        title = QLabel("⚙️ CachyOS Service Manager - Full Control")
        title.setStyleSheet("color: white; font-size: 14pt; font-weight: bold; border: none;")
        
        # Stats
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("color: #eff0f1; border: none;")
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton { background-color: #3daee9; color: white; border: none; 
                         border-radius: 4px; padding: 6px 16px; font-weight: bold; }
            QPushButton:hover { background-color: #2980b9; }
        """)
        refresh_btn.clicked.connect(self.load_services)
        
        layout.addWidget(title)
        layout.addWidget(self.stats_label)
        layout.addStretch()
        layout.addWidget(refresh_btn)
        
        return header
    
    def create_services_tab(self):
        """Create services tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Controls
        controls = QHBoxLayout()
        
        # Search
        search_label = QLabel("🔍 Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search services...")
        self.search_input.textChanged.connect(self.filter_services)
        
        # Filter
        filter_label = QLabel("Filter:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Active", "Inactive", "Failed", "Enabled"])
        self.filter_combo.currentTextChanged.connect(self.filter_services)
        
        # Show inactive
        self.show_inactive_check = QCheckBox("Show Inactive")
        self.show_inactive_check.setChecked(True)
        self.show_inactive_check.toggled.connect(lambda: self.load_services())
        
        controls.addWidget(search_label)
        controls.addWidget(self.search_input, stretch=1)
        controls.addWidget(filter_label)
        controls.addWidget(self.filter_combo)
        controls.addWidget(self.show_inactive_check)
        
        layout.addLayout(controls)
        
        # Service table
        self.service_table = ServiceTable(self)
        layout.addWidget(self.service_table)
        
        return widget
    
    def create_logs_tab(self):
        """Create logs tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setStyleSheet("""
            QTextEdit { 
                background-color: #232629; 
                color: #eff0f1; 
                font-family: monospace; 
                font-size: 10pt;
            }
        """)
        
        layout.addWidget(QLabel("Service logs will appear here"))
        layout.addWidget(self.logs_text)
        
        return widget
    
    def apply_plasma_theme(self):
        """Apply Plasma theme."""
        self.setStyleSheet("""
            QMainWindow { background-color: #232629; }
            QTableWidget {
                background-color: #31363b;
                color: #eff0f1;
                gridline-color: #4d4d4d;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #3daee9;
            }
            QHeaderView::section {
                background-color: #31363b;
                color: #eff0f1;
                padding: 6px;
                border: none;
                border-bottom: 2px solid #3daee9;
                font-weight: bold;
            }
            QLineEdit, QComboBox {
                background-color: #31363b;
                color: #eff0f1;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 6px;
            }
            QTabWidget::pane {
                border: none;
                background-color: #232629;
            }
            QTabBar::tab {
                background-color: #31363b;
                color: #eff0f1;
                padding: 8px 16px;
                border: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3daee9;
            }
        """)
    
    def load_services(self):
        """Load all services."""
        self.status_bar.showMessage("Loading services...")
        
        def load():
            show_inactive = self.show_inactive_check.isChecked()
            services = self.service_manager.list_all_services(
                service_type=ServiceType.SERVICE,
                show_inactive=show_inactive
            )
            self.signals.services_loaded.emit(services)
        
        threading.Thread(target=load, daemon=True).start()
    
    def on_services_loaded(self, services):
        """Handle services loaded."""
        self.all_services = services
        self.filtered_services = services
        self.filter_services()
        
        # Update stats
        stats = self.service_manager.get_stats(services)
        self.stats_label.setText(
            f"Total: {stats['total']} | "
            f"Active: {stats['active']} | "
            f"Inactive: {stats['inactive']} | "
            f"Failed: {stats['failed']} | "
            f"Enabled: {stats['enabled']}"
        )
        
        self.status_bar.showMessage(f"Loaded {len(services)} services", 3000)
    
    def filter_services(self):
        """Filter services based on search and filter."""
        services = self.all_services
        
        # Search filter
        search = self.search_input.text().strip()
        if search:
            services = self.service_manager.search_services(search, services)
        
        # State filter
        filter_type = self.filter_combo.currentText()
        if filter_type == "Active":
            services = [s for s in services if s.state == ServiceState.ACTIVE]
        elif filter_type == "Inactive":
            services = [s for s in services if s.state == ServiceState.INACTIVE]
        elif filter_type == "Failed":
            services = [s for s in services if s.state == ServiceState.FAILED]
        elif filter_type == "Enabled":
            services = [s for s in services if s.enabled]
        
        self.filtered_services = services
        self.service_table.load_services(services)
    
    def start_service(self, service: ServiceInfo):
        """Start service."""
        def run():
            success, msg = self.service_manager.start_service(service.name)
            self.signals.action_completed.emit(success, msg)
        threading.Thread(target=run, daemon=True).start()
    
    def stop_service(self, service: ServiceInfo):
        """Stop service."""
        def run():
            success, msg = self.service_manager.stop_service(service.name)
            self.signals.action_completed.emit(success, msg)
        threading.Thread(target=run, daemon=True).start()
    
    def restart_service(self, service: ServiceInfo):
        """Restart service."""
        def run():
            success, msg = self.service_manager.restart_service(service.name)
            self.signals.action_completed.emit(success, msg)
        threading.Thread(target=run, daemon=True).start()
    
    def enable_service(self, service: ServiceInfo):
        """Enable service."""
        def run():
            success, msg = self.service_manager.enable_service(service.name)
            self.signals.action_completed.emit(success, msg)
        threading.Thread(target=run, daemon=True).start()
    
    def disable_service(self, service: ServiceInfo):
        """Disable service."""
        def run():
            success, msg = self.service_manager.disable_service(service.name)
            self.signals.action_completed.emit(success, msg)
        threading.Thread(target=run, daemon=True).start()
    
    def show_logs(self, service: ServiceInfo):
        """Show service logs."""
        self.tabs.setCurrentIndex(1)
        self.logs_text.setText(f"Loading logs for {service.display_name}...")
        
        def load():
            logs = self.service_manager.get_service_logs(service.name, lines=200)
            self.signals.logs_loaded.emit(logs)
        threading.Thread(target=load, daemon=True).start()
    
    def on_logs_loaded(self, logs):
        """Handle logs loaded."""
        self.logs_text.setText(logs)
    
    def on_action_completed(self, success, msg):
        """Handle action completed."""
        if success:
            self.status_bar.showMessage(f"✓ {msg}", 3000)
        else:
            self.status_bar.showMessage(f"✗ {msg}", 5000)
        
        # Refresh after action
        QTimer.singleShot(1000, self.load_services)
    
    def start_auto_refresh(self):
        """Start auto-refresh."""
        timer = QTimer()
        timer.timeout.connect(self.load_services)
        timer.start(30000)  # 30 seconds


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CachyOS Service Manager")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Desktop test for CachyOS Service Manager - KDE Plasma Edition.

Qt6/KDE Plasma style GUI to test service management functionality:
- List systemd services
- Start/Stop/Restart services
- Real-time status display with Breeze icons
"""

import sys
import subprocess
import threading
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QLabel, QPushButton, QFrame, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor


class ServiceSignals(QObject):
    """Signals for thread-safe communication."""
    status_updated = pyqtSignal(str, str)  # service_name, status
    action_completed = pyqtSignal(str, str, bool)  # service, action, success


class ServiceWidget(QFrame):
    """Widget for displaying a single service with KDE Plasma styling."""
    
    def __init__(self, service_name, parent=None):
        super().__init__(parent)
        self.service_name = service_name
        self.signals = ServiceSignals()
        self.signals.status_updated.connect(self._update_status_ui)
        
        self.setup_ui()
        self.update_status()
        
    def setup_ui(self):
        """Setup the widget UI with KDE Plasma styling."""
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Left side: Service info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        # Service name
        self.name_label = QLabel(self.service_name)
        name_font = QFont()
        name_font.setPointSize(11)
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        
        # Status label
        self.status_label = QLabel("Checking...")
        status_font = QFont()
        status_font.setPointSize(9)
        self.status_label.setFont(status_font)
        
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.status_label)
        info_layout.addStretch()
        
        # Right side: Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        # Start button (Breeze green)
        self.start_btn = QPushButton("▶ Start")
        self.start_btn.setMinimumWidth(100)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #bdc3c7;
            }
        """)
        self.start_btn.clicked.connect(lambda: self.execute_action("start"))
        
        # Stop button (Breeze red)
        self.stop_btn = QPushButton("■ Stop")
        self.stop_btn.setMinimumWidth(100)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #da4453;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #bdc3c7;
            }
        """)
        self.stop_btn.clicked.connect(lambda: self.execute_action("stop"))
        
        # Restart button (Breeze blue)
        self.restart_btn = QPushButton("⟳ Restart")
        self.restart_btn.setMinimumWidth(100)
        self.restart_btn.setStyleSheet("""
            QPushButton {
                background-color: #3daee9;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #bdc3c7;
            }
        """)
        self.restart_btn.clicked.connect(lambda: self.execute_action("restart"))
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.restart_btn)
        
        layout.addLayout(info_layout, stretch=1)
        layout.addLayout(button_layout)
        
    def update_status(self):
        """Update service status in background thread."""
        def check_status():
            try:
                result = subprocess.run(
                    ['systemctl', 'is-active', self.service_name],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                status = result.stdout.strip()
                self.signals.status_updated.emit(self.service_name, status)
            except Exception as e:
                self.signals.status_updated.emit(self.service_name, f"error:{str(e)}")
        
        thread = threading.Thread(target=check_status, daemon=True)
        thread.start()
    
    def _update_status_ui(self, service_name, status):
        """Update UI with status (called from signal)."""
        if service_name != self.service_name:
            return
        
        if status == 'active':
            self.status_label.setText("● Active")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.restart_btn.setEnabled(True)
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(39, 174, 96, 0.1);
                    border: 1px solid rgba(39, 174, 96, 0.3);
                    border-radius: 6px;
                }
            """)
        elif status == 'inactive':
            self.status_label.setText("○ Inactive")
            self.status_label.setStyleSheet("color: #f39c12; font-weight: bold;")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.restart_btn.setEnabled(False)
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(243, 156, 18, 0.1);
                    border: 1px solid rgba(243, 156, 18, 0.3);
                    border-radius: 6px;
                }
            """)
        elif status == 'failed':
            self.status_label.setText("✗ Failed")
            self.status_label.setStyleSheet("color: #da4453; font-weight: bold;")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            self.restart_btn.setEnabled(True)
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(218, 68, 83, 0.1);
                    border: 1px solid rgba(218, 68, 83, 0.3);
                    border-radius: 6px;
                }
            """)
        else:
            self.status_label.setText(f"Status: {status}")
            self.status_label.setStyleSheet("color: #7f8c8d;")
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(127, 140, 141, 0.1);
                    border: 1px solid rgba(127, 140, 141, 0.3);
                    border-radius: 6px;
                }
            """)
    
    def execute_action(self, action):
        """Execute service action in background thread."""
        def run_action():
            try:
                result = subprocess.run(
                    ['pkexec', 'systemctl', action, self.service_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                success = result.returncode == 0
                self.signals.action_completed.emit(self.service_name, action, success)
                
                # Wait for systemd to update
                time.sleep(0.5)
                self.update_status()
                
            except Exception as e:
                self.signals.action_completed.emit(self.service_name, action, False)
        
        thread = threading.Thread(target=run_action, daemon=True)
        thread.start()


class MainWindow(QMainWindow):
    """Main window with KDE Plasma styling."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CachyOS Service Manager - KDE Plasma Edition")
        self.setMinimumSize(900, 700)
        
        # Test services
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
        
        self.service_widgets = {}
        
        self.setup_ui()
        self.apply_plasma_theme()
        self.start_auto_refresh()
    
    def setup_ui(self):
        """Setup the main UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header / Toolbar
        header = QFrame()
        header.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        header.setStyleSheet("""
            QFrame {
                background-color: #31363b;
                border-bottom: 2px solid #3daee9;
                padding: 8px;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        
        # Title
        title = QLabel("⚙ CachyOS Service Manager")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: white; border: none;")
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3daee9;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_all)
        
        # About button
        about_btn = QPushButton("ℹ About")
        about_btn.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5d6d7e;
            }
        """)
        about_btn.clicked.connect(self.show_about)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        header_layout.addWidget(about_btn)
        
        # Scroll area for services
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        scroll_widget = QWidget()
        self.services_layout = QVBoxLayout(scroll_widget)
        self.services_layout.setContentsMargins(16, 16, 16, 16)
        self.services_layout.setSpacing(12)
        
        # Add service widgets
        for service_name in self.test_services:
            widget = ServiceWidget(service_name)
            widget.signals.action_completed.connect(self.on_action_completed)
            self.service_widgets[service_name] = widget
            self.services_layout.addWidget(widget)
        
        self.services_layout.addStretch()
        scroll.setWidget(scroll_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #31363b;
                color: #eff0f1;
                border-top: 1px solid #3daee9;
            }
        """)
        self.status_bar.showMessage("Ready")
        self.setStatusBar(self.status_bar)
        
        main_layout.addWidget(header)
        main_layout.addWidget(scroll, stretch=1)
    
    def apply_plasma_theme(self):
        """Apply KDE Plasma dark theme."""
        palette = QPalette()
        
        # Breeze Dark colors
        palette.setColor(QPalette.ColorRole.Window, QColor(49, 54, 59))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(239, 240, 241))
        palette.setColor(QPalette.ColorRole.Base, QColor(35, 38, 41))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(49, 54, 59))
        palette.setColor(QPalette.ColorRole.Text, QColor(239, 240, 241))
        palette.setColor(QPalette.ColorRole.Button, QColor(49, 54, 59))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(239, 240, 241))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(61, 174, 233))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(239, 240, 241))
        
        QApplication.setPalette(palette)
        
        # Global stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #232629;
            }
            QScrollArea {
                background-color: #232629;
                border: none;
            }
            QWidget {
                background-color: #232629;
            }
        """)
    
    def refresh_all(self):
        """Refresh all service statuses."""
        for widget in self.service_widgets.values():
            widget.update_status()
        self.status_bar.showMessage("Refreshing all services...", 2000)
    
    def start_auto_refresh(self):
        """Start automatic refresh timer."""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_all)
        self.refresh_timer.start(5000)  # 5 seconds
    
    def on_action_completed(self, service, action, success):
        """Handle action completion."""
        if success:
            self.status_bar.showMessage(f"✓ {action.capitalize()} {service} completed", 3000)
        else:
            self.status_bar.showMessage(f"✗ Failed to {action} {service}", 3000)
    
    def show_about(self):
        """Show about dialog."""
        about_text = """
        <h2>CachyOS Service Manager</h2>
        <p><b>Version:</b> 0.1.0 (KDE Plasma Edition)</p>
        <p><b>Developer:</b> Rolf Greger</p>
        <p><b>License:</b> GPL-3.0</p>
        <br>
        <p>Desktop test for systemd service management with KDE Plasma styling.</p>
        <p><a href='https://github.com/Goitonthefloor/cachyos-service-manager'>GitHub Repository</a></p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("About CachyOS Service Manager")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(about_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("CachyOS Service Manager")
    app.setOrganizationName("CachyOS")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

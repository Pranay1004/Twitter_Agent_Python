"""
Twitter Automation Suite - Main Launcher
Launch all GUI applications from a single interface
"""

import sys
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QFrame, QScrollArea, 
                            QMessageBox, QTextEdit, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QProcess
from PyQt5.QtGui import QFont, QPixmap, QIcon

class AppLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Twitter Automation Suite - Launcher")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(700, 500)
        
        # Apply modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel#title {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
            QLabel#subtitle {
                font-size: 14px;
                color: #7f8c8d;
                padding: 5px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton#danger {
                background-color: #e74c3c;
            }
            QPushButton#danger:hover {
                background-color: #c0392b;
            }
            QPushButton#success {
                background-color: #27ae60;
            }
            QPushButton#success:hover {
                background-color: #229954;
            }
            QFrame#separator {
                background-color: #bdc3c7;
                max-height: 2px;
                margin: 10px 0px;
            }
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                padding: 8px;
            }
        """)
        
        self.setupUI()
        self.running_processes = {}
        
    def setupUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main splitter
        splitter = QSplitter(Qt.Vertical)
        
        # Top section with app buttons
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        
        # Header
        title_label = QLabel("🚁 Twitter Automation Suite")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Professional drone content automation tools")
        subtitle_label.setObjectName("subtitle")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        top_layout.addWidget(title_label)
        top_layout.addWidget(subtitle_label)
        
        # Separator
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.HLine)
        top_layout.addWidget(separator)
        
        # Application buttons
        apps_layout = self.createAppButtons()
        top_layout.addLayout(apps_layout)
        
        # Control buttons
        control_layout = self.createControlButtons()
        top_layout.addLayout(control_layout)
        
        # Add to splitter
        splitter.addWidget(top_widget)
        
        # Bottom section with log/status
        log_widget = self.createLogSection()
        splitter.addWidget(log_widget)
        
        # Set splitter proportions
        splitter.setSizes([400, 200])
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(splitter)
        
    def createAppButtons(self):
        layout = QVBoxLayout()
        
        # Main Applications
        main_apps_label = QLabel("📱 Main Applications")
        main_apps_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin: 10px 0px 5px 0px;")
        layout.addWidget(main_apps_label)
        
        main_apps_layout = QHBoxLayout()
        
        # Main GUI Button
        self.main_gui_btn = QPushButton("🚀 Main Twitter Agent")
        self.main_gui_btn.clicked.connect(lambda: self.launch_app("TwitterAgent-Main.exe", "Main Twitter Agent"))
        self.main_gui_btn.setToolTip("Launch the main Twitter automation interface with content generation, posting, and scheduling features")
        main_apps_layout.addWidget(self.main_gui_btn)
        
        # Content Ideator Button
        self.ideator_btn = QPushButton("💡 Content Ideator")
        self.ideator_btn.clicked.connect(lambda: self.launch_app("TwitterAgent-Ideator.exe", "Content Ideator"))
        self.ideator_btn.setToolTip("Launch the content ideation tool for generating creative drone industry content ideas")
        main_apps_layout.addWidget(self.ideator_btn)
        
        # API Manager Button
        self.api_manager_btn = QPushButton("🔧 API Manager")
        self.api_manager_btn.clicked.connect(lambda: self.launch_app("TwitterAgent-APIManager.exe", "API Manager"))
        self.api_manager_btn.setToolTip("Manage API keys and configuration settings for all integrated services")
        main_apps_layout.addWidget(self.api_manager_btn)
        
        layout.addLayout(main_apps_layout)
        
        # Utility Applications
        utils_label = QLabel("🛠️ Utility Tools")
        utils_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin: 15px 0px 5px 0px;")
        layout.addWidget(utils_label)
        
        utils_layout = QHBoxLayout()
        
        # Image Preview Tool
        self.image_preview_btn = QPushButton("🖼️ Image Preview")
        self.image_preview_btn.clicked.connect(lambda: self.launch_app("../image_preview.py", "Image Preview"))
        self.image_preview_btn.setToolTip("Preview and manage generated images for your content")
        utils_layout.addWidget(self.image_preview_btn)
        
        # Test Tools Button
        self.test_tools_btn = QPushButton("🧪 Test Tools")
        self.test_tools_btn.clicked.connect(self.show_test_tools)
        self.test_tools_btn.setToolTip("Access testing and debugging utilities")
        utils_layout.addWidget(self.test_tools_btn)
        
        layout.addLayout(utils_layout)
        
        return layout
        
    def createControlButtons(self):
        layout = QHBoxLayout()
        
        # Status label
        self.status_label = QLabel("Ready to launch applications")
        self.status_label.setStyleSheet("color: #27ae60; font-weight: bold; padding: 10px;")
        layout.addWidget(self.status_label)
        
        # Spacer
        layout.addStretch()
        
        # Close All Button
        self.close_all_btn = QPushButton("❌ Close All Apps")
        self.close_all_btn.setObjectName("danger")
        self.close_all_btn.clicked.connect(self.close_all_apps)
        self.close_all_btn.setToolTip("Close all running applications")
        layout.addWidget(self.close_all_btn)
        
        # Refresh Button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_status)
        self.refresh_btn.setToolTip("Refresh application status")
        layout.addWidget(self.refresh_btn)
        
        # Exit Button
        self.exit_btn = QPushButton("🚪 Exit Launcher")
        self.exit_btn.setObjectName("danger")
        self.exit_btn.clicked.connect(self.close_launcher)
        self.exit_btn.setToolTip("Exit the launcher application")
        layout.addWidget(self.exit_btn)
        
        return layout
        
    def createLogSection(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        log_label = QLabel("📋 Activity Log")
        log_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50; margin: 5px 0px;")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Add initial log entry
        self.log("🚀 Twitter Automation Suite Launcher started")
        self.log("📱 Ready to launch applications")
        
        return widget
        
    def launch_app(self, exe_name, app_name):
        """Launch an executable application"""
        try:
            if app_name in self.running_processes:
                if self.running_processes[app_name].poll() is None:
                    self.log(f"⚠️ {app_name} is already running")
                    self.status_label.setText(f"{app_name} is already running")
                    return
            
            # Look for exe in dist directory first
            exe_path = os.path.join(os.path.dirname(__file__), "dist", exe_name)
            if not os.path.exists(exe_path):
                # Try current directory
                exe_path = os.path.join(os.path.dirname(__file__), exe_name)
                if not os.path.exists(exe_path):
                    self.log(f"❌ Executable not found: {exe_name}")
                    self.status_label.setText(f"Error: {exe_name} not found")
                    return
            
            # Launch the process
            process = subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))
            
            self.running_processes[app_name] = process
            self.log(f"✅ Launched: {app_name}")
            self.status_label.setText(f"Launched: {app_name}")
            
        except Exception as e:
            self.log(f"❌ Failed to launch {app_name}: {str(e)}")
            self.status_label.setText(f"Error launching {app_name}")
            QMessageBox.critical(self, "Launch Error", f"Failed to launch {app_name}:\n{str(e)}")
    
    def show_test_tools(self):
        """Show available test tools"""
        msg = QMessageBox()
        msg.setWindowTitle("Test Tools")
        msg.setText("Available test utilities:")
        msg.setDetailedText("""
Available Test Scripts:
• test_apis.py - Test all API connections
• test_gemini_api_fixed.py - Test Gemini API specifically
• test_perplexity_api.py - Test Perplexity API
• test_image_generation.py - Test image generation
• test_full_agent.py - Full system test
• test_ai_ideas.py - Test AI idea generation
• test_ai_threads.py - Test AI thread generation

These tools help debug and verify system functionality.
        """)
        msg.exec_()
    
    def close_all_apps(self):
        """Close all running applications"""
        count = 0
        for app_name, process in list(self.running_processes.items()):
            try:
                if process.poll() is None:  # Process is still running
                    process.terminate()
                    count += 1
                    self.log(f"🔴 Closed: {app_name}")
                del self.running_processes[app_name]
            except Exception as e:
                self.log(f"⚠️ Error closing {app_name}: {str(e)}")
        
        if count > 0:
            self.status_label.setText(f"Closed {count} applications")
            self.log(f"📴 Closed {count} applications")
        else:
            self.status_label.setText("No applications were running")
            self.log("📴 No applications were running")
    
    def refresh_status(self):
        """Refresh the status of running applications"""
        active_count = 0
        for app_name, process in list(self.running_processes.items()):
            if process.poll() is None:
                active_count += 1
            else:
                del self.running_processes[app_name]
        
        self.status_label.setText(f"{active_count} applications running")
        self.log(f"🔄 Status refreshed: {active_count} apps running")
    
    def close_launcher(self):
        """Close the launcher and all applications"""
        reply = QMessageBox.question(
            self, 'Exit Launcher', 
            'Do you want to close all applications and exit?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close_all_apps()
            self.close()
    
    def log(self, message):
        """Add a message to the log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self, 'Exit Launcher', 
            'Do you want to close all applications and exit?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close_all_apps()
            event.accept()
        else:
            event.ignore()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Twitter Automation Suite")
    app.setApplicationVersion("1.0.0")
    
    # Set application icon if available
    try:
        app.setWindowIcon(QIcon('icon.ico'))
    except:
        pass
    
    launcher = AppLauncher()
    launcher.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

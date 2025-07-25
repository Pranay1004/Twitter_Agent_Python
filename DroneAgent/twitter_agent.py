#!/usr/bin/env python3
"""
Twitter Agent - Single Unified GUI Application
Entry point for the complete Twitter automation suite
"""

import sys
import os

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Ensure the directory is in the path for PyInstaller
if hasattr(sys, '_MEIPASS'):
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    sys.path.insert(0, sys._MEIPASS)
    
    # Add specific module paths when running as bundled app
    agent_dir = os.path.join(sys._MEIPASS, 'agent')
    if os.path.exists(agent_dir):
        sys.path.insert(0, agent_dir)
        print(f"Added agent directory to path: {agent_dir}")
        
    utils_dir = os.path.join(sys._MEIPASS, 'utils')
    if os.path.exists(utils_dir):
        sys.path.insert(0, utils_dir)
        print(f"Added utils directory to path: {utils_dir}")
    
# Add the current directory to sys.path to ensure modules can be found
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Add local agent directory if it exists
agent_dir = os.path.join(current_dir, 'agent')
if os.path.exists(agent_dir):
    sys.path.insert(0, agent_dir)

# Import the special hook to ensure all modules are found
try:
    import import_hook
except ImportError:
    print("Could not import hook module - continuing anyway")

def main():
    """Main entry point for the Twitter Agent GUI"""
    
    try:
        # Import the main GUI
        from gui import DroneAgentGUI
    except ImportError:
        print("Error: Could not import GUI module. Make sure 'gui.py' is in the application directory.")
        sys.exit(1)
    from PyQt5.QtWidgets import QApplication
    
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("Twitter Automation Suite")
    app.setApplicationVersion("1.0.0")
    
    # Create and show the main window
    window = DroneAgentGUI()
    window.show()
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

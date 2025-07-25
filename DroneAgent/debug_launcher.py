"""
Debug launcher for TwitterAgent
Runs the application with detailed error logging
"""

import sys
import os
import traceback

def main():
    try:
        # Add the current directory to sys.path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        # Create a log file for errors
        log_path = os.path.join(current_dir, 'error_log.txt')
        with open(log_path, 'w') as f:
            f.write(f"Starting application from {current_dir}\n")
            f.write(f"Python version: {sys.version}\n")
            f.write(f"System path: {sys.path}\n\n")
        
        # Try to import and run the main application
        try:
            from twitter_agent import main as twitter_main
            with open(log_path, 'a') as f:
                f.write("Successfully imported twitter_agent\n")
            twitter_main()
        except ImportError as e:
            with open(log_path, 'a') as f:
                f.write(f"Import Error: {str(e)}\n")
                f.write(traceback.format_exc())
                
            # Try direct import of GUI
            try:
                with open(log_path, 'a') as f:
                    f.write("Trying direct GUI import...\n")
                from gui import DroneAgentGUI
                from PyQt5.QtWidgets import QApplication
                
                app = QApplication(sys.argv)
                app.setApplicationName("Twitter Automation Suite")
                app.setApplicationVersion("1.0.0")
                
                window = DroneAgentGUI()
                window.show()
                
                sys.exit(app.exec_())
            except Exception as gui_error:
                with open(log_path, 'a') as f:
                    f.write(f"GUI Error: {str(gui_error)}\n")
                    f.write(traceback.format_exc())
        except Exception as e:
            with open(log_path, 'a') as f:
                f.write(f"General Error: {str(e)}\n")
                f.write(traceback.format_exc())
    
    except Exception as outer_error:
        # If we can't even write to the log file, print to stderr
        print(f"Critical error: {str(outer_error)}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
    # Keep the console window open if there was an error
    input("Press Enter to exit...")

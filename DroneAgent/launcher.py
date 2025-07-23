#!/usr/bin/env python3
"""
DroneAgent Launcher
Sets proper working directory and launches the application
"""

import os
import sys
from pathlib import Path

# Set working directory to project root
project_root = Path(__file__).parent
os.chdir(project_root)

# Add to Python path
sys.path.insert(0, str(project_root))

# Import and run main
if __name__ == "__main__":
    from main import main
    main()

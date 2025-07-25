"""
Import hook for agent modules
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Add specific module locations if they exist
agent_dir = os.path.join(current_dir, 'agent')
if os.path.exists(agent_dir) and agent_dir not in sys.path:
    sys.path.insert(0, agent_dir)

utils_dir = os.path.join(current_dir, 'utils')
if os.path.exists(utils_dir) and utils_dir not in sys.path:
    sys.path.insert(0, utils_dir)

# Helper function to check if a module exists
def module_exists(module_name):
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

# Print system path for debugging
if not module_exists('agent.ideator'):
    print(f"Error: agent.ideator not found in sys.path: {sys.path}")
    
    # Try fallback imports
    try:
        import agent
        print(f"Found agent at: {agent.__file__}")
        
        # Check agent directory content
        agent_path = os.path.dirname(agent.__file__)
        print(f"Agent directory contains: {os.listdir(agent_path)}")
    except ImportError as e:
        print(f"Could not import agent module: {e}")

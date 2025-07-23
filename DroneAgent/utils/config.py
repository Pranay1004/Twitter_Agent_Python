"""
Configuration management utilities
"""

import yaml
import os
from pathlib import Path

def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent.parent / "config.yaml"
    
    if not config_path.exists():
        # Try the parent directory
        config_path = Path(__file__).parent.parent.parent / "config.yaml"
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    else:
        # Return default config if file doesn't exist
        return {
            'thread_templates': {},
            'posting_schedule': {},
            'content_settings': {}
        }

def save_config(config):
    """Save configuration to config.yaml"""
    config_path = Path(__file__).parent.parent / "config.yaml"
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config, f, default_flow_style=False)

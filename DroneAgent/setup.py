#!/usr/bin/env python3
"""
DroneAgent Setup Script
Automates the initial setup process
"""

import os
import shutil
from pathlib import Path

def create_logs_directory():
    """Create logs directory"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    print("✅ Created logs directory")

def setup_env_file():
    """Setup .env file from template"""
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️ .env file already exists, skipping...")
        return
    
    env_template = """# Twitter API Keys (Required)
TWITTER_API_KEY=your_twitter_api_key_here
TWITTER_API_SECRET=your_twitter_api_secret_here
TWITTER_ACCESS_TOKEN=your_twitter_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret_here
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here

# AI API Keys (At least one required)
PERPLEXITY_API_KEY=your_perplexity_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Image APIs (Optional)
UNSPLASH_ACCESS_KEY=your_unsplash_access_key_here
PEXELS_API_KEY=your_pexels_api_key_here

# URL Shortener (Optional)
BITLY_ACCESS_TOKEN=your_bitly_access_token_here"""
    
    with open(env_file, 'w') as f:
        f.write(env_template)
    
    print("✅ Created .env template file")
    print("📝 Please edit .env with your actual API keys")

def setup_config():
    """Verify config.yaml exists"""
    config_file = Path("config.yaml")
    if config_file.exists():
        print("✅ Configuration file found")
    else:
        print("❌ config.yaml not found")

def check_dependencies():
    """Check if required packages can be imported"""
    required_packages = [
        'tweepy', 'PyQt5', 'requests', 'pytz', 'matplotlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - installed")
        except ImportError:
            print(f"❌ {package} - missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Install missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
    else:
        print("\n✅ All required packages are installed!")

def main():
    """Main setup function"""
    print("🚁 DroneAgent Setup")
    print("=" * 30)
    
    print("\n📁 Setting up directories...")
    create_logs_directory()
    
    print("\n🔧 Setting up configuration...")
    setup_env_file()
    setup_config()
    
    print("\n📦 Checking dependencies...")
    check_dependencies()
    
    print("\n" + "=" * 30)
    print("🎯 Next Steps:")
    print("1. Edit .env file with your API keys")
    print("2. Customize config.yaml if needed")
    print("3. Run: python main.py --gui")
    print("4. Or run: python main.py --ideate")
    print("\n📚 See README.md for detailed instructions")

if __name__ == "__main__":
    main()

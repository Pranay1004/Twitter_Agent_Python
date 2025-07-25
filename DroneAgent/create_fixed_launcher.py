"""
Create a fixed version of the launcher that correctly finds the executables
"""
import os
import subprocess

# Path to where the script is running
script_dir = os.path.dirname(os.path.abspath(__file__))
dist_dir = os.path.join(script_dir, "dist")

def create_fixed_batch_file():
    """Create an improved batch file for launching applications"""
    
    batch_content = """@echo off
echo ============================================
echo Twitter Automation Suite - Fixed Launcher
echo ============================================
echo.
echo 1. Main Twitter Agent
echo 2. Content Ideator
echo 3. API Manager
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

cd /d "%~dp0dist"

if "%choice%"=="1" (
    echo Launching Main Twitter Agent...
    start "" "TwitterAgent-Main.exe"
) else if "%choice%"=="2" (
    echo Launching Content Ideator...
    start "" "TwitterAgent-Ideator.exe"
) else if "%choice%"=="3" (
    echo Launching API Manager...
    start "" "TwitterAgent-APIManager.exe"
) else if "%choice%"=="4" (
    exit
) else (
    echo Invalid choice. Please try again.
    pause
    goto :start
)

echo Application launched successfully!
"""
    
    # Write the batch file
    batch_path = os.path.join(script_dir, "Launch_Fixed.bat")
    with open(batch_path, "w") as f:
        f.write(batch_content)
    
    print(f"Created fixed launcher batch file at: {batch_path}")

if __name__ == "__main__":
    create_fixed_batch_file()
    print("Fix completed.")

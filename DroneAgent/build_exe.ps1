# Twitter Automation Suite - Build Script (PowerShell)
# Run this script to build all GUI applications into executable files

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Twitter Automation Suite - Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

Write-Host "[2/6] Installing required packages..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    Write-Host "Requirements installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to install requirements!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

Write-Host "[3/6] Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
Write-Host "Build directories cleaned." -ForegroundColor Green
Write-Host ""

Write-Host "[4/6] Building all applications with PyInstaller..." -ForegroundColor Yellow
try {
    pyinstaller build_all.spec --clean --noconfirm
    Write-Host "Build completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

Write-Host "[5/6] Creating application shortcuts..." -ForegroundColor Yellow
Set-Location "dist\TwitterAutomationSuite"

# Create batch files for easy launching
@"
@echo off
cd /d "%~dp0"
start "" "TwitterAgent-Main.exe"
"@ | Out-File -FilePath "Launch Twitter Agent.bat" -Encoding ASCII

@"
@echo off
cd /d "%~dp0"
start "" "TwitterAgent-Ideator.exe"
"@ | Out-File -FilePath "Launch Content Ideator.bat" -Encoding ASCII

@"
@echo off
cd /d "%~dp0"
start "" "TwitterAgent-APIManager.exe"
"@ | Out-File -FilePath "Launch API Manager.bat" -Encoding ASCII

@"
@echo off
cd /d "%~dp0"
start "" "TwitterAgent-Launcher.exe"
"@ | Out-File -FilePath "Launch Suite.bat" -Encoding ASCII

Set-Location "..\..\"
Write-Host "Shortcuts created." -ForegroundColor Green
Write-Host ""

Write-Host "[6/6] Creating README for distribution..." -ForegroundColor Yellow
$readmeContent = @"
# Twitter Automation Suite

This package contains the complete Twitter Automation Suite for drone content creation.

## Available Applications:

1. TwitterAgent-Launcher.exe  - Main suite launcher (RECOMMENDED)
2. TwitterAgent-Main.exe      - Main Twitter automation interface
3. TwitterAgent-Ideator.exe   - Content ideation tool
4. TwitterAgent-APIManager.exe - API configuration manager

## Quick Start:

1. Double-click "TwitterAgent-Launcher.exe" to start the suite launcher
2. Use the launcher to open individual applications as needed
3. Configure your API keys using the API Manager first
4. Start creating content with the Main Twitter Agent

## Batch Files:

- Launch Suite.bat           - Start the main launcher
- Launch Twitter Agent.bat   - Start main application directly
- Launch Content Ideator.bat - Start ideator tool directly
- Launch API Manager.bat     - Start API manager directly

## Support:

For issues and updates, visit: https://github.com/Pranay1004/Twitter_Agent_Python
"@

$readmeContent | Out-File -FilePath "dist\TwitterAutomationSuite\README.txt" -Encoding UTF8
Write-Host "README created." -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "BUILD COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your Twitter Automation Suite has been built and is ready for distribution!" -ForegroundColor Green
Write-Host ""
Write-Host "Location: dist\TwitterAutomationSuite\" -ForegroundColor Cyan
Write-Host ""
Write-Host "The folder contains:" -ForegroundColor Yellow
Write-Host "- All executable files (.exe)" -ForegroundColor White
Write-Host "- Batch files for easy launching" -ForegroundColor White
Write-Host "- README with instructions" -ForegroundColor White
Write-Host "- All required dependencies" -ForegroundColor White
Write-Host ""
Write-Host "You can now:" -ForegroundColor Yellow
Write-Host "1. Test the applications by running the .exe files" -ForegroundColor White
Write-Host "2. Copy the entire 'TwitterAutomationSuite' folder to any Windows computer" -ForegroundColor White
Write-Host "3. No Python installation required on target machines!" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to open the build folder"
Start-Process "dist\TwitterAutomationSuite"

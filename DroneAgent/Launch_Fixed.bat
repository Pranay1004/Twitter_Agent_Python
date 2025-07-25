@echo off
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

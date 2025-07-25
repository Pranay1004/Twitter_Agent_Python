@echo off
title Twitter Automation Suite
echo.
echo ============================================
echo    Twitter Automation Suite
echo    Complete Twitter Automation in One App
echo ============================================
echo.
echo Starting the unified Twitter Agent GUI...
echo.

cd /d "%~dp0"

if exist "dist\TwitterAgent.exe" (
    start "" "dist\TwitterAgent.exe"
    echo.
    echo TwitterAgent launched successfully!
    echo The GUI window should open shortly.
    echo.
) else (
    echo ERROR: TwitterAgent.exe not found in dist folder
    echo Please make sure the application is properly built.
    echo.
    pause
    exit /b 1
)

echo.
echo You can close this window now.
echo.
timeout /t 5 /nobreak > nul

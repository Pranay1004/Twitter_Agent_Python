@echo off
echo ========================================
echo Twitter Automation Suite - Build Script
echo ========================================
echo.

echo [1/6] Checking Python installation...
python --version
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    pause
    exit /b 1
)
echo.

echo [2/6] Installing required packages...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install requirements!
    pause
    exit /b 1
)
echo.

echo [3/6] Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
echo Build directories cleaned.
echo.

echo [4/6] Building all applications with PyInstaller...
pyinstaller build_all.spec --clean --noconfirm
if %ERRORLEVEL% neq 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)
echo.

echo [5/6] Creating application shortcuts...
cd dist\TwitterAutomationSuite

:: Create batch files for easy launching
echo @echo off > "Launch Twitter Agent.bat"
echo cd /d "%%~dp0" >> "Launch Twitter Agent.bat"
echo start "" "TwitterAgent-Main.exe" >> "Launch Twitter Agent.bat"

echo @echo off > "Launch Content Ideator.bat"
echo cd /d "%%~dp0" >> "Launch Content Ideator.bat"
echo start "" "TwitterAgent-Ideator.exe" >> "Launch Content Ideator.bat"

echo @echo off > "Launch API Manager.bat"
echo cd /d "%%~dp0" >> "Launch API Manager.bat"
echo start "" "TwitterAgent-APIManager.exe" >> "Launch API Manager.bat"

echo @echo off > "Launch Suite.bat"
echo cd /d "%%~dp0" >> "Launch Suite.bat"
echo start "" "TwitterAgent-Launcher.exe" >> "Launch Suite.bat"

cd ..\..
echo.

echo [6/6] Creating README for distribution...
echo # Twitter Automation Suite > dist\TwitterAutomationSuite\README.txt
echo. >> dist\TwitterAutomationSuite\README.txt
echo This package contains the complete Twitter Automation Suite for drone content creation. >> dist\TwitterAutomationSuite\README.txt
echo. >> dist\TwitterAutomationSuite\README.txt
echo ## Available Applications: >> dist\TwitterAutomationSuite\README.txt
echo. >> dist\TwitterAutomationSuite\README.txt
echo 1. TwitterAgent-Launcher.exe  - Main suite launcher ^(RECOMMENDED^) >> dist\TwitterAutomationSuite\README.txt
echo 2. TwitterAgent-Main.exe      - Main Twitter automation interface >> dist\TwitterAutomationSuite\README.txt
echo 3. TwitterAgent-Ideator.exe   - Content ideation tool >> dist\TwitterAutomationSuite\README.txt
echo 4. TwitterAgent-APIManager.exe - API configuration manager >> dist\TwitterAutomationSuite\README.txt
echo. >> dist\TwitterAutomationSuite\README.txt
echo ## Quick Start: >> dist\TwitterAutomationSuite\README.txt
echo. >> dist\TwitterAutomationSuite\README.txt
echo 1. Double-click "TwitterAgent-Launcher.exe" to start the suite launcher >> dist\TwitterAutomationSuite\README.txt
echo 2. Use the launcher to open individual applications as needed >> dist\TwitterAutomationSuite\README.txt
echo 3. Configure your API keys using the API Manager first >> dist\TwitterAutomationSuite\README.txt
echo 4. Start creating content with the Main Twitter Agent >> dist\TwitterAutomationSuite\README.txt
echo. >> dist\TwitterAutomationSuite\README.txt
echo ## Batch Files: >> dist\TwitterAutomationSuite\README.txt
echo. >> dist\TwitterAutomationSuite\README.txt
echo - Launch Suite.bat           - Start the main launcher >> dist\TwitterAutomationSuite\README.txt
echo - Launch Twitter Agent.bat   - Start main application directly >> dist\TwitterAutomationSuite\README.txt
echo - Launch Content Ideator.bat - Start ideator tool directly >> dist\TwitterAutomationSuite\README.txt
echo - Launch API Manager.bat     - Start API manager directly >> dist\TwitterAutomationSuite\README.txt
echo. >> dist\TwitterAutomationSuite\README.txt
echo ## Support: >> dist\TwitterAutomationSuite\README.txt
echo. >> dist\TwitterAutomationSuite\README.txt
echo For issues and updates, visit: https://github.com/Pranay1004/Twitter_Agent_Python >> dist\TwitterAutomationSuite\README.txt

echo.
echo ========================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo Your Twitter Automation Suite has been built and is ready for distribution!
echo.
echo Location: dist\TwitterAutomationSuite\
echo.
echo The folder contains:
echo - All executable files (.exe)
echo - Batch files for easy launching
echo - README with instructions
echo - All required dependencies
echo.
echo You can now:
echo 1. Test the applications by running the .exe files
echo 2. Copy the entire 'TwitterAutomationSuite' folder to any Windows computer
echo 3. No Python installation required on target machines!
echo.
echo Press any key to open the build folder...
pause > nul
start "" "dist\TwitterAutomationSuite"

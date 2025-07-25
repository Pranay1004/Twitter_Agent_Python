@echo off
echo ========================================
echo Building Twitter Automation Suite
echo ========================================

echo Installing requirements...
python -m pip install -r requirements.txt

rem Build main application
echo Building main application...
pyinstaller --clean --noconfirm main.spec
if %errorlevel% neq 0 (
    echo Failed to build main application
    exit /b %errorlevel%
)

rem Build content ideator
echo Building content ideator...
pyinstaller --clean --noconfirm ideator.spec
if %errorlevel% neq 0 (
    echo Failed to build ideator
    exit /b %errorlevel%
)

rem Build API manager
echo Building API manager...
pyinstaller --clean --noconfirm api_manager.spec
if %errorlevel% neq 0 (
    echo Failed to build API manager
    exit /b %errorlevel%
)

rem Build launcher last
echo Building launcher...
pyinstaller --clean --noconfirm launcher.spec
if %errorlevel% neq 0 (
    echo Failed to build launcher
    exit /b %errorlevel%
)

echo.
echo ========================================
echo BUILD COMPLETE!
echo ========================================
echo Your executables are in the 'dist' folder:
echo - TwitterAgent-Launcher.exe (Main launcher)
echo - TwitterAgent-Main.exe (Main app)
echo - TwitterAgent-Ideator.exe (Content ideator)
echo - TwitterAgent-APIManager.exe (API manager)
echo.
echo Remember to:
echo 1. Configure your API keys using API Manager
echo 2. Start with TwitterAgent-Launcher.exe
echo 3. Keep all executables in the same folder

pause

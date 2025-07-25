@echo off
echo ========================================
echo Building Twitter Automation Suite
echo ========================================

:: Install requirements
echo Installing requirements...
pip install -r requirements.txt

:: Clean previous builds
echo Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

:: Create dist directory
mkdir dist

:: Build main launcher (most important)
echo Building main launcher...
pyinstaller launcher.spec --clean --noconfirm
move "dist\TwitterAgent-Launcher.exe" "dist\TwitterAgent-Launcher-temp.exe"

:: Build main GUI
echo Building main Twitter agent...
pyinstaller main_gui.spec --clean --noconfirm
move "dist\TwitterAgent-Main.exe" "dist\TwitterAgent-Main-temp.exe"

:: Build content ideator
echo Building content ideator...
pyinstaller gui_ideator.py --onefile --windowed --name "TwitterAgent-Ideator" --add-data "utils/;utils/" --add-data "agent/;agent/" --add-data ".env;."

:: Build API manager  
echo Building API manager...
pyinstaller gui_api_manager.py --onefile --windowed --name "TwitterAgent-APIManager" --add-data "utils/;utils/" --add-data ".env;."

:: Move main files back
move "dist\TwitterAgent-Launcher-temp.exe" "dist\TwitterAgent-Launcher.exe"
move "dist\TwitterAgent-Main-temp.exe" "dist\TwitterAgent-Main.exe"

:: Create batch shortcuts
echo Creating shortcuts...
cd dist

echo @echo off > "Launch Suite.bat"
echo start "" "TwitterAgent-Launcher.exe" >> "Launch Suite.bat"

echo @echo off > "Launch Main App.bat"
echo start "" "TwitterAgent-Main.exe" >> "Launch Main App.bat"

echo @echo off > "Launch Ideator.bat"
echo start "" "TwitterAgent-Ideator.exe" >> "Launch Ideator.bat"

echo @echo off > "Launch API Manager.bat"
echo start "" "TwitterAgent-APIManager.exe" >> "Launch API Manager.bat"

cd ..

echo.
echo ========================================
echo BUILD COMPLETE!
echo ========================================
echo.
echo Your executables are in the 'dist' folder:
echo - TwitterAgent-Launcher.exe (Main launcher)
echo - TwitterAgent-Main.exe (Main app)
echo - TwitterAgent-Ideator.exe (Content ideator)
echo - TwitterAgent-APIManager.exe (API manager)
echo.
echo Batch files for easy launching:
echo - Launch Suite.bat (Recommended)
echo - Launch Main App.bat
echo - Launch Ideator.bat
echo - Launch API Manager.bat
echo.
pause

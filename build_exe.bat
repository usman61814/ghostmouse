@echo off
echo ==========================================
echo Building GhostMouse Standalone Executable
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Install PyInstaller if not already installed
echo Installing PyInstaller...
pip install pyinstaller -q

REM Clean old builds
echo Cleaning old builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build the executable
echo.
echo Building executable... This may take a few minutes.
echo.

pyinstaller --noconfirm --onefile --windowed --icon=winrar.ico --name "GhostMouse" --add-data "config.json;." --add-data "winrar.ico;." --hidden-import=pyautogui --hidden-import=pynput --hidden-import=pystray --hidden-import=PIL --hidden-import=PIL.Image --hidden-import=PIL.ImageDraw --hidden-import=keyboard --hidden-import=tkinter --hidden-import=tkinter.ttk --hidden-import=tkinter.messagebox main.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

REM Create final package folder
echo.
echo Creating package...
if not exist "GhostMouse_Portable" mkdir "GhostMouse_Portable"
xcopy /y "dist\GhostMouse.exe" "GhostMouse_Portable\" >nul
xcopy /y "config.json" "GhostMouse_Portable\" >nul 2>nul
xcopy /y "winrar.ico" "GhostMouse_Portable\" >nul 2>nul

echo.
echo ==========================================
echo Build Complete!
echo ==========================================
echo.
echo Your portable app is in: GhostMouse_Portable\
echo.
echo To use on another PC:
echo 1. Copy the "GhostMouse_Portable" folder
echo 2. Paste it on the other PC
echo 3. Double-click GhostMouse.exe
echo.
pause

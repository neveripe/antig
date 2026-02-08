@echo off
REM Build script for creating Windows executable
REM Usage: build_exe.bat

echo ========================================
echo Energy Stats Processor - Build Script
echo ========================================
echo.

echo [1/3] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo Done!
echo.

echo [2/3] Building executable with PyInstaller...
python -m PyInstaller energy-processor.spec
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed!
    echo Make sure PyInstaller is installed: pip install pyinstaller
    pause
    exit /b 1
)
echo Done!
echo.

echo [3/3] Build completed successfully!
echo.
echo Executable location: dist\energy-processor.exe
echo Size: 
dir dist\energy-processor.exe | find "energy-processor.exe"
echo.

echo ========================================
echo Build Complete!
echo ========================================
echo.
echo To test the executable:
echo   dist\energy-processor.exe --help
echo.
pause

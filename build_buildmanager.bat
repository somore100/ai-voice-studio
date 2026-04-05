@echo off
title Building BuildManager.exe
echo.
echo Building BuildManager.exe - please wait...
echo.
py -3.10 -m pip install pyinstaller >nul 2>&1
py -3.10 -m PyInstaller build_manager.spec --clean --noconfirm
if %ERRORLEVEL% NEQ 0 (
    echo FAILED - check errors above
    pause
    exit /b 1
)
echo.
echo Done! Find it at: dist\BuildManager\BuildManager.exe
echo Copy BuildManager.exe next to your project files and run it.
echo.
pause

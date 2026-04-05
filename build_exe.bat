@echo off
title AI Voice Studio - Builder

echo.
echo  AI Voice Studio - Build Script
echo  by domore100
echo.

echo Step 1 of 3 - EXE Options
echo -----------------------------------------
echo Should the app show a console window?
echo.
echo [1]  No console  (clean UI - recommended for release)
echo [2]  Yes console (shows errors - useful for debugging)
echo.
set /p CHOICE=Your choice (1 or 2): 
if "%CHOICE%"=="2" (
    set AVS_CONSOLE=1
    echo Building WITH console...
) else (
    set AVS_CONSOLE=0
    echo Building WITHOUT console...
)
echo.

echo Step 2 of 3 - Building EXE
echo -----------------------------------------
echo Installing PyInstaller if needed...
py -3.10 -m pip install pyinstaller >nul 2>&1

echo Running PyInstaller...
echo.
py -3.10 -m PyInstaller ai_voice_studio.spec --clean --noconfirm

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo EXE BUILD FAILED - check errors above
    pause
    exit /b 1
)

echo.
echo EXE built: dist\AI_Voice_Studio\AI_Voice_Studio.exe
echo.

echo Step 3 of 3 - Compiling Installers
echo -----------------------------------------

set ISCC=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set ISCC="C:\Program Files\Inno Setup 6\ISCC.exe"

if "%ISCC%"=="" (
    echo Inno Setup not found.
    echo Download from: https://jrsoftware.org/isdl.php
    echo Then run these manually:
    echo   ISCC.exe installer_public.iss
    echo   ISCC.exe installer_dev.iss
    goto done
)

if not exist dev_setup mkdir dev_setup
echo Compiling DEV installer...
%ISCC% installer_dev.iss
if %ERRORLEVEL% EQU 0 echo Dev installer ready: dev_setup\AI_Voice_Studio_Dev_Setup.exe

echo.
echo Compiling PUBLIC installer...
if not exist setup_output mkdir setup_output
%ISCC% installer_public.iss
if %ERRORLEVEL% NEQ 0 (
    echo PUBLIC INSTALLER FAILED - check errors above
    pause
    exit /b 1
)

:done
echo.
echo ALL DONE!
echo Public installer: setup_output\AI_Voice_Studio_Setup_v1.0.exe
echo Dev installer:    dev_setup\AI_Voice_Studio_Dev_Setup.exe
echo.
pause

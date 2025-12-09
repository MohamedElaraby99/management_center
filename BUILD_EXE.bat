@echo off
chcp 65001 >nul
title بناء ملف EXE - Build Executable

echo.
echo ╔═══════════════════════════════════════════════════════╗
echo ║          Building EXE File - إنشاء ملف تنفيذي        ║
echo ║                    Version 2.2                        ║
echo ╚═══════════════════════════════════════════════════════╝
echo.

REM Check if Python exists
python --version >nul 2>&1
if %errorlevel% NEQ 0 (
    python3 --version >nul 2>&1
    if %errorlevel% NEQ 0 (
        echo [✗] خطأ: Python غير مثبت!
        echo [✗] Error: Python is not installed!
        echo.
        pause
        exit /b 1
    )
    set PYTHON_CMD=python3
) else (
    set PYTHON_CMD=python
)

echo [✓] Python موجود! / Python found!
echo.

REM Run the build script
%PYTHON_CMD% build_exe.py

exit /b %errorlevel%



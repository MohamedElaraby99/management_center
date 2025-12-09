@echo off
chcp 65001 >nul
title نظام إدارة الطلبة - Student Management System

echo.
echo ╔═══════════════════════════════════════════════════════╗
echo ║     نظام إدارة الطلبة - Student Management System    ║
echo ║                  Version 2.2 - Modern UI             ║
echo ╚═══════════════════════════════════════════════════════╝
echo.
echo [*] جاري تشغيل البرنامج...
echo [*] Starting the application...
echo.

REM Try python command first
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo [✓] Python found!
    echo [*] Launching Student Manager...
    echo.
    python student_manager.py
    goto :end
)

REM Try python3 command
python3 --version >nul 2>&1
if %errorlevel% == 0 (
    echo [✓] Python3 found!
    echo [*] Launching Student Manager...
    echo.
    python3 student_manager.py
    goto :end
)

REM Python not found
echo [✗] خطأ: Python غير مثبت على الجهاز!
echo [✗] Error: Python is not installed!
echo.
echo [!] يرجى تثبيت Python 3.7 أو أحدث من:
echo [!] Please install Python 3.7+ from:
echo     https://www.python.org/downloads/
echo.
echo [!] تأكد من تفعيل خيار "Add Python to PATH" أثناء التثبيت
echo [!] Make sure to check "Add Python to PATH" during installation
echo.
pause
goto :end

:end
if %errorlevel% NEQ 0 (
    echo.
    echo [✗] حدث خطأ أثناء تشغيل البرنامج!
    echo [✗] An error occurred while running the program!
    echo.
    pause
)


@echo off
echo ================================================
echo     بناء برنامج ادارة الطلبة - نسخة بسيطة
echo ================================================
echo.

REM التحقق من PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [*] PyInstaller غير مثبت، جاري التثبيت...
    pip install pyinstaller
) else (
    echo [+] PyInstaller مثبت مسبقا
)

echo.
echo [*] جاري بناء التطبيق...
echo.

REM البناء بدون أيقونة
pyinstaller --onefile --windowed --name=StudentManager --clean student_manager.py

if errorlevel 1 (
    echo.
    echo [X] فشل البناء!
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================
echo     تم البناء بنجاح!
echo ================================================
echo.
echo الملف التنفيذي موجود في: dist\StudentManager.exe
echo.
echo يمكنك الآن:
echo   1. تشغيل dist\StudentManager.exe مباشرة
echo   2. نسخه لأي مكان وتشغيله
echo   3. توزيعه على المستخدمين
echo.
pause


#!/bin/bash

# نظام إدارة الطلبة - Student Management System
# Version 2.2 - Modern UI
# Portable Edition

clear

echo "╔═══════════════════════════════════════════════════════╗"
echo "║     نظام إدارة الطلبة - Student Management System    ║"
echo "║                  Version 2.2 - Modern UI             ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
echo "[*] جاري تشغيل البرنامج..."
echo "[*] Starting the application..."
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Try python3 first (recommended on Unix systems)
if command_exists python3; then
    echo "[✓] Python3 found!"
    echo "[*] Launching Student Manager..."
    echo ""
    python3 student_manager.py
    exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        echo ""
        echo "[✗] حدث خطأ أثناء تشغيل البرنامج!"
        echo "[✗] An error occurred while running the program!"
        echo ""
        read -p "اضغط Enter للإغلاق / Press Enter to close..."
    fi
    exit $exit_code
fi

# Try python command
if command_exists python; then
    # Check if it's Python 3
    python_version=$(python --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
    major_version=$(echo $python_version | cut -d. -f1)
    
    if [ "$major_version" -ge 3 ]; then
        echo "[✓] Python found!"
        echo "[*] Launching Student Manager..."
        echo ""
        python student_manager.py
        exit_code=$?
        
        if [ $exit_code -ne 0 ]; then
            echo ""
            echo "[✗] حدث خطأ أثناء تشغيل البرنامج!"
            echo "[✗] An error occurred while running the program!"
            echo ""
            read -p "اضغط Enter للإغلاق / Press Enter to close..."
        fi
        exit $exit_code
    else
        echo "[✗] خطأ: يتطلب Python 3.7 أو أحدث!"
        echo "[✗] Error: Python 3.7+ is required!"
        echo "[!] النسخة الحالية: $python_version"
        echo "[!] Current version: $python_version"
        echo ""
        echo "[!] يرجى تحديث Python من:"
        echo "[!] Please update Python from:"
        echo "    https://www.python.org/downloads/"
        echo ""
        read -p "اضغط Enter للإغلاق / Press Enter to close..."
        exit 1
    fi
fi

# Python not found
echo "[✗] خطأ: Python غير مثبت على الجهاز!"
echo "[✗] Error: Python is not installed!"
echo ""
echo "[!] يرجى تثبيت Python 3.7 أو أحدث:"
echo "[!] Please install Python 3.7+:"
echo ""
echo "    Ubuntu/Debian: sudo apt-get install python3 python3-tk"
echo "    Fedora/RedHat: sudo dnf install python3 python3-tkinter"
echo "    Mac OS X:      brew install python3"
echo "    Or download:   https://www.python.org/downloads/"
echo ""
echo "[!] إذا كان Python مثبت، تأكد من وجوده في PATH"
echo "[!] If Python is installed, make sure it's in your PATH"
echo ""
read -p "اضغط Enter للإغلاق / Press Enter to close..."
exit 1



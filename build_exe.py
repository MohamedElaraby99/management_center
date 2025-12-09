#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Executable File - إنشاء ملف تنفيذي
Creates a standalone .exe file using PyInstaller
"""

import os
import sys
import subprocess

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_pyinstaller():
    """التحقق من تثبيت PyInstaller"""
    try:
        import PyInstaller
        print("[OK] PyInstaller found!")
        return True
    except ImportError:
        print("[X] PyInstaller not installed!")
        print()
        return False

def install_pyinstaller():
    """تثبيت PyInstaller"""
    print("[*] Installing PyInstaller...")
    print()
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print()
        print("[OK] PyInstaller installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print()
        print("[X] Failed to install PyInstaller!")
        return False

def build_executable():
    """إنشاء ملف EXE"""
    print()
    print("=" * 60)
    print("     Building Executable File - EXE")
    print("=" * 60)
    print()
    
    # التحقق من PyInstaller
    if not check_pyinstaller():
        print("[?] Do you want to install PyInstaller now?")
        response = input("[Y/n]: ").strip().lower()
        
        if response in ['', 'y', 'yes']:
            if not install_pyinstaller():
                print()
                print("[!] Please install PyInstaller manually:")
                print("    pip install pyinstaller")
                return False
        else:
            return False
    
    print()
    print("[*] Building EXE file...")
    print("[!] This may take several minutes, please wait...")
    print()
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single file
        "--windowed",                   # No console window
        "--name=StudentManager",        # File name
        "--icon=NONE",                  # No icon
        "--clean",                      # Clean old files
        "student_manager.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print()
        print("=" * 60)
        print("               SUCCESS!")
        print("=" * 60)
        print()
        print("[OK] Executable file created successfully!")
        print()
        print("[*] Output folders:")
        print()
        print("    dist/")
        print("       StudentManager.exe    <- Final executable file")
        print()
        print("    build/                   <- Temporary files (can delete)")
        print("    StudentManager.spec      <- Config file (can delete)")
        print()
        print("=" * 60)
        print()
        print("[*] How to use:")
        print()
        print("1. Copy StudentManager.exe from dist/ folder")
        print("2. Put it in any folder you want")
        print("3. Double-click to run directly!")
        print("4. Database will be created automatically")
        print()
        print("=" * 60)
        print()
        print("[*] Important notes:")
        print()
        print("OK 100% Portable - No Python needed")
        print("OK Transfer via USB or to another computer")
        print("OK Local and secure database")
        print("!! File may be large (50-100 MB)")
        print("!! Windows Defender may show warning (normal)")
        print()
        
        # Open dist folder
        if os.path.exists("dist"):
            print("[?] Do you want to open dist/ folder now?")
            response = input("[Y/n]: ").strip().lower()
            
            if response in ['', 'y', 'yes']:
                if sys.platform == 'win32':
                    os.startfile("dist")
                elif sys.platform == 'darwin':  # macOS
                    subprocess.call(['open', 'dist'])
                else:  # Linux
                    subprocess.call(['xdg-open', 'dist'])
        
        return True
        
    except subprocess.CalledProcessError as e:
        print()
        print("[X] Failed to build executable!")
        print()
        print(f"[!] Error: {e}")
        print()
        return False
    except FileNotFoundError:
        print()
        print("[X] PyInstaller not found in PATH!")
        print()
        print("[!] Try restarting Terminal/CMD after installing PyInstaller")
        return False

def main():
    print()
    print("=" * 60)
    print("       Student Management System")
    print("           EXE Builder")
    print("            Version 2.2")
    print("=" * 60)
    
    if not os.path.exists("student_manager.py"):
        print()
        print("[X] Error: student_manager.py not found!")
        print()
        print("[!] Make sure to run this script in the same folder")
        print("    as student_manager.py")
        print()
        input("Press Enter to exit...")
        return
    
    success = build_executable()
    
    print()
    if success:
        print("[SUCCESS] Done! You can now use the file from dist/ folder")
    else:
        print("[ERROR] An error occurred. Please check the messages above.")
    
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()

"""
سكربت لبناء تطبيق سطح المكتب
"""
import os
import sys
import subprocess

def build_desktop_app():
    """بناء التطبيق باستخدام PyInstaller"""
    
    print("=" * 60)
    print("بناء برنامج إدارة الطلبة والمجموعات")
    print("=" * 60)
    
    # التحقق من تثبيت PyInstaller
    try:
        import PyInstaller
        print("✓ PyInstaller مثبت بالفعل")
    except ImportError:
        print("! PyInstaller غير مثبت")
        print("جاري التثبيت...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ تم تثبيت PyInstaller")
    
    # التحقق من Pillow إذا كانت الأيقونة موجودة
    use_icon = False
    if os.path.exists("app_icon.ico"):
        try:
            import PIL
            use_icon = True
            print("✓ Pillow مثبت، سيتم استخدام الأيقونة المخصصة")
        except ImportError:
            print("⚠ Pillow غير مثبت")
            response = input("هل تريد تثبيت Pillow لاستخدام أيقونة مخصصة؟ (y/n): ")
            if response.lower() == 'y':
                print("جاري تثبيت Pillow...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
                use_icon = True
                print("✓ تم تثبيت Pillow")
            else:
                print("⚠ سيتم استخدام الأيقونة الافتراضية")
    
    # أوامر PyInstaller
    pyinstaller_command = [
        "pyinstaller",
        "--onefile",  # ملف واحد
        "--windowed",  # بدون نافذة console
        "--name=StudentManager",  # اسم التطبيق
        "--clean",  # تنظيف الملفات القديمة
        "student_manager.py"
    ]
    
    # إضافة الأيقونة إذا كانت متاحة
    if use_icon:
        pyinstaller_command.insert(4, "--icon=app_icon.ico")
    
    print("\nجاري البناء...")
    try:
        subprocess.check_call(pyinstaller_command)
        print("\n" + "=" * 60)
        print("✓ تم البناء بنجاح!")
        print("=" * 60)
        print("\nالملف التنفيذي موجود في:")
        print("  dist/StudentManager.exe")
        print("\nيمكنك تشغيله مباشرة أو إنشاء installer له")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ فشل البناء: {e}")
        return False
    
    return True

if __name__ == "__main__":
    build_desktop_app()


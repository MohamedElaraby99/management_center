#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
برنامج إدارة الطلبة والمجموعات
Desktop Application - Python + Tkinter + SQLite
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, date, timedelta
import os
import json


class StudentManagementDB:
    """إدارة قاعدة البيانات SQLite"""
    
    def __init__(self, db_name="student_management.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """الاتصال بقاعدة البيانات"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        """إنشاء الجداول الأساسية"""
        
        # جدول الطلبة
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول المعلمين
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                specialization TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول المجموعات
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                subject TEXT,
                teacher TEXT,
                schedule TEXT,
                fee REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول ربط الطلبة بالمجموعات
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
                UNIQUE(student_id, group_id)
            )
        """)
        
        # جدول الدفعات
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
            )
        """)
        
        # جدول الحضور والغياب
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                attendance_date DATE NOT NULL,
                status TEXT CHECK(status IN ('حاضر', 'غائب', 'غياب بعذر')) DEFAULT 'حاضر',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
                UNIQUE(student_id, group_id, attendance_date)
            )
        """)
        
        # جدول الإشعارات
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                group_id INTEGER,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read INTEGER DEFAULT 0,
                priority TEXT DEFAULT 'normal',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
            )
        """)
        
        # جدول إعدادات الإشعارات
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notification_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT NOT NULL
            )
        """)
        
        # إدراج الإعدادات الافتراضية
        self.cursor.execute("""
            INSERT OR IGNORE INTO notification_settings (setting_key, setting_value)
            VALUES 
                ('payment_reminder_days', '7'),
                ('show_notifications_on_startup', '1'),
                ('payment_alert_enabled', '1'),
                ('attendance_milestone_enabled', '1'),
                ('attendance_milestone_count', '4')
        """)
        
        self.conn.commit()
    
    def execute_query(self, query, params=()):
        """تنفيذ استعلام"""
        self.cursor.execute(query, params)
        self.conn.commit()
        return self.cursor.lastrowid
    
    def fetch_all(self, query, params=()):
        """جلب جميع النتائج"""
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def fetch_one(self, query, params=()):
        """جلب نتيجة واحدة"""
        self.cursor.execute(query, params)
        return self.cursor.fetchone()
    
    def close(self):
        """إغلاق الاتصال"""
        if self.conn:
            self.conn.close()


class StudentManagementApp:
    """التطبيق الرئيسي - واجهة Tkinter"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 برنامج إدارة الطلبة والمجموعات")
        self.root.geometry("1440x900")
        self.root.state('zoomed')  # Start maximized
        self.root.minsize(1200, 700)
        
        # Current active page
        self.current_page = None
        
        # Modern Icons Dictionary
        self.icons = {
            'student': '👤',
            'students': '👥',
            'group': '📚',
            'groups': '📖',
            'enrollment': '✍️',
            'payment': '💰',
            'payments': '💳',
            'attendance': '✅',
            'absent': '❌',
            'notification': '🔔',
            'notifications': '🔕',
            'reports': '📊',
            'chart': '📈',
            'add': '➕',
            'edit': '✏️',
            'delete': '🗑️',
            'clear': '🔄',
            'search': '🔍',
            'filter': '🔎',
            'save': '💾',
            'cancel': '✖️',
            'check': '✔️',
            'settings': '⚙️',
            'calendar': '📅',
            'phone': '📱',
            'email': '📧',
            'home': '🏠',
            'info': 'ℹ️',
            'warning': '⚠️',
            'success': '✓',
            'stats': '📊',
            'refresh': '🔄',
            'close': '✕',
            'menu': '☰',
            'print': '🖨️',
            'export': '📤',
            'import': '📥',
            'help': '❓',
            'star': '⭐',
            'flag': '🚩'
        }
        
        # تفعيل RTL للغة العربية
        self.setup_rtl()
        
        # قاعدة البيانات
        self.db = StudentManagementDB()
        
        # إعداد الواجهة
        self.setup_ui()
        
        # تفعيل النسخ واللصق
        self.setup_copy_paste()
    
    def setup_rtl(self):
        """إعداد RTL (Right to Left) للغة العربية"""
        try:
            # محاولة تفعيل RTL على Windows
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        except:
            pass
    
    def setup_copy_paste(self):
        """تفعيل النسخ واللصق عبر التطبيق"""
        # إنشاء قائمة سياقية للنسخ واللصق
        self.context_menu = tk.Menu(self.root, tearoff=0, font=('Segoe UI', 12))
        self.context_menu.add_command(label="📋 نسخ", command=self.copy_text, accelerator="Ctrl+C")
        self.context_menu.add_command(label="📋 لصق", command=self.paste_text, accelerator="Ctrl+V")
        self.context_menu.add_command(label="✂️ قص", command=self.cut_text, accelerator="Ctrl+X")
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🔘 تحديد الكل", command=self.select_all, accelerator="Ctrl+A")
        
        # ربط اختصارات لوحة المفاتيح
        self.root.bind_all("<Control-c>", lambda e: self.copy_text())
        self.root.bind_all("<Control-v>", lambda e: self.paste_text())
        self.root.bind_all("<Control-x>", lambda e: self.cut_text())
        self.root.bind_all("<Control-a>", lambda e: self.select_all())
        
        # ربط النقر بزر الفأرة الأيمن لإظهار القائمة السياقية
        self.root.bind_all("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        """عرض قائمة النسخ واللصق السياقية"""
        try:
            # تركيز العنصر الذي تم النقر عليه
            event.widget.focus_set()
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def copy_text(self):
        """نسخ النص المحدد"""
        try:
            widget = self.root.focus_get()
            if widget:
                # للـ Entry و Combobox
                if hasattr(widget, 'selection_present') and widget.selection_present():
                    try:
                        text = widget.selection_get()
                        self.root.clipboard_clear()
                        self.root.clipboard_append(text)
                    except:
                        pass
                # للـ Text widgets
                elif hasattr(widget, 'tag_ranges') and widget.tag_ranges('sel'):
                    try:
                        text = widget.get('sel.first', 'sel.last')
                        self.root.clipboard_clear()
                        self.root.clipboard_append(text)
                    except:
                        pass
        except:
            pass
    
    def paste_text(self):
        """لصق النص من الحافظة"""
        try:
            widget = self.root.focus_get()
            if widget:
                try:
                    text = self.root.clipboard_get()
                    
                    # للـ Entry و Combobox
                    if hasattr(widget, 'selection_present'):
                        if widget.selection_present():
                            # حذف النص المحدد أولاً
                            try:
                                widget.delete('sel.first', 'sel.last')
                            except:
                                pass
                        # إدراج النص في موقع المؤشر
                        widget.insert('insert', text)
                    # للـ Text widgets
                    elif hasattr(widget, 'tag_ranges'):
                        if widget.tag_ranges('sel'):
                            try:
                                widget.delete('sel.first', 'sel.last')
                            except:
                                pass
                        widget.insert('insert', text)
                except tk.TclError:
                    pass
        except:
            pass
    
    def cut_text(self):
        """قص النص المحدد"""
        try:
            widget = self.root.focus_get()
            if widget:
                # للـ Entry و Combobox
                if hasattr(widget, 'selection_present') and widget.selection_present():
                    try:
                        text = widget.selection_get()
                        self.root.clipboard_clear()
                        self.root.clipboard_append(text)
                        widget.delete('sel.first', 'sel.last')
                    except:
                        pass
                # للـ Text widgets
                elif hasattr(widget, 'tag_ranges') and widget.tag_ranges('sel'):
                    try:
                        text = widget.get('sel.first', 'sel.last')
                        self.root.clipboard_clear()
                        self.root.clipboard_append(text)
                        widget.delete('sel.first', 'sel.last')
                    except:
                        pass
        except:
            pass
    
    def select_all(self):
        """تحديد كل النص"""
        try:
            widget = self.root.focus_get()
            if widget:
                # للـ Entry و Combobox
                if hasattr(widget, 'select_range'):
                    widget.select_range(0, 'end')
                    widget.icursor('end')
                # للـ Text widgets
                elif hasattr(widget, 'tag_add'):
                    widget.tag_add('sel', '1.0', 'end-1c')
        except:
            pass
    
    def create_desktop_shortcut(self):
        """إنشاء اختصار على سطح المكتب"""
        try:
            import sys
            import os
            import subprocess
            
            # الحصول على مسار سطح المكتب بطريقة موثوقة على Windows
            # استخدام متغير البيئة USERPROFILE للحصول على مسار المستخدم الصحيح
            user_profile = os.environ.get('USERPROFILE', os.path.expanduser('~'))
            desktop = os.path.join(user_profile, "Desktop")
            
            # التحقق من وجود مجلد سطح المكتب
            if not os.path.exists(desktop):
                # محاولة استخدام OneDrive Desktop إذا كان موجوداً
                onedrive_desktop = os.path.join(user_profile, "OneDrive", "Desktop")
                if os.path.exists(onedrive_desktop):
                    desktop = onedrive_desktop
                else:
                    # إنشاء المجلد إذا لم يكن موجوداً
                    os.makedirs(desktop, exist_ok=True)
            
            # تحديد مسار البرنامج
            if getattr(sys, 'frozen', False):
                # إذا كان البرنامج مجمع كـ exe
                app_path = sys.executable
                target_path = app_path
                arguments = ""
            else:
                # إذا كان يعمل كسكريبت Python
                app_path = os.path.abspath(__file__)
                target_path = sys.executable  # استخدام مسار Python الفعلي
                arguments = f'"{app_path}"'
            
            app_dir = os.path.dirname(app_path)
            shortcut_path = os.path.join(desktop, "StudentManager.lnk")
            
            # البحث عن الأيقونة في عدة أماكن
            icon_path = None
            possible_icon_paths = [
                os.path.join(app_dir, "app_icon.ico"),
                os.path.join(os.getcwd(), "app_icon.ico"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon.ico"),
                os.path.join(app_dir, "..", "app_icon.ico"),  # parent directory
            ]
            
            for path in possible_icon_paths:
                if os.path.exists(path):
                    icon_path = os.path.abspath(path)
                    break
            
            # استخدام PowerShell لإنشاء اختصار .lnk حقيقي
            # تضمين علامات الاقتباس المزدوجة للمسارات
            ps_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{target_path}"
$Shortcut.Arguments = '{arguments}'
$Shortcut.WorkingDirectory = "{app_dir}"
$Shortcut.Description = "Student Manager App"
'''
            # إضافة الأيقونة إذا كانت موجودة
            if icon_path:
                ps_script += f'$Shortcut.IconLocation = "{icon_path}"\n'
            elif getattr(sys, 'frozen', False):
                # إذا كان EXE، استخدم الـ EXE نفسه كأيقونة
                ps_script += f'$Shortcut.IconLocation = "{target_path}"\n'
            
            ps_script += '$Shortcut.Save()'
            
            # تنفيذ PowerShell
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                messagebox.showinfo("تم بنجاح", 
                    "تم إنشاء الاختصار على سطح المكتب بنجاح!\n\n"
                    f"الاختصار: {shortcut_path}")
            else:
                raise Exception(result.stderr)
                
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل إنشاء الاختصار:\n{str(e)}")
    
    def create_modern_button(self, parent, text, command, style='primary', icon=''):
        """إنشاء زر حديث مع تأثيرات hover"""
        colors = {
            'primary': (self.colors['primary'], self.colors['primary_dark'], 'white'),
            'success': (self.colors['success'], '#059669', 'white'),
            'danger': (self.colors['danger'], '#DC2626', 'white'),
            'warning': (self.colors['warning'], '#D97706', 'white'),
            'secondary': (self.colors['text_secondary'], self.colors['text'], 'white'),
            'info': (self.colors['info'], '#2563EB', 'white')
        }
        
        bg, hover_bg, fg = colors.get(style, colors['primary'])
        button_text = f"{icon} {text}" if icon else text
        
        btn = tk.Button(parent, text=button_text, bg=bg, fg=fg,
                       font=('Segoe UI', 13, 'bold'), padx=25, pady=12,
                       border=0, cursor='hand2', relief='flat',
                       activebackground=hover_bg, activeforeground=fg,
                       command=command)
        
        # تأثير hover
        def on_enter(e):
            btn['background'] = hover_bg
        
        def on_leave(e):
            btn['background'] = bg
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def create_modern_card(self, parent, title='', subtitle=''):
        """إنشاء بطاقة حديثة مع ظل"""
        # Outer frame for shadow effect
        shadow_frame = tk.Frame(parent, bg=self.colors['border'], bd=0)
        
        # Card frame
        card = tk.Frame(shadow_frame, bg=self.colors['card'], bd=0)
        card.pack(padx=1, pady=1, fill=tk.BOTH, expand=True)
        
        if title:
            header = tk.Frame(card, bg=self.colors['card'])
            header.pack(fill=tk.X, padx=25, pady=(20, 10))
            
            tk.Label(header, text=title,
                    bg=self.colors['card'],
                    fg=self.colors['text'],
                    font=('Segoe UI', 18, 'bold')).pack(anchor=tk.E)
            
            if subtitle:
                tk.Label(header, text=subtitle,
                        bg=self.colors['card'],
                        fg=self.colors['text_secondary'],
                        font=('Segoe UI', 14)).pack(anchor=tk.E, pady=(2, 0))
            
            # Separator line
            tk.Frame(card, bg=self.colors['border'], height=1).pack(fill=tk.X, padx=25, pady=(10, 0))
        
        return shadow_frame, card
    
    def create_modern_input(self, parent, label_text, icon='', width=30):
        """إنشاء حقل إدخال حديث مع أيقونة - RTL"""
        container = tk.Frame(parent, bg=self.colors['card'])
        
        # Label مع أيقونة
        label_frame = tk.Frame(container, bg=self.colors['card'])
        label_frame.pack(side=tk.RIGHT, padx=(0, 15))
        
        if icon:
            tk.Label(label_frame, text=icon,
                    bg=self.colors['card'],
                    fg=self.colors['primary'],
                    font=('Segoe UI', 14)).pack(side=tk.RIGHT, padx=(5, 0))
        
        tk.Label(label_frame, text=label_text,
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 12, 'bold')).pack(side=tk.RIGHT)
        
        # Entry field مع تصميم حديث
        entry_frame = tk.Frame(container, bg=self.colors['border'], bd=0)
        entry_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        entry = tk.Entry(entry_frame,
                        font=('Segoe UI', 14),
                        bd=0,
                        relief='flat',
                        bg=self.colors['card'],
                        fg=self.colors['text'],
                        insertbackground=self.colors['primary'],
                        width=width,
                        justify='right')  # RTL alignment
        entry.pack(padx=1, pady=1, ipady=8, ipadx=10)
        
        # Hover effect
        def on_focus_in(e):
            entry_frame.config(bg=self.colors['primary'])
        
        def on_focus_out(e):
            entry_frame.config(bg=self.colors['border'])
        
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)
        
        return container, entry
    
    def get_id_from_combo(self, text):
        """استخراج ID من نص القائمة المنسدلة"""
        try:
            if " - " in text:
                return int(text.split(" - ")[0])
            return None
        except:
            return None

    def enable_search(self, combo):
        """تفعيل البحث في القائمة المنسدلة"""
        combo.configure(state='normal')
        combo.bind('<KeyRelease>', self.on_combo_key_release)
        combo.bind('<FocusOut>', self.on_combo_focus_out)
        combo.all_values = []
        
    def on_combo_focus_out(self, event):
        """استعادة القيم عند الخروج"""
        combo = event.widget
        if hasattr(combo, 'all_values') and combo.all_values:
            current = combo.get()
            # Restore all values but keep current text
            combo['values'] = combo.all_values
            
    def on_combo_key_release(self, event):
        """تصفية القائمة عند الكتابة"""
        combo = event.widget
        if event.keysym in ['Up', 'Down', 'Return', 'Left', 'Right', 'Tab']:
            return
            
        value = combo.get().lower()
        if not hasattr(combo, 'all_values'):
            return
            
        if value == '':
            combo['values'] = combo.all_values
        else:
            filtered_data = []
            for item in combo.all_values:
                if value in item.lower():
                    filtered_data.append(item)
            combo['values'] = filtered_data
            
        # فتح القائمة تلقائياً إذا وجدت نتائج
        try:
            if combo['values']:
                combo.event_generate('<Down>')
        except:
            pass
    
    def create_nav_button(self, parent, text, icon, command, key):
        """إنشاء زر تنقل في الشريط الجانبي"""
        btn_frame = tk.Frame(parent, bg=self.colors['card'])
        
        btn = tk.Button(btn_frame,
                       text=f"  {icon}  {text}  ",
                       bg=self.colors['card'],
                       fg=self.colors['text'],
                       font=('Segoe UI', 15),
                       bd=0,
                       relief='flat',
                       cursor='hand2',
                       anchor='e',  # RTL align
                       padx=20,
                       pady=15,
                       command=command)
        btn.pack(fill=tk.X)
        
        # Store the key and button reference in the frame
        btn_frame.nav_key = key
        btn_frame.nav_button = btn
        
        # Hover effects
        def on_enter(e):
            if self.current_page != key:
                btn.config(bg=self.colors['hover'])
        
        def on_leave(e):
            if self.current_page != key:
                btn.config(bg=self.colors['card'])
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn_frame
    
    def highlight_nav_button(self, key):
        """تمييز زر التنقل النشط"""
        for btn_key, btn_frame in self.nav_buttons.items():
            # Get the button from the stored reference
            btn = btn_frame.nav_button
            
            if btn_key == key:
                btn.config(bg=self.colors['primary_light'], fg='white', font=('Segoe UI', 13, 'bold'))
            else:
                btn.config(bg=self.colors['card'], fg=self.colors['text'], font=('Segoe UI', 15))
    
    def show_page(self, page_key):
        """عرض صفحة محددة وإخفاء الباقي"""
        # Hide all pages
        for key, page in self.pages.items():
            page.pack_forget()
        
        # Show selected page
        if page_key in self.pages:
            self.pages[page_key].pack(fill=tk.BOTH, expand=True)
            self.current_page = page_key
            self.highlight_nav_button(page_key)
    
    def create_all_pages(self):
        """إنشاء جميع الصفحات"""
        self.pages['students'] = self.create_students_page()
        self.pages['groups'] = self.create_groups_page()
        self.pages['teachers'] = self.create_teachers_page()
        self.pages['enrollment'] = self.create_enrollment_page()
        self.pages['payments'] = self.create_payments_page()
        self.pages['attendance'] = self.create_attendance_page()
        self.pages['notifications'] = self.create_notifications_page()
        self.pages['reports'] = self.create_reports_page()
    
    def show_students_page(self):
        self.show_page('students')
    
    def show_groups_page(self):
        self.show_page('groups')
    
    def show_teachers_page(self):
        self.show_page('teachers')
    
    def show_enrollment_page(self):
        self.show_page('enrollment')
    
    def show_payments_page(self):
        self.show_page('payments')
    
    def show_attendance_page(self):
        self.show_page('attendance')
    
    def show_notifications_page(self):
        self.show_page('notifications')
        self.load_notifications()
    
    def show_reports_page(self):
        self.show_page('reports')
    
    def setup_ui(self):
        """إنشاء الواجهة الرسومية"""
        
        # تطبيق ثيم حديث
        style = ttk.Style()
        style.theme_use('clam')
        
        # Increase global dropdown list font size
        self.root.option_add('*TCombobox*Listbox.font', ('Segoe UI', 16))
        
        # تكبير خط الجداول والعناصر + Modern Styling
        style.configure("Treeview", 
                       font=('Segoe UI', 13), 
                       rowheight=35,
                       background='#FFFFFF',
                       foreground='#111827',
                       fieldbackground='#FFFFFF',
                       borderwidth=0,
                       relief='flat')
        
        style.configure("Treeview.Heading", 
                       font=('Segoe UI', 14, 'bold'),
                       background='#6366F1',
                       foreground='white',
                       borderwidth=0,
                       relief='flat')
        
        style.map("Treeview.Heading",
                 background=[('active', '#4F46E5')])
        
        style.map("Treeview",
                 background=[('selected', '#818CF8')],
                 foreground=[('selected', 'white')])
        
        style.configure("TCombobox", font=('Segoe UI', 13))
        
        # ألوان احترافية حديثة - Modern Professional Palette
        self.colors = {
            'primary': '#6366F1',      # Indigo - modern & professional
            'primary_dark': '#4F46E5', # Darker indigo
            'primary_light': '#818CF8', # Light indigo
            'secondary': '#8B5CF6',    # Purple accent
            'success': '#10B981',      # Modern green
            'danger': '#EF4444',       # Modern red
            'warning': '#F59E0B',      # Modern amber
            'info': '#3B82F6',         # Modern blue
            'bg': '#F9FAFB',          # Very light gray background
            'bg_dark': '#F3F4F6',     # Light gray
            'card': '#FFFFFF',         # White cards
            'text': '#111827',         # Almost black
            'text_secondary': '#6B7280', # Gray text
            'text_light': '#9CA3AF',   # Light gray text
            'border': '#E5E7EB',       # Light border
            'hover': '#F3F4F6',        # Hover state
            'shadow': '#00000015'      # Subtle shadow
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # إعداد الستايلات الحديثة
        style.configure('TNotebook', 
                       background=self.colors['bg'],
                       borderwidth=0,
                       relief='flat')
        style.configure('TNotebook.Tab',
                       background=self.colors['card'],
                       foreground=self.colors['text'],
                       padding=[20, 12],
                       font=('Segoe UI', 12, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['primary'])],
                 foreground=[('selected', 'white')],
                 expand=[('selected', [1, 1, 1, 0])])
        
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('Card.TFrame', 
                       background=self.colors['card'],
                       relief='flat',
                       borderwidth=0)
        
        style.configure('TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 14))
        style.configure('Title.TLabel',
                       font=('Segoe UI', 24, 'bold'),
                       foreground=self.colors['primary'])
        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 13, 'bold'),
                       foreground=self.colors['text'])
        
        # تحسين مظهر الـ Treeview
        style.configure('Treeview',
                       background=self.colors['card'],
                       foreground=self.colors['text'],
                       fieldbackground=self.colors['card'],
                       borderwidth=0,
                       font=('Segoe UI', 14),
                       rowheight=35)
        style.configure('Treeview.Heading',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       font=('Segoe UI', 12, 'bold'),
                       relief='flat')
        style.map('Treeview.Heading',
                 background=[('active', self.colors['primary_dark'])])
        style.map('Treeview',
                 background=[('selected', self.colors['primary_light'])],
                 foreground=[('selected', 'white')])
        
        # تحسين Entry و Combobox
        style.configure('TEntry',
                       fieldbackground=self.colors['card'],
                       borderwidth=2,
                       relief='solid',
                       bordercolor=self.colors['border'],
                       font=('Segoe UI', 14))
        style.configure('TCombobox',
                       fieldbackground=self.colors['card'],
                       borderwidth=2,
                       relief='solid',
                       bordercolor=self.colors['border'],
                       font=('Segoe UI', 14))
        
        # ============================================
        # MODERN DESKTOP UI LAYOUT with SIDEBAR
        # ============================================
        
        # Main Container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # ============================================
        # SIDEBAR - Modern Navigation (Right side for RTL)
        # ============================================
        self.sidebar = tk.Frame(main_container, bg=self.colors['card'], width=280)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        # Sidebar Header
        sidebar_header = tk.Frame(self.sidebar, bg=self.colors['primary'], height=100)
        sidebar_header.pack(fill=tk.X)
        sidebar_header.pack_propagate(False)
        
        # App Logo and Title
        logo_frame = tk.Frame(sidebar_header, bg=self.colors['primary'])
        logo_frame.pack(expand=True)
        
        tk.Label(logo_frame, text=self.icons['students'],
                bg=self.colors['primary'],
                font=('Segoe UI', 48)).pack(pady=(5, 0))
        tk.Label(logo_frame, text="إدارة الطلبة",
                bg=self.colors['primary'], fg='white',
                font=('Segoe UI', 18, 'bold')).pack()
        
        # Sidebar Navigation Buttons
        nav_frame = tk.Frame(self.sidebar, bg=self.colors['card'])
        nav_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Navigation items
        self.nav_buttons = {}
        nav_items = [
            ('students', 'الطلبة', self.icons['students'], self.show_students_page),
            ('groups', 'المجموعات', self.icons['groups'], self.show_groups_page),
            ('teachers', 'المعلمين', self.icons['student'], self.show_teachers_page),
            ('enrollment', 'التسجيل', self.icons['enrollment'], self.show_enrollment_page),
            ('payments', 'الدفعات', self.icons['payments'], self.show_payments_page),
            ('attendance', 'الحضور', self.icons['attendance'], self.show_attendance_page),
            ('notifications', 'الإشعارات', self.icons['notification'], self.show_notifications_page),
            ('reports', 'التقارير', self.icons['reports'], self.show_reports_page),
        ]
        
        for key, text, icon, command in nav_items:
            self.nav_buttons[key] = self.create_nav_button(nav_frame, text, icon, command, key)
            self.nav_buttons[key].pack(fill=tk.X, padx=15, pady=3)
        
        # Sidebar Footer
        sidebar_footer = tk.Frame(self.sidebar, bg=self.colors['card'])
        sidebar_footer.pack(fill=tk.X, pady=20)
        
        # زر إنشاء اختصار على سطح المكتب
        shortcut_btn = tk.Button(sidebar_footer,
                                text="🖥️ اختصار سطح المكتب",
                                bg=self.colors['secondary'],
                                fg='white',
                                font=('Segoe UI', 11),
                                bd=0,
                                relief='flat',
                                cursor='hand2',
                                padx=15,
                                pady=8,
                                command=self.create_desktop_shortcut)
        shortcut_btn.pack(pady=(0, 10))
        
        # Hover effect for shortcut button
        def on_shortcut_enter(e):
            shortcut_btn.config(bg=self.colors['primary'])
        def on_shortcut_leave(e):
            shortcut_btn.config(bg=self.colors['secondary'])
        shortcut_btn.bind('<Enter>', on_shortcut_enter)
        shortcut_btn.bind('<Leave>', on_shortcut_leave)
        
        # Date display
        from datetime import datetime
        today = datetime.now().strftime("%Y/%m/%d")
        tk.Label(sidebar_footer, text=f"{self.icons['calendar']} {today}",
                bg=self.colors['card'], fg=self.colors['text_secondary'],
                font=('Segoe UI', 11)).pack(pady=5)
        
        # Version
        tk.Label(sidebar_footer, text="v2.3",
                bg=self.colors['card'], fg=self.colors['text_light'],
                font=('Segoe UI', 10)).pack()
        
        # ============================================
        # CONTENT AREA - Main workspace
        # ============================================
        self.content_area = tk.Frame(main_container, bg=self.colors['bg'])
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create all pages (hidden initially)
        self.pages = {}
        self.create_all_pages()
        
        # Show default page
        self.show_students_page()
        
        # فحص الإشعارات عند التشغيل
        self.root.after(1000, self.check_notifications_on_startup)
    
    def create_students_page(self):
        """صفحة إدارة الطلبة - Modern Desktop UI"""
        page = tk.Frame(self.content_area, bg=self.colors['bg'])
        
        # Page Header
        header = tk.Frame(page, bg=self.colors['bg'], height=80)
        header.pack(fill=tk.X, padx=30, pady=(20, 0))
        header.pack_propagate(False)
        
        # Title with icon - RTL
        title_frame = tk.Frame(header, bg=self.colors['bg'])
        title_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(title_frame, text=f"{self.icons['students']} إدارة الطلبة",
                bg=self.colors['bg'],
                fg=self.colors['text'],
                font=('Segoe UI', 28, 'bold')).pack(anchor=tk.E)
        tk.Label(title_frame, text="إضافة وإدارة بيانات الطلاب",
                bg=self.colors['bg'],
                fg=self.colors['text_secondary'],
                font=('Segoe UI', 15)).pack(anchor=tk.E, pady=(2, 0))
        
        # زر التحديث
        refresh_btn = tk.Button(header, text=f"{self.icons['refresh']} تحديث",
                               bg=self.colors['info'], fg='white',
                               font=('Segoe UI', 12, 'bold'),
                               bd=0, padx=20, pady=8, cursor='hand2',
                               activebackground=self.colors['primary'],
                               command=self.load_students)
        refresh_btn.pack(side=tk.LEFT, pady=15)
        
        # Container رئيسي
        main_container = tk.Frame(page, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # ===================
        # قسم البحث والإحصائيات
        # ===================
        top_section = tk.Frame(main_container, bg=self.colors['bg'])
        top_section.pack(fill=tk.X, pady=(0, 20))
        
        # بطاقة الإحصائيات - Modern gradient card
        stats_outer = tk.Frame(top_section, bg=self.colors['border'], bd=0)
        stats_outer.pack(side=tk.RIGHT, padx=(15, 0))
        
        stats_card = tk.Frame(stats_outer, bg=self.colors['primary'], bd=0)
        stats_card.pack(padx=1, pady=1)
        
        stats_inner = tk.Frame(stats_card, bg=self.colors['primary'])
        stats_inner.pack(padx=30, pady=20)
        
        tk.Label(stats_inner, text=f"{self.icons['stats']} إجمالي الطلبة", 
                bg=self.colors['primary'], fg=self.colors['primary_light'],
                font=('Segoe UI', 11, 'bold')).pack()
        self.students_count_label = tk.Label(stats_inner, text="0", 
                                             bg=self.colors['primary'], fg='white',
                                             font=('Segoe UI', 42, 'bold'))
        self.students_count_label.pack(pady=(8, 0))
        tk.Label(stats_inner, text="طالب مسجل", 
                bg=self.colors['primary'], fg=self.colors['primary_light'],
                font=('Segoe UI', 11)).pack(pady=(2, 0))
        
        # بطاقة البحث - Modern search bar
        search_outer = tk.Frame(top_section, bg=self.colors['border'], bd=0)
        search_outer.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        search_card = tk.Frame(search_outer, bg=self.colors['card'], bd=0)
        search_card.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=1, pady=1)
        
        search_inner = tk.Frame(search_card, bg=self.colors['card'])
        search_inner.pack(padx=25, pady=20, fill=tk.X)
        
        # Search icon - RTL (right side)
        tk.Label(search_inner, text=self.icons['search'], 
                bg=self.colors['card'], 
                fg=self.colors['primary'],
                font=('Segoe UI', 22)).pack(side=tk.RIGHT, padx=(10, 0))
        
        self.student_search_var = tk.StringVar()
        
        # Modern search entry with border
        entry_outer = tk.Frame(search_inner, bg=self.colors['border'])
        entry_outer.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        search_entry = tk.Entry(entry_outer, 
                               textvariable=self.student_search_var, 
                               font=('Segoe UI', 15),
                               bd=0,
                               relief='flat',
                               bg=self.colors['card'],
                               fg=self.colors['text'],
                               insertbackground=self.colors['primary'],
                               justify='right')  # RTL
        search_entry.pack(fill=tk.X, padx=1, pady=1, ipady=8, ipadx=15)
        search_entry.insert(0, "ابحث عن طالب بالاسم، الهاتف، أو البريد...")
        
        def on_search_focus_in(e):
            if search_entry.get() == "ابحث عن طالب بالاسم، الهاتف، أو البريد...":
                search_entry.delete(0, tk.END)
                search_entry.config(fg=self.colors['text'])
            entry_outer.config(bg=self.colors['primary'])
        
        def on_search_focus_out(e):
            if search_entry.get() == "":
                search_entry.insert(0, "ابحث عن طالب بالاسم، الهاتف، أو البريد...")
                search_entry.config(fg=self.colors['text_light'])
            entry_outer.config(bg=self.colors['border'])
        
        search_entry.bind('<FocusIn>', on_search_focus_in)
        search_entry.bind('<FocusOut>', on_search_focus_out)
        search_entry.config(fg=self.colors['text_light'])
        
        # Clear button - RTL (left side)
        clear_btn = tk.Button(search_inner, text=self.icons['close'], 
                             bg=self.colors['card'], 
                             fg=self.colors['text_light'],
                             border=0, font=('Segoe UI', 20), cursor='hand2',
                             activebackground=self.colors['card'],
                             activeforeground=self.colors['danger'],
                             command=lambda: self.student_search_var.set(""))
        clear_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # ===================
        # قسم نموذج الإدخال - Modern Card
        # ===================
        form_outer = tk.Frame(main_container, bg=self.colors['border'], bd=0)
        form_outer.pack(fill=tk.X, pady=(0, 15))
        
        form_card = tk.Frame(form_outer, bg=self.colors['card'], bd=0)
        form_card.pack(fill=tk.X, padx=1, pady=1)
        
        form_inner = ttk.Frame(form_card)
        form_inner.pack(padx=25, pady=25, fill=tk.X)
        
        # عنوان النموذج مع أيقونة - RTL
        form_title_frame = tk.Frame(form_inner, bg=self.colors['card'])
        form_title_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(form_title_frame, text=f"{self.icons['enrollment']} معلومات الطالب", 
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 19, 'bold')).pack(side=tk.RIGHT)
        
        # Separator line
        tk.Frame(form_inner, bg=self.colors['border'], height=2).pack(fill=tk.X, pady=(10, 20))
        
        # حقول الإدخال الحديثة مع الأيقونات - RTL
        fields_frame = tk.Frame(form_inner, bg=self.colors['card'])
        fields_frame.pack(fill=tk.X)
        
        # الصف الأول - RTL
        row1 = tk.Frame(fields_frame, bg=self.colors['card'])
        row1.pack(fill=tk.X, pady=8)
        
        # رقم الهاتف (يسار)
        phone_container, self.student_phone = self.create_modern_input(
            row1, "رقم الهاتف", self.icons['phone'], 25)
        phone_container.pack(side=tk.LEFT, padx=(15, 0))
        
        # الاسم الكامل (يمين)
        name_container, self.student_name = self.create_modern_input(
            row1, "الاسم الكامل", self.icons['student'], 35)
        name_container.pack(side=tk.RIGHT)
        
        # الصف الثاني - RTL
        row2 = tk.Frame(fields_frame, bg=self.colors['card'])
        row2.pack(fill=tk.X, pady=8)
        
        # العنوان (يسار)
        address_container, self.student_address = self.create_modern_input(
            row2, "العنوان", self.icons['home'], 25)
        address_container.pack(side=tk.LEFT, padx=(15, 0))
        
        # البريد الإلكتروني (يمين)
        email_container, self.student_email = self.create_modern_input(
            row2, "البريد الإلكتروني", self.icons['email'], 35)
        email_container.pack(side=tk.RIGHT)
        
        # أزرار العمليات - Modern Design RTL
        btn_frame = tk.Frame(form_inner, bg=self.colors['card'])
        btn_frame.pack(pady=(25, 0))
        
        # أزرار حديثة مع تأثيرات hover - ترتيب RTL
        self.create_modern_button(btn_frame, "مسح الحقول", self.clear_student_fields, 
                                  'secondary', self.icons['clear']).pack(side=tk.LEFT, padx=5)
        self.create_modern_button(btn_frame, "حذف", self.delete_student, 
                                  'danger', self.icons['delete']).pack(side=tk.LEFT, padx=5)
        self.create_modern_button(btn_frame, "تحديث", self.update_student, 
                                  'warning', self.icons['edit']).pack(side=tk.LEFT, padx=5)
        self.create_modern_button(btn_frame, "إضافة طالب", self.add_student, 
                                  'success', self.icons['add']).pack(side=tk.LEFT, padx=5)
        
        # ===================
        # قسم عرض الطلبة - Modern Table
        # ===================
        display_outer = tk.Frame(main_container, bg=self.colors['border'], bd=0)
        display_outer.pack(fill=tk.BOTH, expand=True)
        
        display_card = tk.Frame(display_outer, bg=self.colors['card'], bd=0)
        display_card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        display_inner = ttk.Frame(display_card)
        display_inner.pack(padx=25, pady=25, fill=tk.BOTH, expand=True)
        
        # عنوان القائمة مع أيقونة - RTL
        tk.Label(display_inner, text=f"{self.icons['students']} قائمة الطلبة المسجلين", 
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 19, 'bold')).pack(anchor=tk.E, pady=(0, 5))
        
        # Separator
        tk.Frame(display_inner, bg=self.colors['border'], height=2).pack(fill=tk.X, pady=(5, 15))
        
        # إطار الجدول مع حدود حديثة
        tree_outer = tk.Frame(display_inner, bg='#D1D5DB', bd=0)
        tree_outer.pack(fill=tk.BOTH, expand=True)
        
        tree_frame = tk.Frame(tree_outer, bg='#FFFFFF')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # جدول الطلبة مع تنسيق حديث - RTL (من اليمين لليسار)
        columns = ("المجموعات", "تاريخ التسجيل", "العنوان", "البريد", "الهاتف", "الاسم", "ID")
        self.students_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", 
                                         height=15, selectmode='browse')
        
        # تنسيق الأعمدة - RTL
        self.students_tree.column("المجموعات", width=80, anchor='center')
        self.students_tree.column("تاريخ التسجيل", width=120, anchor='center')
        self.students_tree.column("العنوان", width=150, anchor='e')
        self.students_tree.column("البريد", width=200, anchor='e')
        self.students_tree.column("الهاتف", width=120, anchor='center')
        self.students_tree.column("الاسم", width=200, anchor='e')
        self.students_tree.column("ID", width=50, anchor='center')
        
        for col in columns:
            self.students_tree.heading(col, text=col)
        
        # تلوين الصفوف بالتبادل
        self.students_tree.tag_configure('oddrow', background='#F3F4F6', foreground='#111827')
        self.students_tree.tag_configure('evenrow', background='#FFFFFF', foreground='#111827')
        self.students_tree.tag_configure('selected', background=self.colors['primary'], foreground='white')
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.students_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.students_tree.xview)
        self.students_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.students_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # حدث النقر
        self.students_tree.bind("<ButtonRelease-1>", self.on_student_tree_click)
        self.students_tree.bind("<Double-1>", self.view_student_details)
        
        # تفعيل البحث المباشر بعد إنشاء الـ tree
        self.student_search_var.trace('w', lambda *args: self.search_students())
        
        # تحميل البيانات
        self.load_students()
    
        return page
    
    def create_groups_page(self):
        """صفحة إدارة المجموعات - Modern Desktop UI"""
        page = tk.Frame(self.content_area, bg=self.colors['bg'])
        
        # Page Header
        header = tk.Frame(page, bg=self.colors['bg'], height=80)
        header.pack(fill=tk.X, padx=30, pady=(20, 0))
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg=self.colors['bg'])
        title_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(title_frame, text=f"{self.icons['groups']} إدارة المجموعات",
                bg=self.colors['bg'],
                fg=self.colors['text'],
                font=('Segoe UI', 28, 'bold')).pack(anchor=tk.E)
        tk.Label(title_frame, text="إنشاء وإدارة المجموعات الدراسية",
                bg=self.colors['bg'],
                fg=self.colors['text_secondary'],
                font=('Segoe UI', 15)).pack(anchor=tk.E, pady=(2, 0))
        
        # زر التحديث
        refresh_btn = tk.Button(header, text=f"{self.icons['refresh']} تحديث",
                               bg=self.colors['info'], fg='white',
                               font=('Segoe UI', 12, 'bold'),
                               bd=0, padx=20, pady=8, cursor='hand2',
                               activebackground=self.colors['primary'],
                               command=self.load_groups)
        refresh_btn.pack(side=tk.LEFT, pady=15)
        
        # Content from old tab
        content = tk.Frame(page, bg=self.colors['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        self.create_groups_tab_for_page(content)
        
        return page
    
    def create_teachers_page(self):
        """صفحة إدارة المعلمين - Modern Desktop UI"""
        page = tk.Frame(self.content_area, bg=self.colors['bg'])
        
        # Page Header
        header = tk.Frame(page, bg=self.colors['bg'], height=80)
        header.pack(fill=tk.X, padx=30, pady=(20, 0))
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg=self.colors['bg'])
        title_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(title_frame, text=f"{self.icons['student']} إدارة المعلمين",
                bg=self.colors['bg'],
                fg=self.colors['text'],
                font=('Segoe UI', 28, 'bold')).pack(anchor=tk.E)
        tk.Label(title_frame, text="إضافة وإدارة بيانات المعلمين",
                bg=self.colors['bg'],
                fg=self.colors['text_secondary'],
                font=('Segoe UI', 15)).pack(anchor=tk.E, pady=(2, 0))
        
        # زر التحديث
        refresh_btn = tk.Button(header, text=f"{self.icons['refresh']} تحديث",
                               bg=self.colors['info'], fg='white',
                               font=('Segoe UI', 12, 'bold'),
                               bd=0, padx=20, pady=8, cursor='hand2',
                               activebackground=self.colors['primary'],
                               command=self.load_teachers)
        refresh_btn.pack(side=tk.LEFT, pady=15)
        
        # Main container
        main_container = tk.Frame(page, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Form section
        form_outer = tk.Frame(main_container, bg=self.colors['border'], bd=0)
        form_outer.pack(fill=tk.X, pady=(0, 15))
        
        form_card = tk.Frame(form_outer, bg=self.colors['card'], bd=0)
        form_card.pack(fill=tk.X, padx=1, pady=1)
        
        form_inner = ttk.Frame(form_card)
        form_inner.pack(padx=25, pady=25, fill=tk.X)
        
        # Form title
        form_title_frame = tk.Frame(form_inner, bg=self.colors['card'])
        form_title_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(form_title_frame, text=f"{self.icons['student']} معلومات المعلم", 
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 19, 'bold')).pack(side=tk.RIGHT)
        
        tk.Frame(form_inner, bg=self.colors['border'], height=2).pack(fill=tk.X, pady=(10, 20))
        
        # Input fields
        fields_frame = tk.Frame(form_inner, bg=self.colors['card'])
        fields_frame.pack(fill=tk.X)
        
        # Row 1
        row1 = tk.Frame(fields_frame, bg=self.colors['card'])
        row1.pack(fill=tk.X, pady=8)
        
        phone_container, self.teacher_phone = self.create_modern_input(
            row1, "رقم الهاتف", self.icons['phone'], 25)
        phone_container.pack(side=tk.LEFT, padx=(15, 0))
        
        name_container, self.teacher_name = self.create_modern_input(
            row1, "اسم المعلم", self.icons['student'], 35)
        name_container.pack(side=tk.RIGHT)
        
        # Row 2
        row2 = tk.Frame(fields_frame, bg=self.colors['card'])
        row2.pack(fill=tk.X, pady=8)
        
        spec_container, self.teacher_specialization = self.create_modern_input(
            row2, "التخصص", self.icons['group'], 25)
        spec_container.pack(side=tk.LEFT, padx=(15, 0))
        
        email_container, self.teacher_email = self.create_modern_input(
            row2, "البريد الإلكتروني", self.icons['email'], 35)
        email_container.pack(side=tk.RIGHT)
        
        # Action buttons
        btn_frame = tk.Frame(form_inner, bg=self.colors['card'])
        btn_frame.pack(pady=(25, 0))
        
        self.create_modern_button(btn_frame, "مسح الحقول", self.clear_teacher_fields, 
                                  'secondary', self.icons['clear']).pack(side=tk.LEFT, padx=5)
        self.create_modern_button(btn_frame, "حذف", self.delete_teacher, 
                                  'danger', self.icons['delete']).pack(side=tk.LEFT, padx=5)
        self.create_modern_button(btn_frame, "تحديث", self.update_teacher, 
                                  'warning', self.icons['edit']).pack(side=tk.LEFT, padx=5)
        self.create_modern_button(btn_frame, "إضافة معلم", self.add_teacher, 
                                  'success', self.icons['add']).pack(side=tk.LEFT, padx=5)
        
        # Display section
        display_outer = tk.Frame(main_container, bg=self.colors['border'], bd=0)
        display_outer.pack(fill=tk.BOTH, expand=True)
        
        display_card = tk.Frame(display_outer, bg=self.colors['card'], bd=0)
        display_card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        display_inner = ttk.Frame(display_card)
        display_inner.pack(padx=25, pady=25, fill=tk.BOTH, expand=True)
        
        tk.Label(display_inner, text=f"{self.icons['student']} قائمة المعلمين", 
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 19, 'bold')).pack(anchor=tk.E, pady=(0, 5))
        
        tk.Frame(display_inner, bg=self.colors['border'], height=2).pack(fill=tk.X, pady=(5, 15))
        
        # Table
        tree_outer = tk.Frame(display_inner, bg='#D1D5DB', bd=0)
        tree_outer.pack(fill=tk.BOTH, expand=True)
        
        tree_frame = tk.Frame(tree_outer, bg='#FFFFFF')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        columns = ("المجموعات", "عدد الطلاب", "التخصص", "البريد", "الهاتف", "الاسم", "ID")
        self.teachers_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", 
                                         height=15, selectmode='browse')
        
        # Column formatting
        self.teachers_tree.column("المجموعات", width=80, anchor='center')
        self.teachers_tree.column("عدد الطلاب", width=100, anchor='center')
        self.teachers_tree.column("التخصص", width=150, anchor='e')
        self.teachers_tree.column("البريد", width=200, anchor='e')
        self.teachers_tree.column("الهاتف", width=120, anchor='center')
        self.teachers_tree.column("الاسم", width=200, anchor='e')
        self.teachers_tree.column("ID", width=50, anchor='center')
        
        for col in columns:
            self.teachers_tree.heading(col, text=col)
        
        # Row coloring
        self.teachers_tree.tag_configure('oddrow', background='#F3F4F6', foreground='#111827')
        self.teachers_tree.tag_configure('evenrow', background='#FFFFFF', foreground='#111827')
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.teachers_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.teachers_tree.xview)
        self.teachers_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.teachers_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Click events
        self.teachers_tree.bind("<ButtonRelease-1>", self.on_teacher_tree_click)
        
        # Load data
        self.load_teachers()
        
        # ===================
        # قسم عرض مجموعات المعلم المحدد
        # ===================
        teacher_groups_outer = tk.Frame(main_container, bg=self.colors['border'], bd=0)
        teacher_groups_outer.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        teacher_groups_card = tk.Frame(teacher_groups_outer, bg=self.colors['card'], bd=0)
        teacher_groups_card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        teacher_groups_inner = ttk.Frame(teacher_groups_card)
        teacher_groups_inner.pack(padx=25, pady=25, fill=tk.BOTH, expand=True)
        
        self.selected_teacher_label = tk.Label(teacher_groups_inner, 
                                               text=f"{self.icons['groups']} مجموعات المعلم", 
                                               bg=self.colors['card'],
                                               fg=self.colors['text'],
                                               font=('Segoe UI', 19, 'bold'))
        self.selected_teacher_label.pack(anchor=tk.E, pady=(0, 5))
        
        tk.Frame(teacher_groups_inner, bg=self.colors['border'], height=2).pack(fill=tk.X, pady=(5, 15))
        
        # Table for teacher's groups
        tg_tree_outer = tk.Frame(teacher_groups_inner, bg='#D1D5DB', bd=0)
        tg_tree_outer.pack(fill=tk.BOTH, expand=True)
        
        tg_tree_frame = tk.Frame(tg_tree_outer, bg='#FFFFFF')
        tg_tree_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        tg_columns = ("عدد الطلاب", "الرسوم", "الجدول", "المادة", "المجموعة", "ID")
        self.teacher_groups_tree = ttk.Treeview(tg_tree_frame, columns=tg_columns, show="headings", height=8)
        
        # Column formatting
        self.teacher_groups_tree.column("ID", width=60, anchor='center')
        self.teacher_groups_tree.column("المجموعة", width=200, anchor='e')
        self.teacher_groups_tree.column("المادة", width=150, anchor='e')
        self.teacher_groups_tree.column("الجدول", width=200, anchor='e')
        self.teacher_groups_tree.column("الرسوم", width=100, anchor='center')
        self.teacher_groups_tree.column("عدد الطلاب", width=100, anchor='center')
        
        for col in tg_columns:
            self.teacher_groups_tree.heading(col, text=col)
        
        # Row coloring
        self.teacher_groups_tree.tag_configure('oddrow', background='#F3F4F6', foreground='#111827')
        self.teacher_groups_tree.tag_configure('evenrow', background='#FFFFFF', foreground='#111827')
        
        # Scrollbars
        tg_vsb = ttk.Scrollbar(tg_tree_frame, orient="vertical", command=self.teacher_groups_tree.yview)
        tg_hsb = ttk.Scrollbar(tg_tree_frame, orient="horizontal", command=self.teacher_groups_tree.xview)
        self.teacher_groups_tree.configure(yscrollcommand=tg_vsb.set, xscrollcommand=tg_hsb.set)
        
        self.teacher_groups_tree.grid(row=0, column=0, sticky='nsew')
        tg_vsb.grid(row=0, column=1, sticky='ns')
        tg_hsb.grid(row=1, column=0, sticky='ew')
        
        tg_tree_frame.grid_rowconfigure(0, weight=1)
        tg_tree_frame.grid_columnconfigure(0, weight=1)
    
        return page
    
    def create_enrollment_page(self):
        """صفحة التسجيل"""
        page = tk.Frame(self.content_area, bg=self.colors['bg'])
        
        # Page Header
        header = tk.Frame(page, bg=self.colors['bg'], height=80)
        header.pack(fill=tk.X, padx=30, pady=(20, 0))
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg=self.colors['bg'])
        title_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(title_frame, text=f"{self.icons['enrollment']} التسجيل في المجموعات",
                bg=self.colors['bg'],
                fg=self.colors['text'],
                font=('Segoe UI', 28, 'bold')).pack(anchor=tk.E)
        tk.Label(title_frame, text="تسجيل الطلاب في المجموعات الدراسية",
                bg=self.colors['bg'],
                fg=self.colors['text_secondary'],
                font=('Segoe UI', 15)).pack(anchor=tk.E, pady=(2, 0))
        
        # زر التحديث
        refresh_btn = tk.Button(header, text=f"{self.icons['refresh']} تحديث",
                               bg=self.colors['info'], fg='white',
                               font=('Segoe UI', 12, 'bold'),
                               bd=0, padx=20, pady=8, cursor='hand2',
                               activebackground=self.colors['primary'],
                               command=self.load_enrollments)
        refresh_btn.pack(side=tk.LEFT, pady=15)
        
        # Content from old tab - will be converted
        content = tk.Frame(page, bg=self.colors['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Will copy content from create_enrollment_tab
        self.create_enrollment_tab_for_page(content)
        
        return page
    
    def create_payments_page(self):
        """صفحة الدفعات"""
        page = tk.Frame(self.content_area, bg=self.colors['bg'])
        
        header = tk.Frame(page, bg=self.colors['bg'], height=80)
        header.pack(fill=tk.X, padx=30, pady=(20, 0))
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg=self.colors['bg'])
        title_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(title_frame, text=f"{self.icons['payments']} إدارة الدفعات",
                bg=self.colors['bg'],
                fg=self.colors['text'],
                font=('Segoe UI', 28, 'bold')).pack(anchor=tk.E)
        tk.Label(title_frame, text="تسجيل ومتابعة المدفوعات والرسوم",
                bg=self.colors['bg'],
                fg=self.colors['text_secondary'],
                font=('Segoe UI', 15)).pack(anchor=tk.E, pady=(2, 0))
        
        # زر التحديث
        refresh_btn = tk.Button(header, text=f"{self.icons['refresh']} تحديث",
                               bg=self.colors['info'], fg='white',
                               font=('Segoe UI', 12, 'bold'),
                               bd=0, padx=20, pady=8, cursor='hand2',
                               activebackground=self.colors['primary'],
                               command=self.load_payments)
        refresh_btn.pack(side=tk.LEFT, pady=15)
        
        content = tk.Frame(page, bg=self.colors['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        self.create_payments_tab_for_page(content)
        
        return page
    
    def create_attendance_page(self):
        """صفحة الحضور"""
        page = tk.Frame(self.content_area, bg=self.colors['bg'])
        
        header = tk.Frame(page, bg=self.colors['bg'], height=80)
        header.pack(fill=tk.X, padx=30, pady=(20, 0))
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg=self.colors['bg'])
        title_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(title_frame, text=f"{self.icons['attendance']} الحضور والغياب",
                bg=self.colors['bg'],
                fg=self.colors['text'],
                font=('Segoe UI', 28, 'bold')).pack(anchor=tk.E)
        tk.Label(title_frame, text="تسجيل ومتابعة حضور الطلاب",
                bg=self.colors['bg'],
                fg=self.colors['text_secondary'],
                font=('Segoe UI', 15)).pack(anchor=tk.E, pady=(2, 0))
        
        # زر التحديث
        refresh_btn = tk.Button(header, text=f"{self.icons['refresh']} تحديث",
                               bg=self.colors['info'], fg='white',
                               font=('Segoe UI', 12, 'bold'),
                               bd=0, padx=20, pady=8, cursor='hand2',
                               activebackground=self.colors['primary'],
                               command=self.load_attendance)
        refresh_btn.pack(side=tk.LEFT, pady=15)
        
        content = tk.Frame(page, bg=self.colors['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        self.create_attendance_tab_for_page(content)
        
        return page
    
    def create_notifications_page(self):
        """صفحة الإشعارات"""
        page = tk.Frame(self.content_area, bg=self.colors['bg'])
        
        header = tk.Frame(page, bg=self.colors['bg'], height=80)
        header.pack(fill=tk.X, padx=30, pady=(20, 0))
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg=self.colors['bg'])
        title_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(title_frame, text=f"{self.icons['notification']} الإشعارات",
                bg=self.colors['bg'],
                fg=self.colors['text'],
                font=('Segoe UI', 28, 'bold')).pack(anchor=tk.E)
        tk.Label(title_frame, text="عرض وإدارة جميع الإشعارات",
                bg=self.colors['bg'],
                fg=self.colors['text_secondary'],
                font=('Segoe UI', 15)).pack(anchor=tk.E, pady=(2, 0))
        
        # زر التحديث
        refresh_btn = tk.Button(header, text=f"{self.icons['refresh']} تحديث",
                               bg=self.colors['info'], fg='white',
                               font=('Segoe UI', 12, 'bold'),
                               bd=0, padx=20, pady=8, cursor='hand2',
                               activebackground=self.colors['primary'],
                               command=self.refresh_notifications)
        refresh_btn.pack(side=tk.LEFT, pady=15)
        
        content = tk.Frame(page, bg=self.colors['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        self.create_notifications_tab_for_page(content)
        
        return page
    
    def create_reports_page(self):
        """صفحة التقارير"""
        page = tk.Frame(self.content_area, bg=self.colors['bg'])
        
        header = tk.Frame(page, bg=self.colors['bg'], height=80)
        header.pack(fill=tk.X, padx=30, pady=(20, 0))
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg=self.colors['bg'])
        title_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(title_frame, text=f"{self.icons['reports']} التقارير والإحصائيات",
                bg=self.colors['bg'],
                fg=self.colors['text'],
                font=('Segoe UI', 28, 'bold')).pack(anchor=tk.E)
        tk.Label(title_frame, text="تقارير شاملة عن الطلاب والمجموعات",
                bg=self.colors['bg'],
                fg=self.colors['text_secondary'],
                font=('Segoe UI', 15)).pack(anchor=tk.E, pady=(2, 0))
        
        content = tk.Frame(page, bg=self.colors['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        self.create_reports_tab_for_page(content)
        
        return page
    
    def create_placeholder_page(self, title, subtitle, icon):
        """إنشاء صفحة مؤقتة"""
        page = tk.Frame(self.content_area, bg=self.colors['bg'])
        
        # Page Header
        header = tk.Frame(page, bg=self.colors['bg'], height=80)
        header.pack(fill=tk.X, padx=30, pady=(20, 0))
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg=self.colors['bg'])
        title_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(title_frame, text=f"{icon} {title}",
                bg=self.colors['bg'],
                fg=self.colors['text'],
                font=('Segoe UI', 28, 'bold')).pack(anchor=tk.E)
        tk.Label(title_frame, text=subtitle,
                bg=self.colors['bg'],
                fg=self.colors['text_secondary'],
                font=('Segoe UI', 15)).pack(anchor=tk.E, pady=(2, 0))
        
        # Content
        content = tk.Frame(page, bg=self.colors['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Placeholder card
        card_outer = tk.Frame(content, bg=self.colors['border'])
        card_outer.pack(expand=True)
        
        card = tk.Frame(card_outer, bg=self.colors['card'])
        card.pack(padx=1, pady=1, ipadx=100, ipady=80)
        
        tk.Label(card, text=f"{icon}",
                bg=self.colors['card'],
                font=('Segoe UI', 64)).pack(pady=(20, 10))
        tk.Label(card, text=f"🚧 قيد التطوير",
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 18, 'bold')).pack()
        tk.Label(card, text=f"صفحة {title} ستكون متاحة قريباً",
                bg=self.colors['card'],
                fg=self.colors['text_secondary'],
                font=('Segoe UI', 15)).pack(pady=(5, 20))
        
        return page
    
    def create_groups_tab_for_page(self, parent):
        """محتوى صفحة المجموعات - Modern UI"""
        # Main container
        main_container = tk.Frame(parent, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # ===================
        # قسم نموذج الإدخال - Modern Card
        # ===================
        form_outer = tk.Frame(main_container, bg=self.colors['border'], bd=0)
        form_outer.pack(fill=tk.X, pady=(0, 20))
        
        form_card = tk.Frame(form_outer, bg=self.colors['card'], bd=0)
        form_card.pack(fill=tk.X, padx=1, pady=1)
        
        form_inner = tk.Frame(form_card, bg=self.colors['card'])
        form_inner.pack(padx=25, pady=25, fill=tk.X)
        
        # عنوان النموذج
        tk.Label(form_inner, text=f"{self.icons['groups']} معلومات المجموعة", 
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 19, 'bold')).pack(anchor=tk.E, pady=(0, 5))
        
        # Separator
        tk.Frame(form_inner, bg=self.colors['border'], height=2).pack(fill=tk.X, pady=(5, 20))
        
        # حقول الإدخال الحديثة - RTL
        fields_frame = tk.Frame(form_inner, bg=self.colors['card'])
        fields_frame.pack(fill=tk.X)
        
        # الصف الأول - RTL
        row1 = tk.Frame(fields_frame, bg=self.colors['card'])
        row1.pack(fill=tk.X, pady=8)
        
        # المادة (يسار)
        subject_container, self.group_subject = self.create_modern_input(
            row1, "المادة", self.icons['group'], 25)
        subject_container.pack(side=tk.LEFT, padx=(15, 0))
        
        # اسم المجموعة (يمين)
        name_container, self.group_name = self.create_modern_input(
            row1, "اسم المجموعة", self.icons['groups'], 35)
        name_container.pack(side=tk.RIGHT)
        
        # الصف الثاني - RTL
        row2 = tk.Frame(fields_frame, bg=self.colors['card'])
        row2.pack(fill=tk.X, pady=8)
        
        # الجدول (يسار)
        schedule_container, self.group_schedule = self.create_modern_input(
            row2, "الجدول الزمني", self.icons['calendar'], 25)
        schedule_container.pack(side=tk.LEFT, padx=(15, 0))
        
        # المعلم (يمين) - Dropdown to select from existing teachers
        teacher_label = tk.Frame(row2, bg=self.colors['card'])
        teacher_label.pack(side=tk.RIGHT)
        tk.Label(teacher_label, text=f"{self.icons['student']} اسم المعلم:",
                bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 12, 'bold')).pack()
        
        teacher_combo_frame = tk.Frame(row2, bg=self.colors['border'])
        teacher_combo_frame.pack(side=tk.RIGHT, padx=(0, 10))
        self.group_teacher = ttk.Combobox(teacher_combo_frame, width=33, font=('Segoe UI', 14))
        self.enable_search(self.group_teacher)
        self.group_teacher.pack(padx=1, pady=1, ipady=6)
        
        # الصف الثالث - الرسوم
        row3 = tk.Frame(fields_frame, bg=self.colors['card'])
        row3.pack(fill=tk.X, pady=8)
        
        # الرسوم (يمين)
        fee_container, self.group_fee = self.create_modern_input(
            row3, "الرسوم الشهرية", self.icons['payment'], 20)
        fee_container.pack(side=tk.RIGHT)
        
        # أزرار العمليات - Modern Design RTL
        btn_frame = tk.Frame(form_inner, bg=self.colors['card'])
        btn_frame.pack(pady=(25, 0))
        
        self.create_modern_button(btn_frame, "مسح الحقول", self.clear_group_fields, 
                                  'secondary', self.icons['clear']).pack(side=tk.LEFT, padx=5)
        self.create_modern_button(btn_frame, "حذف", self.delete_group, 
                                  'danger', self.icons['delete']).pack(side=tk.LEFT, padx=5)
        self.create_modern_button(btn_frame, "تحديث", self.update_group, 
                                  'warning', self.icons['edit']).pack(side=tk.LEFT, padx=5)
        self.create_modern_button(btn_frame, "إضافة مجموعة", self.add_group, 
                                  'success', self.icons['add']).pack(side=tk.LEFT, padx=5)
        
        # Load teachers into dropdown
        self.refresh_group_teacher_combo()
        
        # ===================
        # قسم عرض المجموعات - Modern Table
        # ===================
        display_outer = tk.Frame(main_container, bg=self.colors['border'], bd=0)
        display_outer.pack(fill=tk.BOTH, expand=True)
        
        display_card = tk.Frame(display_outer, bg=self.colors['card'], bd=0)
        display_card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        display_inner = tk.Frame(display_card, bg=self.colors['card'])
        display_inner.pack(padx=25, pady=25, fill=tk.BOTH, expand=True)
        
        # عنوان القائمة
        tk.Label(display_inner, text=f"{self.icons['groups']} قائمة المجموعات", 
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 19, 'bold')).pack(anchor=tk.E, pady=(0, 5))
        
        # Separator
        tk.Frame(display_inner, bg=self.colors['border'], height=2).pack(fill=tk.X, pady=(5, 15))
        
        # إطار الجدول مع حدود حديثة
        tree_outer = tk.Frame(display_inner, bg='#D1D5DB', bd=0)
        tree_outer.pack(fill=tk.BOTH, expand=True)
        
        tree_frame = tk.Frame(tree_outer, bg='#FFFFFF')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        
        # جدول المجموعات - RTL Modern
        columns = ("عرض", "الرسوم", "الجدول", "المعلم", "المادة", "الاسم", "ID")
        self.groups_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        
        # تنسيق الأعمدة - RTL
        self.groups_tree.column("عرض", width=60, anchor='center')
        self.groups_tree.column("ID", width=60, anchor='center')
        self.groups_tree.column("الاسم", width=200, anchor='e')
        self.groups_tree.column("المادة", width=150, anchor='e')
        self.groups_tree.column("المعلم", width=180, anchor='e')
        self.groups_tree.column("الجدول", width=180, anchor='e')
        self.groups_tree.column("الرسوم", width=100, anchor='center')
        
        for col in columns:
            self.groups_tree.heading(col, text=col)
        
        # تلوين الصفوف بالتبادل
        self.groups_tree.tag_configure('oddrow', background='#F3F4F6', foreground='#111827')
        self.groups_tree.tag_configure('evenrow', background='#FFFFFF', foreground='#111827')
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.groups_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.groups_tree.xview)
        self.groups_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.groups_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # حدث النقر
        self.groups_tree.bind("<ButtonRelease-1>", self.on_group_tree_click)
        
        # تحميل البيانات
        self.load_groups()
    
    def create_enrollment_tab_for_page(self, parent):
        """محتوى صفحة التسجيل - Modern UI"""
        main_container = tk.Frame(parent, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # نموذج التسجيل - Modern Card
        form_outer = tk.Frame(main_container, bg=self.colors['border'], bd=0)
        form_outer.pack(fill=tk.X, pady=(0, 20))
        
        form_card = tk.Frame(form_outer, bg=self.colors['card'], bd=0)
        form_card.pack(fill=tk.X, padx=1, pady=1)
        
        form_inner = tk.Frame(form_card, bg=self.colors['card'])
        form_inner.pack(padx=25, pady=25, fill=tk.X)
        
        tk.Label(form_inner, text=f"{self.icons['enrollment']} تسجيل طالب في مجموعة", 
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 19, 'bold')).pack(anchor=tk.E, pady=(0, 5))
        
        tk.Frame(form_inner, bg=self.colors['border'], height=2).pack(fill=tk.X, pady=(5, 20))
        
        # حقول الاختيار - RTL
        fields_frame = tk.Frame(form_inner, bg=self.colors['card'])
        fields_frame.pack(fill=tk.X)
        
        # الطالب
        student_row = tk.Frame(fields_frame, bg=self.colors['card'])
        student_row.pack(fill=tk.X, pady=10)
        
        tk.Label(student_row, text=f"{self.icons['student']} اختر الطالب:",
                bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 12, 'bold')).pack(side=tk.RIGHT, padx=(0, 15))
        
        combo_frame1 = tk.Frame(student_row, bg=self.colors['border'])
        combo_frame1.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.enroll_student_combo = ttk.Combobox(combo_frame1, width=40, font=('Segoe UI', 18))
        self.enable_search(self.enroll_student_combo)
        self.enroll_student_combo.pack(padx=1, pady=1, ipady=6)
        
        # المجموعة
        group_row = tk.Frame(fields_frame, bg=self.colors['card'])
        group_row.pack(fill=tk.X, pady=10)
        
        tk.Label(group_row, text=f"{self.icons['groups']} اختر المجموعة:",
                bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 12, 'bold')).pack(side=tk.RIGHT, padx=(0, 15))
        
        combo_frame2 = tk.Frame(group_row, bg=self.colors['border'])
        combo_frame2.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.enroll_group_combo = ttk.Combobox(combo_frame2, width=40, font=('Segoe UI', 18))
        self.enable_search(self.enroll_group_combo)
        self.enroll_group_combo.pack(padx=1, pady=1, ipady=6)
        
        # أزرار
        btn_frame = tk.Frame(form_inner, bg=self.colors['card'])
        btn_frame.pack(pady=(25, 0))
        
        self.create_modern_button(btn_frame, "تحديث القوائم", self.refresh_enrollment_combos, 
                                  'info', self.icons['refresh']).pack(side=tk.LEFT, padx=5)
        self.create_modern_button(btn_frame, "إلغاء التسجيل", self.unenroll_student, 
                                  'danger', self.icons['delete']).pack(side=tk.LEFT, padx=5)
        self.create_modern_button(btn_frame, "تسجيل الطالب", self.enroll_student, 
                                  'success', self.icons['add']).pack(side=tk.LEFT, padx=5)
        
        # جدول العرض - Modern
        display_outer = tk.Frame(main_container, bg=self.colors['border'], bd=0)
        display_outer.pack(fill=tk.BOTH, expand=True)
        
        display_card = tk.Frame(display_outer, bg=self.colors['card'], bd=0)
        display_card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        display_inner = tk.Frame(display_card, bg=self.colors['card'])
        display_inner.pack(padx=25, pady=25, fill=tk.BOTH, expand=True)
        
        tk.Label(display_inner, text=f"{self.icons['students']} الطلبة المسجلين", 
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 19, 'bold')).pack(anchor=tk.E, pady=(0, 5))
        
        tk.Frame(display_inner, bg=self.colors['border'], height=2).pack(fill=tk.X, pady=(5, 15))
        
        tree_outer = tk.Frame(display_inner, bg='#D1D5DB', bd=0)
        tree_outer.pack(fill=tk.BOTH, expand=True)
        
        tree_frame = tk.Frame(tree_outer, bg='#FFFFFF')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        columns = ("تاريخ التسجيل", "المجموعة", "الطالب", "ID")
        self.enrollment_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        
        self.enrollment_tree.column("ID", width=60, anchor='center')
        self.enrollment_tree.column("الطالب", width=220, anchor='e')
        self.enrollment_tree.column("المجموعة", width=220, anchor='e')
        self.enrollment_tree.column("تاريخ التسجيل", width=150, anchor='center')
        
        for col in columns:
            self.enrollment_tree.heading(col, text=col)
        
        self.enrollment_tree.tag_configure('oddrow', background='#F3F4F6', foreground='#111827')
        self.enrollment_tree.tag_configure('evenrow', background='#FFFFFF', foreground='#111827')
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.enrollment_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.enrollment_tree.xview)
        self.enrollment_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.enrollment_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # تحميل البيانات
        self.refresh_enrollment_combos()
        self.load_enrollments()
    
    def create_notifications_tab_for_page(self, parent):
        """محتوى صفحة الإشعارات - Modern Premium UI"""
        tab = parent
        
        # Container رئيسي مع خلفية حديثة
        main_container = tk.Frame(tab, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # ===================
        # قسم الإحصائيات - Modern Gradient Cards
        # ===================
        top_section = tk.Frame(main_container, bg=self.colors['bg'])
        top_section.pack(fill=tk.X, pady=(0, 20))
        
        # بطاقة الإشعارات غير المقروءة - Red Accent
        unread_outer = tk.Frame(top_section, bg='#DC2626', bd=0)
        unread_outer.pack(side=tk.RIGHT, padx=(0, 15))
        
        unread_card = tk.Frame(unread_outer, bg='#EF4444', bd=0)
        unread_card.pack(padx=2, pady=2)
        
        unread_inner = tk.Frame(unread_card, bg='#EF4444')
        unread_inner.pack(padx=30, pady=20)
        
        tk.Label(unread_inner, text="🔴 غير مقروءة", 
                bg='#EF4444', fg='#FEE2E2',
                font=('Segoe UI', 11, 'bold')).pack()
        self.unread_count_label = tk.Label(unread_inner, text="0", 
                                           bg='#EF4444', fg='white',
                                           font=('Segoe UI', 36, 'bold'))
        self.unread_count_label.pack(pady=(5, 0))
        tk.Label(unread_inner, text="إشعار", 
                bg='#EF4444', fg='#FEE2E2',
                font=('Segoe UI', 10)).pack()
        
        # بطاقة إجمالي الإشعارات - Primary Color
        total_outer = tk.Frame(top_section, bg=self.colors['primary_dark'], bd=0)
        total_outer.pack(side=tk.RIGHT, padx=(0, 15))
        
        total_card = tk.Frame(total_outer, bg=self.colors['primary'], bd=0)
        total_card.pack(padx=2, pady=2)
        
        total_inner = tk.Frame(total_card, bg=self.colors['primary'])
        total_inner.pack(padx=30, pady=20)
        
        tk.Label(total_inner, text="🔔 الإجمالي", 
                bg=self.colors['primary'], fg=self.colors['primary_light'],
                font=('Segoe UI', 11, 'bold')).pack()
        self.total_notif_label = tk.Label(total_inner, text="0", 
                                          bg=self.colors['primary'], fg='white',
                                          font=('Segoe UI', 36, 'bold'))
        self.total_notif_label.pack(pady=(5, 0))
        tk.Label(total_inner, text="إشعار", 
                bg=self.colors['primary'], fg=self.colors['primary_light'],
                font=('Segoe UI', 10)).pack()
        
        # بطاقة أزرار الإجراءات - Modern Control Panel
        actions_outer = tk.Frame(top_section, bg=self.colors['border'], bd=0)
        actions_outer.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        actions_card = tk.Frame(actions_outer, bg=self.colors['card'], bd=0)
        actions_card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        actions_inner = tk.Frame(actions_card, bg=self.colors['card'])
        actions_inner.pack(padx=20, pady=20, fill=tk.X)
        
        tk.Label(actions_inner, text=f"{self.icons['settings']} لوحة التحكم", 
                bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 14, 'bold')).pack(anchor=tk.E, pady=(0, 15))
        
        # أزرار الإجراءات في صف واحد
        btn_row = tk.Frame(actions_inner, bg=self.colors['card'])
        btn_row.pack(fill=tk.X)
        
        self.create_modern_button(btn_row, "إعدادات", 
                                 self.show_notification_settings, 
                                 'secondary', self.icons['settings']).pack(side=tk.RIGHT, padx=5)
        
        self.create_modern_button(btn_row, "تحديث", 
                                 self.refresh_notifications,
                                 'success', self.icons['refresh']).pack(side=tk.RIGHT, padx=5)
        
        self.create_modern_button(btn_row, "تعليم الكل كمقروء", 
                                 self.mark_all_read,
                                 'info', self.icons['check']).pack(side=tk.RIGHT, padx=5)
        
        # ===================
        # قسم عرض الإشعارات - Premium Card
        # ===================
        display_outer = tk.Frame(main_container, bg=self.colors['border'], bd=0)
        display_outer.pack(fill=tk.BOTH, expand=True)
        
        display_card = tk.Frame(display_outer, bg=self.colors['card'], bd=0)
        display_card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        display_inner = tk.Frame(display_card, bg=self.colors['card'])
        display_inner.pack(padx=25, pady=25, fill=tk.BOTH, expand=True)
        
        # عنوان مع أيقونة
        header_row = tk.Frame(display_inner, bg=self.colors['card'])
        header_row.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(header_row, text=f"{self.icons['notification']} الإشعارات النشطة", 
                bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 19, 'bold')).pack(side=tk.RIGHT)
        
        tk.Label(header_row, text="انقر مرتين لعرض التفاصيل", 
                bg=self.colors['card'], fg=self.colors['text_light'],
                font=('Segoe UI', 11)).pack(side=tk.LEFT)
        
        # Separator line
        tk.Frame(display_inner, bg=self.colors['border'], height=2).pack(fill=tk.X, pady=(5, 15))
        
        # إطار الجدول مع حدود حديثة
        tree_outer = tk.Frame(display_inner, bg='#D1D5DB', bd=0)
        tree_outer.pack(fill=tk.BOTH, expand=True)
        
        tree_frame = tk.Frame(tree_outer, bg='#FFFFFF')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # جدول الإشعارات - RTL مع أعمدة محسنة
        columns = ("التاريخ", "الطالب", "الرسالة", "العنوان", "الأولوية", "الحالة", "ID")
        self.notifications_tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                              height=15, selectmode='browse')
        
        self.notifications_tree.column("التاريخ", width=140, anchor='center')
        self.notifications_tree.column("الطالب", width=160, anchor='e')
        self.notifications_tree.column("الرسالة", width=350, anchor='e')
        self.notifications_tree.column("العنوان", width=180, anchor='e')
        self.notifications_tree.column("الأولوية", width=100, anchor='center')
        self.notifications_tree.column("الحالة", width=100, anchor='center')
        self.notifications_tree.column("ID", width=50, anchor='center')
        
        for col in columns:
            self.notifications_tree.heading(col, text=col)
        
        # تلوين حسب الأولوية والحالة - Modern Vibrant Colors
        self.notifications_tree.tag_configure('unread', 
                                             background='#FEF3C7', 
                                             foreground='#92400E', 
                                             font=('Segoe UI', 13, 'bold'))
        self.notifications_tree.tag_configure('high', 
                                             background='#FEE2E2', 
                                             foreground='#991B1B', 
                                             font=('Segoe UI', 13, 'bold'))
        self.notifications_tree.tag_configure('normal', 
                                             background='#FFFFFF', 
                                             foreground='#111827',
                                             font=('Segoe UI', 13))
        self.notifications_tree.tag_configure('read', 
                                             background='#F9FAFB', 
                                             foreground='#9CA3AF',
                                             font=('Segoe UI', 13))
        
        # Scrollbars مع تصميم حديث
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.notifications_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.notifications_tree.xview)
        self.notifications_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.notifications_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # حدث النقر المزدوج
        self.notifications_tree.bind("<Double-1>", self.view_notification_details)
        
        # تحميل الإشعارات
        self.load_notifications()
    
    def create_payments_tab_for_page(self, parent):
        """محتوى صفحة الدفعات - Modern UI"""
        main_container = tk.Frame(parent, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # نموذج الدفع - Modern Card
        form_outer = tk.Frame(main_container, bg=self.colors['border'], bd=0)
        form_outer.pack(fill=tk.X, pady=(0, 20))
        
        form_card = tk.Frame(form_outer, bg=self.colors['card'], bd=0)
        form_card.pack(fill=tk.X, padx=1, pady=1)
        
        form_inner = tk.Frame(form_card, bg=self.colors['card'])
        form_inner.pack(padx=25, pady=25, fill=tk.X)
        
        tk.Label(form_inner, text=f"{self.icons['payments']} تسجيل دفعة جديدة", 
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 19, 'bold')).pack(anchor=tk.E, pady=(0, 5))
        
        tk.Frame(form_inner, bg=self.colors['border'], height=2).pack(fill=tk.X, pady=(5, 20))
        
        fields_frame = tk.Frame(form_inner, bg=self.colors['card'])
        fields_frame.pack(fill=tk.X)
        
        # الصف الأول - Combos
        row1 = tk.Frame(fields_frame, bg=self.colors['card'])
        row1.pack(fill=tk.X, pady=8)
        
        # المجموعة
        group_label = tk.Frame(row1, bg=self.colors['card'])
        group_label.pack(side=tk.LEFT, padx=(15, 0))
        tk.Label(group_label, text=f"{self.icons['groups']} المجموعة:",
                bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 12, 'bold')).pack()
        
        combo_frame2 = tk.Frame(row1, bg=self.colors['border'])
        combo_frame2.pack(side=tk.LEFT, padx=(10, 15))
        self.payment_group_combo = ttk.Combobox(combo_frame2, width=25, font=('Segoe UI', 14))
        self.enable_search(self.payment_group_combo)
        self.payment_group_combo.pack(padx=1, pady=1, ipady=6)
        # ربط حدث تغيير المجموعة لتصفية الطلاب
        self.payment_group_combo.bind('<<ComboboxSelected>>', self.on_payment_group_change)
        
        # الطالب
        student_label = tk.Frame(row1, bg=self.colors['card'])
        student_label.pack(side=tk.RIGHT)
        tk.Label(student_label, text=f"{self.icons['student']} الطالب:",
                bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 12, 'bold')).pack()
        
        combo_frame1 = tk.Frame(row1, bg=self.colors['border'])
        combo_frame1.pack(side=tk.RIGHT, padx=(0, 10))
        self.payment_student_combo = ttk.Combobox(combo_frame1, width=30, font=('Segoe UI', 14))
        self.enable_search(self.payment_student_combo)
        self.payment_student_combo.pack(padx=1, pady=1, ipady=6)
        
        # الصف الثاني - Amount & Date
        row2 = tk.Frame(fields_frame, bg=self.colors['card'])
        row2.pack(fill=tk.X, pady=8)
        
        # التاريخ (يسار)
        date_container, self.payment_date = self.create_modern_input(
            row2, "تاريخ الدفع", self.icons['calendar'], 20)
        date_container.pack(side=tk.LEFT, padx=(15, 0))
        self.payment_date.insert(0, date.today().strftime("%Y-%m-%d"))
        
        # المبلغ (يمين)
        amount_container, self.payment_amount = self.create_modern_input(
            row2, "المبلغ المدفوع", self.icons['payment'], 20)
        amount_container.pack(side=tk.RIGHT)
        
        # الصف الثالث - Notes
        row3 = tk.Frame(fields_frame, bg=self.colors['card'])
        row3.pack(fill=tk.X, pady=8)
        
        notes_container, self.payment_notes = self.create_modern_input(
            row3, "ملاحظات (اختياري)", self.icons['info'], 60)
        notes_container.pack(side=tk.RIGHT)
        
        # أزرار
        btn_frame = tk.Frame(form_inner, bg=self.colors['card'])
        btn_frame.pack(pady=(25, 0))
        
        self.create_modern_button(btn_frame, "تحديث", self.refresh_payment_combos, 
                                  'info', self.icons['refresh']).pack(side=tk.LEFT, padx=5)
        self.create_modern_button(btn_frame, "حذف", self.delete_payment, 
                                  'danger', self.icons['delete']).pack(side=tk.LEFT, padx=5)
        self.create_modern_button(btn_frame, "تسجيل الدفعة", self.add_payment, 
                                  'success', self.icons['save']).pack(side=tk.LEFT, padx=5)
        
        # جدول العرض - Modern
        display_outer = tk.Frame(main_container, bg=self.colors['border'], bd=0)
        display_outer.pack(fill=tk.BOTH, expand=True)
        
        display_card = tk.Frame(display_outer, bg=self.colors['card'], bd=0)
        display_card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        display_inner = tk.Frame(display_card, bg=self.colors['card'])
        display_inner.pack(padx=25, pady=25, fill=tk.BOTH, expand=True)
        
        tk.Label(display_inner, text=f"{self.icons['payments']} سجل الدفعات", 
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 19, 'bold')).pack(anchor=tk.E, pady=(0, 5))
        
        tk.Frame(display_inner, bg=self.colors['border'], height=2).pack(fill=tk.X, pady=(5, 15))
        
        tree_outer = tk.Frame(display_inner, bg='#D1D5DB', bd=0)
        tree_outer.pack(fill=tk.BOTH, expand=True)
        
        tree_frame = tk.Frame(tree_outer, bg='#FFFFFF')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        columns = ("ملاحظات", "التاريخ", "المبلغ", "المجموعة", "الطالب", "ID")
        self.payments_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        
        self.payments_tree.column("ID", width=60, anchor='center')
        self.payments_tree.column("الطالب", width=180, anchor='e')
        self.payments_tree.column("المجموعة", width=180, anchor='e')
        self.payments_tree.column("المبلغ", width=100, anchor='center')
        self.payments_tree.column("التاريخ", width=120, anchor='center')
        self.payments_tree.column("ملاحظات", width=200, anchor='e')
        
        for col in columns:
            self.payments_tree.heading(col, text=col)
        
        self.payments_tree.tag_configure('oddrow', background='#F3F4F6', foreground='#111827')
        self.payments_tree.tag_configure('evenrow', background='#FFFFFF', foreground='#111827')
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.payments_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.payments_tree.xview)
        self.payments_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.payments_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # تحميل البيانات
        self.refresh_payment_combos()
        self.load_payments()
    
    def create_attendance_tab_for_page(self, parent):
        """محتوى صفحة الحضور - Modern UI"""
        main_container = tk.Frame(parent, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # نموذج الحضور - Modern Card
        form_outer = tk.Frame(main_container, bg=self.colors['border'], bd=0)
        form_outer.pack(fill=tk.X, pady=(0, 20))
        
        form_card = tk.Frame(form_outer, bg=self.colors['card'], bd=0)
        form_card.pack(fill=tk.X, padx=1, pady=1)
        
        form_inner = tk.Frame(form_card, bg=self.colors['card'])
        form_inner.pack(padx=25, pady=25, fill=tk.X)
        
        tk.Label(form_inner, text=f"{self.icons['attendance']} تسجيل حضور/غياب", 
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 19, 'bold')).pack(anchor=tk.E, pady=(0, 5))
        
        tk.Frame(form_inner, bg=self.colors['border'], height=2).pack(fill=tk.X, pady=(5, 20))
        
        fields_frame = tk.Frame(form_inner, bg=self.colors['card'])
        fields_frame.pack(fill=tk.X)
        
        # الصف الأول - Combos
        row1 = tk.Frame(fields_frame, bg=self.colors['card'])
        row1.pack(fill=tk.X, pady=8)
        
        # المجموعة
        group_label = tk.Frame(row1, bg=self.colors['card'])
        group_label.pack(side=tk.LEFT, padx=(15, 0))
        tk.Label(group_label, text=f"{self.icons['groups']} المجموعة:",
                bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 12, 'bold')).pack()
        
        combo_frame2 = tk.Frame(row1, bg=self.colors['border'])
        combo_frame2.pack(side=tk.LEFT, padx=(10, 15))
        self.attendance_group_combo = ttk.Combobox(combo_frame2, width=25, font=('Segoe UI', 14))
        self.enable_search(self.attendance_group_combo)
        self.attendance_group_combo.pack(padx=1, pady=1, ipady=6)
        # ربط حدث تغيير المجموعة لتصفية الطلاب
        self.attendance_group_combo.bind('<<ComboboxSelected>>', self.on_attendance_group_change)
        
        # الطالب
        student_label = tk.Frame(row1, bg=self.colors['card'])
        student_label.pack(side=tk.RIGHT)
        tk.Label(student_label, text=f"{self.icons['student']} الطالب:",
                bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 12, 'bold')).pack()
        
        combo_frame1 = tk.Frame(row1, bg=self.colors['border'])
        combo_frame1.pack(side=tk.RIGHT, padx=(0, 10))
        self.attendance_student_combo = ttk.Combobox(combo_frame1, width=30, font=('Segoe UI', 14))
        self.enable_search(self.attendance_student_combo)
        self.attendance_student_combo.pack(padx=1, pady=1, ipady=6)
        
        # الصف الثاني - Status & Date
        row2 = tk.Frame(fields_frame, bg=self.colors['card'])
        row2.pack(fill=tk.X, pady=8)
        
        # التاريخ (يسار)
        date_container, self.attendance_date = self.create_modern_input(
            row2, "تاريخ الحضور", self.icons['calendar'], 20)
        date_container.pack(side=tk.LEFT, padx=(15, 0))
        self.attendance_date.insert(0, date.today().strftime("%Y-%m-%d"))
        
        # الحالة (يمين)
        status_label = tk.Frame(row2, bg=self.colors['card'])
        status_label.pack(side=tk.RIGHT)
        tk.Label(status_label, text=f"{self.icons['attendance']} الحالة:",
                bg=self.colors['card'], fg=self.colors['text'],
                font=('Segoe UI', 12, 'bold')).pack()
        
        status_frame = tk.Frame(row2, bg=self.colors['border'])
        status_frame.pack(side=tk.RIGHT, padx=(0, 10))
        self.attendance_status = ttk.Combobox(status_frame, width=18, values=["حاضر", "غائب", "غياب بعذر"], font=('Segoe UI', 14))
        self.enable_search(self.attendance_status)
        self.attendance_status.all_values = ["حاضر", "غائب", "غياب بعذر"]
        self.attendance_status.current(0)
        self.attendance_status.pack(padx=1, pady=1, ipady=6)
        
        # الصف الثالث - Notes
        row3 = tk.Frame(fields_frame, bg=self.colors['card'])
        row3.pack(fill=tk.X, pady=8)
        
        notes_container, self.attendance_notes = self.create_modern_input(
            row3, "ملاحظات (اختياري)", self.icons['info'], 60)
        notes_container.pack(side=tk.RIGHT)
        
        # أزرار
        btn_frame = tk.Frame(form_inner, bg=self.colors['card'])
        btn_frame.pack(pady=(25, 0))
        
        self.create_modern_button(btn_frame, "تحديث", self.refresh_attendance_combos, 
                                  'info', self.icons['refresh']).pack(side=tk.LEFT, padx=5)
        self.create_modern_button(btn_frame, "حذف", self.delete_attendance, 
                                  'danger', self.icons['delete']).pack(side=tk.LEFT, padx=5)
        self.create_modern_button(btn_frame, "تسجيل الحضور", self.add_attendance, 
                                  'success', self.icons['save']).pack(side=tk.LEFT, padx=5)
        
        # جدول العرض - Modern
        display_outer = tk.Frame(main_container, bg=self.colors['border'], bd=0)
        display_outer.pack(fill=tk.BOTH, expand=True)
        
        display_card = tk.Frame(display_outer, bg=self.colors['card'], bd=0)
        display_card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        display_inner = tk.Frame(display_card, bg=self.colors['card'])
        display_inner.pack(padx=25, pady=25, fill=tk.BOTH, expand=True)
        
        tk.Label(display_inner, text=f"{self.icons['attendance']} سجل الحضور", 
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 19, 'bold')).pack(anchor=tk.E, pady=(0, 5))
        
        tk.Frame(display_inner, bg=self.colors['border'], height=2).pack(fill=tk.X, pady=(5, 15))
        
        tree_outer = tk.Frame(display_inner, bg='#D1D5DB', bd=0)
        tree_outer.pack(fill=tk.BOTH, expand=True)
        
        tree_frame = tk.Frame(tree_outer, bg='#FFFFFF')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        columns = ("ملاحظات", "التاريخ", "الحالة", "المجموعة", "الطالب", "ID")
        self.attendance_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        
        self.attendance_tree.column("ID", width=60, anchor='center')
        self.attendance_tree.column("الطالب", width=180, anchor='e')
        self.attendance_tree.column("المجموعة", width=250, anchor='e')
        self.attendance_tree.column("الحالة", width=100, anchor='center')
        self.attendance_tree.column("التاريخ", width=120, anchor='center')
        self.attendance_tree.column("ملاحظات", width=200, anchor='e')
        
        for col in columns:
            self.attendance_tree.heading(col, text=col)
        
        self.attendance_tree.tag_configure('oddrow', background='#F3F4F6', foreground='#111827')
        self.attendance_tree.tag_configure('evenrow', background='#FFFFFF', foreground='#111827')
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.attendance_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.attendance_tree.xview)
        self.attendance_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.attendance_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # تحميل البيانات
        self.refresh_attendance_combos()
        self.load_attendance()
    
    def create_reports_tab_for_page(self, parent):
        """محتوى صفحة التقارير - Modern UI"""
        main_container = tk.Frame(parent, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # أزرار التقارير - Modern Card
        options_outer = tk.Frame(main_container, bg=self.colors['border'], bd=0)
        options_outer.pack(fill=tk.X, pady=(0, 20))
        
        options_card = tk.Frame(options_outer, bg=self.colors['card'], bd=0)
        options_card.pack(fill=tk.X, padx=1, pady=1)
        
        options_inner = tk.Frame(options_card, bg=self.colors['card'])
        options_inner.pack(padx=25, pady=25, fill=tk.X)
        
        tk.Label(options_inner, text=f"{self.icons['reports']} اختر التقرير المطلوب", 
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 19, 'bold')).pack(anchor=tk.E, pady=(0, 5))
        
        tk.Frame(options_inner, bg=self.colors['border'], height=2).pack(fill=tk.X, pady=(5, 20))
        
        btn_frame = tk.Frame(options_inner, bg=self.colors['card'])
        btn_frame.pack()
        
        self.create_modern_button(btn_frame, "تقرير الحضور", self.show_attendance_report, 
                                  'success', self.icons['attendance']).pack(side=tk.RIGHT, padx=5)
        self.create_modern_button(btn_frame, "تقرير الدفعات", self.show_payments_report, 
                                  'info', self.icons['payments']).pack(side=tk.RIGHT, padx=5)
        self.create_modern_button(btn_frame, "تقرير المجموعات", self.show_groups_report, 
                                  'primary', self.icons['groups']).pack(side=tk.RIGHT, padx=5)
        self.create_modern_button(btn_frame, "تقرير الطلبة", self.show_students_report, 
                                  'primary', self.icons['student']).pack(side=tk.RIGHT, padx=5)
        
        # عرض التقرير - Modern Card
        display_outer = tk.Frame(main_container, bg=self.colors['border'], bd=0)
        display_outer.pack(fill=tk.BOTH, expand=True)
        
        display_card = tk.Frame(display_outer, bg=self.colors['card'], bd=0)
        display_card.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        display_inner = tk.Frame(display_card, bg=self.colors['card'])
        display_inner.pack(padx=25, pady=25, fill=tk.BOTH, expand=True)
        
        tk.Label(display_inner, text=f"{self.icons['reports']} نتائج التقرير", 
                bg=self.colors['card'],
                fg=self.colors['text'],
                font=('Segoe UI', 19, 'bold')).pack(anchor=tk.E, pady=(0, 5))
        
        tk.Frame(display_inner, bg=self.colors['border'], height=2).pack(fill=tk.X, pady=(5, 15))
        
        self.report_text = scrolledtext.ScrolledText(display_inner, width=100, height=20, 
                                                     font=("Segoe UI", 11),
                                                     bg='#FFFFFF', fg=self.colors['text'],
                                                     relief=tk.FLAT, bd=0)
        self.report_text.pack(fill=tk.BOTH, expand=True)
    
    # ========== وظائف الطلبة ==========
    
    def add_student(self):
        """إضافة طالب جديد"""
        name = self.student_name.get().strip()
        if not name:
            messagebox.showerror("خطأ", "يرجى إدخال اسم الطالب")
            return
        
        phone = self.student_phone.get().strip()
        email = self.student_email.get().strip()
        address = self.student_address.get().strip()
        
        try:
            self.db.execute_query(
                "INSERT INTO students (name, phone, email, address) VALUES (?, ?, ?, ?)",
                (name, phone, email, address)
            )
            messagebox.showinfo("نجح", "تم إضافة الطالب بنجاح")
            self.clear_student_fields()
            self.load_students()
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل إضافة الطالب: {str(e)}")
    
    def update_student(self):
        """تحديث بيانات طالب"""
        selected = self.students_tree.selection()
        if not selected:
            messagebox.showerror("خطأ", "يرجى اختيار طالب للتحديث")
            return
        
        # ID في المكان الأخير (index 5)
        student_id = self.students_tree.item(selected[0])["values"][5]
        name = self.student_name.get().strip()
        
        if not name:
            messagebox.showerror("خطأ", "يرجى إدخال اسم الطالب")
            return
        
        phone = self.student_phone.get().strip()
        email = self.student_email.get().strip()
        address = self.student_address.get().strip()
        
        try:
            self.db.execute_query(
                "UPDATE students SET name=?, phone=?, email=?, address=? WHERE id=?",
                (name, phone, email, address, student_id)
            )
            messagebox.showinfo("نجح", "تم تحديث بيانات الطالب")
            self.clear_student_fields()
            self.load_students()
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل التحديث: {str(e)}")
    
    def delete_student(self):
        """حذف طالب"""
        selected = self.students_tree.selection()
        if not selected:
            messagebox.showerror("خطأ", "يرجى اختيار طالب للحذف")
            return
        
        # ID في المكان الأخير (index 5)
        student_id = self.students_tree.item(selected[0])["values"][5]
        
        if messagebox.askyesno("تأكيد", "هل تريد حذف هذا الطالب؟"):
            try:
                self.db.execute_query("DELETE FROM students WHERE id=?", (student_id,))
                messagebox.showinfo("نجح", "تم حذف الطالب")
                self.clear_student_fields()
                self.load_students()
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل الحذف: {str(e)}")
    
    def load_students(self, search_term=""):
        """تحميل قائمة الطلبة"""
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        if search_term and search_term != "ابحث عن طالب بالاسم، الهاتف، أو البريد...":
            # بحث مع فلتر
            query = """
                SELECT id, name, phone, email, address, 
                       datetime(created_at, 'localtime') as created_at 
                FROM students 
                WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?
                ORDER BY created_at DESC
            """
            search_pattern = f"%{search_term}%"
            students = self.db.fetch_all(query, (search_pattern, search_pattern, search_pattern))
        else:
            # جلب جميع الطلبة
            students = self.db.fetch_all("""
                SELECT id, name, phone, email, address, 
                       datetime(created_at, 'localtime') as created_at 
                FROM students 
                ORDER BY created_at DESC
            """)
        
        # إضافة الطلبة للجدول مع تلوين الصفوف - RTL (عكس الترتيب)
        for idx, student in enumerate(students):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            # تنسيق التاريخ
            created_at = student[5][:10] if len(student) > 5 and student[5] else ""
            # الترتيب: المجموعات (أيقونة)، تاريخ التسجيل، العنوان، البريد، الهاتف، الاسم، ID
            values = [self.icons['groups'], created_at, student[4], student[3], student[2], student[1], student[0]]
            self.students_tree.insert("", tk.END, values=values, tags=(tag,))
        
        # تحديث عداد الطلبة
        self.students_count_label.config(text=str(len(students)))
    
    def search_students(self):
        """البحث في قائمة الطلبة"""
        search_term = self.student_search_var.get()
        self.load_students(search_term)
    
    def view_student_details(self, event):
        """عرض تفاصيل الطالب في نافذة منبثقة"""
        selected = self.students_tree.selection()
        if not selected:
            return
        
        # ID في المكان الأخير (index 5)
        student_id = self.students_tree.item(selected[0])["values"][5]
        
        # جلب معلومات الطالب
        student = self.db.fetch_one("""
            SELECT id, name, phone, email, address, created_at 
            FROM students WHERE id=?
        """, (student_id,))
        
        if not student:
            return
        
        # جلب المجموعات المسجل فيها
        groups = self.db.fetch_all("""
            SELECT g.name, g.subject, g.teacher, sg.joined_at
            FROM student_groups sg
            JOIN groups g ON sg.group_id = g.id
            WHERE sg.student_id = ?
        """, (student_id,))
        
        # جلب إحصائيات الدفعات
        payments_stats = self.db.fetch_one("""
            SELECT COUNT(*), COALESCE(SUM(amount), 0)
            FROM payments WHERE student_id = ?
        """, (student_id,))
        
        # جلب إحصائيات الحضور
        attendance_stats = self.db.fetch_one("""
            SELECT 
                SUM(CASE WHEN status='حاضر' THEN 1 ELSE 0 END) as present,
                SUM(CASE WHEN status='غائب' THEN 1 ELSE 0 END) as absent,
                COUNT(*) as total
            FROM attendance WHERE student_id = ?
        """, (student_id,))
        
        # إنشاء نافذة التفاصيل
        details_window = tk.Toplevel(self.root)
        details_window.title(f"تفاصيل الطالب: {student[1]}")
        details_window.geometry("700x600")
        details_window.configure(bg=self.colors['bg'])
        details_window.transient(self.root)
        details_window.grab_set()
        
        # Container
        container = ttk.Frame(details_window)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header = tk.Frame(container, bg=self.colors['primary'], height=80)
        header.pack(fill=tk.X, pady=(0, 20))
        header.pack_propagate(False)
        
        tk.Label(header, text="👤", bg=self.colors['primary'], 
                font=('Arial', 32)).pack(side=tk.RIGHT, padx=20)
        
        info_frame = tk.Frame(header, bg=self.colors['primary'])
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        tk.Label(info_frame, text=student[1], bg=self.colors['primary'], 
                fg='white', font=('Arial', 16, 'bold')).pack(anchor=tk.E)
        tk.Label(info_frame, text=f"ID: {student[0]}", bg=self.colors['primary'], 
                fg='white', font=('Arial', 10)).pack(anchor=tk.E)
        
        # معلومات أساسية
        info_card = tk.Frame(container, bg=self.colors['card'], relief='raised', bd=2)
        info_card.pack(fill=tk.X, pady=(0, 15))
        
        info_inner = tk.Frame(info_card, bg=self.colors['card'])
        info_inner.pack(padx=20, pady=15, fill=tk.X)
        
        tk.Label(info_inner, text="📋 المعلومات الأساسية", 
                bg=self.colors['card'], font=('Arial', 12, 'bold')).pack(anchor=tk.E, pady=(0, 10))
        
        info_text = f"""
📞 الهاتف: {student[2] or 'غير محدد'}
📧 البريد: {student[3] or 'غير محدد'}
🏠 العنوان: {student[4] or 'غير محدد'}
📅 تاريخ التسجيل: {student[5][:10] if student[5] else 'غير محدد'}
        """
        
        tk.Label(info_inner, text=info_text, bg=self.colors['card'], 
                font=('Arial', 10), justify=tk.RIGHT).pack(anchor=tk.E)
        
        # إحصائيات سريعة
        stats_frame = ttk.Frame(container)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # الحضور
        attend_stat = tk.Frame(stats_frame, bg=self.colors['card'], relief='raised', bd=2)
        attend_stat.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(attend_stat, text="✅ نسبة الحضور", bg=self.colors['card'],
                font=('Arial', 9)).pack(pady=(10, 0))
        
        attend_pct = 0
        if attendance_stats and attendance_stats[2] > 0:
            attend_pct = (attendance_stats[0] / attendance_stats[2] * 100)
        
        tk.Label(attend_stat, text=f"{attend_pct:.0f}%", bg=self.colors['card'],
                fg=self.colors['warning'], font=('Arial', 24, 'bold')).pack(pady=(0, 10))
        
        # الدفعات
        payment_stat = tk.Frame(stats_frame, bg=self.colors['card'], relief='raised', bd=2)
        payment_stat.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 10))
        
        tk.Label(payment_stat, text="💰 إجمالي الدفعات", bg=self.colors['card'],
                font=('Arial', 9)).pack(pady=(10, 0))
        tk.Label(payment_stat, text=f"{payments_stats[1]:.0f}", bg=self.colors['card'],
                fg=self.colors['success'], font=('Arial', 24, 'bold')).pack(pady=(0, 10))
        
        # المجموعات
        group_stat = tk.Frame(stats_frame, bg=self.colors['card'], relief='raised', bd=2)
        group_stat.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(group_stat, text="📚 المجموعات", bg=self.colors['card'],
                font=('Arial', 9)).pack(pady=(10, 0))
        tk.Label(group_stat, text=str(len(groups)), bg=self.colors['card'],
                fg=self.colors['primary'], font=('Arial', 24, 'bold')).pack(pady=(0, 10))
        
        # المجموعات المسجل فيها
        groups_card = tk.Frame(container, bg=self.colors['card'], relief='raised', bd=2)
        groups_card.pack(fill=tk.BOTH, expand=True)
        
        groups_inner = tk.Frame(groups_card, bg=self.colors['card'])
        groups_inner.pack(padx=20, pady=15, fill=tk.BOTH, expand=True)
        
        tk.Label(groups_inner, text="📚 المجموعات المسجل فيها", 
                bg=self.colors['card'], font=('Arial', 12, 'bold')).pack(anchor=tk.E, pady=(0, 10))
        
        if groups:
            groups_text = scrolledtext.ScrolledText(groups_inner, height=8, font=('Arial', 10))
            groups_text.pack(fill=tk.BOTH, expand=True)
            
            for g in groups:
                groups_text.insert(tk.END, f"• {g[0]}\n")
                groups_text.insert(tk.END, f"  المادة: {g[1] or 'غير محدد'}\n")
                groups_text.insert(tk.END, f"  المعلم: {g[2] or 'غير محدد'}\n")
                groups_text.insert(tk.END, f"  تاريخ الانضمام: {g[3][:10] if g[3] else 'غير محدد'}\n\n")
            
            groups_text.config(state=tk.DISABLED)
        else:
            tk.Label(groups_inner, text="لم يتم التسجيل في أي مجموعة بعد", 
                    bg=self.colors['card'], fg=self.colors['text_light'],
                    font=('Arial', 10, 'italic')).pack()
        
        # زر الإغلاق
        tk.Button(container, text="إغلاق", bg=self.colors['text_light'], 
                 fg='white', font=('Arial', 10, 'bold'), padx=30, pady=8,
                 border=0, cursor='hand2', 
                 command=details_window.destroy).pack(pady=(15, 0))
    
    def select_student(self, event):
        """اختيار طالب من الجدول"""
        selected = self.students_tree.selection()
        if selected:
            values = self.students_tree.item(selected[0])["values"]
            # الترتيب الجديد: المجموعات، تاريخ التسجيل، العنوان، البريد، الهاتف، الاسم، ID
            # values[6]=ID, values[5]=الاسم, values[4]=الهاتف, values[3]=البريد, values[2]=العنوان
            self.student_name.delete(0, tk.END)
            self.student_name.insert(0, values[5])
            self.student_phone.delete(0, tk.END)
            self.student_phone.insert(0, values[4])
            self.student_email.delete(0, tk.END)
            self.student_email.insert(0, values[3])
            self.student_address.delete(0, tk.END)
            self.student_address.insert(0, values[2])
    
    def on_student_tree_click(self, event):
        """معالجة النقر على جدول الطلبة"""
        # تحديد العنصر والعمود المنقور
        region = self.students_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.students_tree.identify_column(event.x)
            selected = self.students_tree.selection()
            
            if selected and column == "#1":  # عمود المجموعات (العمود الأول)
                values = self.students_tree.item(selected[0])["values"]
                student_id = values[6]  # ID في العمود الأخير
                student_name = values[5]  # الاسم
                self.show_student_groups(student_id, student_name)
            else:
                # استدعاء الدالة الأصلية للتحديد
                self.select_student(event)
        else:
            self.select_student(event)
    
    def show_student_groups(self, student_id, student_name):
        """عرض مجموعات الطالب مع إحصائيات الحضور"""
        # إنشاء نافذة منبثقة
        dialog = tk.Toplevel(self.root)
        dialog.title(f"مجموعات الطالب: {student_name}")
        dialog.geometry("900x600")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Header
        header = tk.Frame(dialog, bg=self.colors['primary'], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text=f"{self.icons['students']} مجموعات الطالب: {student_name}",
                bg=self.colors['primary'], fg='white',
                font=('Segoe UI', 20, 'bold')).pack(pady=20)
        
        # Main content
        content = tk.Frame(dialog, bg=self.colors['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # جلب مجموعات الطالب
        query = """
            SELECT g.id, g.name, g.subject, g.teacher, g.schedule, g.fee
            FROM groups g
            INNER JOIN student_groups sg ON g.id = sg.group_id
            WHERE sg.student_id = ?
            ORDER BY g.name
        """
        groups = self.db.fetch_all(query, (student_id,))
        
        if not groups:
            tk.Label(content, text="لا توجد مجموعات مسجلة لهذا الطالب",
                    bg=self.colors['bg'], fg=self.colors['text_secondary'],
                    font=('Segoe UI', 16)).pack(pady=50)
        else:
            # جدول المجموعات مع الحضور
            tree_outer = tk.Frame(content, bg=self.colors['border'])
            tree_outer.pack(fill=tk.BOTH, expand=True)
            
            tree_frame = tk.Frame(tree_outer, bg='#FFFFFF')
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
            
            columns = ("النسبة %", "الغياب", "الحضور", "الرسوم", "الجدول", "المعلم", "المادة", "المجموعة")
            tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
            
            # تنسيق الأعمدة
            tree.column("المجموعة", width=220, anchor='e')
            tree.column("المادة", width=120, anchor='e')
            tree.column("المعلم", width=150, anchor='e')
            tree.column("الجدول", width=150, anchor='e')
            tree.column("الرسوم", width=80, anchor='center')
            tree.column("الحضور", width=80, anchor='center')
            tree.column("الغياب", width=80, anchor='center')
            tree.column("النسبة %", width=80, anchor='center')
            
            for col in columns:
                tree.heading(col, text=col)
            
            # إضافة البيانات
            for idx, group in enumerate(groups):
                group_id = group[0]
                
                # حساب إحصائيات الحضور
                attendance_stats = self.get_student_attendance_in_group(student_id, group_id)
                
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                values = [
                    f"{attendance_stats['percentage']:.1f}%",
                    attendance_stats['absent'],
                    attendance_stats['present'],
                    group[5],  # الرسوم
                    group[4],  # الجدول
                    group[3],  # المعلم
                    group[2],  # المادة
                    group[1]   # اسم المجموعة
                ]
                tree.insert("", tk.END, values=values, tags=(tag,))
            
            # Scrollbars
            vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            
            tree.grid(row=0, column=0, sticky='nsew')
            vsb.grid(row=0, column=1, sticky='ns')
            hsb.grid(row=1, column=0, sticky='ew')
            
            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)
        
        # زر الإغلاق
        btn_frame = tk.Frame(dialog, bg=self.colors['bg'])
        btn_frame.pack(pady=20)
        
        self.create_modern_button(btn_frame, "إغلاق", dialog.destroy,
                                  'secondary', self.icons['close']).pack()
    
    def get_student_attendance_in_group(self, student_id, group_id):
        """حساب إحصائيات حضور الطالب في مجموعة معينة"""
        # عدد أيام الحضور
        present_query = """
            SELECT COUNT(*) FROM attendance
            WHERE student_id = ? AND group_id = ? AND status = 'حاضر'
        """
        present_count = self.db.fetch_one(present_query, (student_id, group_id))[0]
        
        # عدد أيام الغياب
        absent_query = """
            SELECT COUNT(*) FROM attendance
            WHERE student_id = ? AND group_id = ? AND status IN ('غائب', 'غياب بعذر')
        """
        absent_count = self.db.fetch_one(absent_query, (student_id, group_id))[0]
        
        # حساب النسبة المئوية
        total = present_count + absent_count
        percentage = (present_count / total * 100) if total > 0 else 0
        
        return {
            'present': present_count,
            'absent': absent_count,
            'total': total,
            'percentage': percentage
        }
    
    def clear_student_fields(self):
        """مسح حقول الطالب"""
        self.student_name.delete(0, tk.END)
        self.student_phone.delete(0, tk.END)
        self.student_email.delete(0, tk.END)
        self.student_address.delete(0, tk.END)
    
    # ========== وظائف المجموعات ==========
    
    def add_group(self):
        """إضافة مجموعة جديدة"""
        name = self.group_name.get().strip()
        if not name:
            messagebox.showerror("خطأ", "يرجى إدخال اسم المجموعة")
            return
        
        subject = self.group_subject.get().strip()
        teacher = self.group_teacher.get().strip()
        schedule = self.group_schedule.get().strip()
        
        try:
            fee = float(self.group_fee.get().strip() or 0)
        except ValueError:
            messagebox.showerror("خطأ", "الرسوم يجب أن تكون رقماً")
            return
        
        try:
            self.db.execute_query(
                "INSERT INTO groups (name, subject, teacher, schedule, fee) VALUES (?, ?, ?, ?, ?)",
                (name, subject, teacher, schedule, fee)
            )
            messagebox.showinfo("نجح", "تم إضافة المجموعة بنجاح")
            self.clear_group_fields()
            self.load_groups()
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل إضافة المجموعة: {str(e)}")
    
    def update_group(self):
        """تحديث بيانات مجموعة"""
        selected = self.groups_tree.selection()
        if not selected:
            messagebox.showerror("خطأ", "يرجى اختيار مجموعة للتحديث")
            return
        
        # ID في المكان الأخير (index 5)
        group_id = self.groups_tree.item(selected[0])["values"][5]
        name = self.group_name.get().strip()
        
        if not name:
            messagebox.showerror("خطأ", "يرجى إدخال اسم المجموعة")
            return
        
        subject = self.group_subject.get().strip()
        teacher = self.group_teacher.get().strip()
        schedule = self.group_schedule.get().strip()
        
        try:
            fee = float(self.group_fee.get().strip() or 0)
        except ValueError:
            messagebox.showerror("خطأ", "الرسوم يجب أن تكون رقماً")
            return
        
        try:
            self.db.execute_query(
                "UPDATE groups SET name=?, subject=?, teacher=?, schedule=?, fee=? WHERE id=?",
                (name, subject, teacher, schedule, fee, group_id)
            )
            messagebox.showinfo("نجح", "تم تحديث بيانات المجموعة")
            self.clear_group_fields()
            self.load_groups()
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل التحديث: {str(e)}")
    
    def delete_group(self):
        """حذف مجموعة"""
        selected = self.groups_tree.selection()
        if not selected:
            messagebox.showerror("خطأ", "يرجى اختيار مجموعة للحذف")
            return
        
        # ID في المكان الأخير (index 5)
        group_id = self.groups_tree.item(selected[0])["values"][5]
        
        if messagebox.askyesno("تأكيد", "هل تريد حذف هذه المجموعة؟"):
            try:
                self.db.execute_query("DELETE FROM groups WHERE id=?", (group_id,))
                messagebox.showinfo("نجح", "تم حذف المجموعة")
                self.clear_group_fields()
                self.load_groups()
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل الحذف: {str(e)}")
    
    def load_groups(self):
        """تحميل قائمة المجموعات"""
        for item in self.groups_tree.get_children():
            self.groups_tree.delete(item)
        
        groups = self.db.fetch_all("SELECT id, name, subject, teacher, schedule, fee FROM groups ORDER BY id DESC")
        
        # إضافة المجموعات مع تلوين الصفوف - RTL
        for idx, group in enumerate(groups):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            # الترتيب RTL: عرض (أيقونة)، الرسوم، الجدول، المعلم، المادة، الاسم، ID
            values = [self.icons['info'], group[5], group[4], group[3], group[2], group[1], group[0]]
            self.groups_tree.insert("", tk.END, values=values, tags=(tag,))
    
    def select_group(self, event):
        """اختيار مجموعة من الجدول"""
        selected = self.groups_tree.selection()
        if selected:
            values = self.groups_tree.item(selected[0])["values"]
            # الترتيب الجديد: عرض، الرسوم، الجدول، المعلم، المادة، الاسم، ID
            # values[6]=ID, values[5]=الاسم, values[4]=المادة, values[3]=المعلم, values[2]=الجدول, values[1]=الرسوم
            self.group_name.delete(0, tk.END)
            self.group_name.insert(0, values[5])
            self.group_subject.delete(0, tk.END)
            self.group_subject.insert(0, values[4])
            self.group_teacher.delete(0, tk.END)
            self.group_teacher.insert(0, values[3])
            self.group_schedule.delete(0, tk.END)
            self.group_schedule.insert(0, values[2])
            self.group_fee.delete(0, tk.END)
            self.group_fee.insert(0, values[1])
    
    def on_group_tree_click(self, event):
        """معالجة النقر على جدول المجموعات"""
        # تحديد العنصر والعمود المنقور
        region = self.groups_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.groups_tree.identify_column(event.x)
            selected = self.groups_tree.selection()
            
            if selected and column == "#1":  # عمود العرض (العمود الأول)
                values = self.groups_tree.item(selected[0])["values"]
                teacher_name = values[3]  # المعلم
                self.show_teacher_groups(teacher_name)
            else:
                # استدعاء الدالة الأصلية للتحديد
                self.select_group(event)
        else:
            self.select_group(event)
    
    def show_teacher_groups(self, teacher_name):
        """عرض جميع مجموعات المعلم"""
        # إنشاء نافذة منبثقة
        dialog = tk.Toplevel(self.root)
        dialog.title(f"مجموعات المعلم: {teacher_name}")
        dialog.geometry("1000x600")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Header
        header = tk.Frame(dialog, bg=self.colors['primary'], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text=f"{self.icons['student']} مجموعات المعلم: {teacher_name}",
                bg=self.colors['primary'], fg='white',
                font=('Segoe UI', 20, 'bold')).pack(pady=20)
        
        # Main content
        content = tk.Frame(dialog, bg=self.colors['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # جلب مجموعات المعلم
        query = """
            SELECT id, name, subject, schedule, fee
            FROM groups
            WHERE teacher = ?
            ORDER BY name
        """
        groups = self.db.fetch_all(query, (teacher_name,))
        
        if not groups:
            tk.Label(content, text="لا توجد مجموعات لهذا المعلم",
                    bg=self.colors['bg'], fg=self.colors['text_secondary'],
                    font=('Segoe UI', 16)).pack(pady=50)
        else:
            # جدول المجموعات
            tree_outer = tk.Frame(content, bg=self.colors['border'])
            tree_outer.pack(fill=tk.BOTH, expand=True)
            
            tree_frame = tk.Frame(tree_outer, bg='#FFFFFF')
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
            
            columns = ("عدد الطلاب", "الرسوم", "الجدول", "المادة", "المجموعة", "ID")
            tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
            
            # تنسيق الأعمدة
            tree.column("ID", width=60, anchor='center')
            tree.column("المجموعة", width=200, anchor='e')
            tree.column("المادة", width=150, anchor='e')
            tree.column("الجدول", width=200, anchor='e')
            tree.column("الرسوم", width=100, anchor='center')
            tree.column("عدد الطلاب", width=100, anchor='center')
            
            for col in columns:
                tree.heading(col, text=col)
            
            # إضافة البيانات
            for idx, group in enumerate(groups):
                group_id = group[0]
                
                # حساب عدد الطلاب في المجموعة
                student_count_query = """
                    SELECT COUNT(*) FROM student_groups WHERE group_id = ?
                """
                student_count = self.db.fetch_one(student_count_query, (group_id,))[0]
                
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                values = [
                    student_count,  # عدد الطلاب
                    group[4],  # الرسوم
                    group[3],  # الجدول
                    group[2],  # المادة
                    group[1],  # اسم المجموعة
                    group[0]   # ID
                ]
                tree.insert("", tk.END, values=values, tags=(tag,))
            
            # Scrollbars
            vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            
            tree.grid(row=0, column=0, sticky='nsew')
            vsb.grid(row=0, column=1, sticky='ns')
            hsb.grid(row=1, column=0, sticky='ew')
            
            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)
        
        # زر الإغلاق
        btn_frame = tk.Frame(dialog, bg=self.colors['bg'])
        btn_frame.pack(pady=20)
        
        self.create_modern_button(btn_frame, "إغلاق", dialog.destroy,
                                  'secondary', self.icons['close']).pack()
    
    def refresh_group_teacher_combo(self):
        """تحديث قائمة المعلمين في dropdown المجموعات"""
        teachers = self.db.fetch_all("SELECT name FROM teachers ORDER BY name")
        teacher_names = [teacher[0] for teacher in teachers]
        self.group_teacher['values'] = teacher_names
        self.group_teacher.all_values = teacher_names
    
    def clear_group_fields(self):
        """مسح حقول المجموعة"""
        self.group_name.delete(0, tk.END)
        self.group_subject.delete(0, tk.END)
        self.group_teacher.delete(0, tk.END)
        self.group_schedule.delete(0, tk.END)
        self.group_fee.delete(0, tk.END)
    
    # ========== وظائف المعلمين ==========
    
    def add_teacher(self):
        """إضافة معلم جديد"""
        name = self.teacher_name.get().strip()
        phone = self.teacher_phone.get().strip()
        email = self.teacher_email.get().strip()
        specialization = self.teacher_specialization.get().strip()
        
        if not name:
            messagebox.showerror("خطأ", "يرجى إدخال اسم المعلم")
            return
        
        try:
            self.db.execute_query(
                "INSERT INTO teachers (name, phone, email, specialization) VALUES (?, ?, ?, ?)",
                (name, phone, email, specialization)
            )
            messagebox.showinfo("نجاح", "تم إضافة المعلم بنجاح!")
            self.clear_teacher_fields()
            self.load_teachers()
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل إضافة المعلم:\n{str(e)}")
    
    def update_teacher(self):
        """تحديث بيانات معلم"""
        selected = self.teachers_tree.selection()
        if not selected:
            messagebox.showwarning("تحذير", "يرجى اختيار معلم للتحديث")
            return
        
        values = self.teachers_tree.item(selected[0])["values"]
        teacher_id = values[6]  # ID in last column
        
        name = self.teacher_name.get().strip()
        phone = self.teacher_phone.get().strip()
        email = self.teacher_email.get().strip()
        specialization = self.teacher_specialization.get().strip()
        
        if not name:
            messagebox.showerror("خطأ", "يرجى إدخال اسم المعلم")
            return
        
        try:
            self.db.execute_query(
                "UPDATE teachers SET name=?, phone=?, email=?, specialization=? WHERE id=?",
                (name, phone, email, specialization, teacher_id)
            )
            messagebox.showinfo("نجاح", "تم تحديث بيانات المعلم بنجاح!")
            self.clear_teacher_fields()
            self.load_teachers()
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل تحديث المعلم:\n{str(e)}")
    
    def delete_teacher(self):
        """حذف معلم"""
        selected = self.teachers_tree.selection()
        if not selected:
            messagebox.showwarning("تحذير", "يرجى اختيار معلم للحذف")
            return
        
        values = self.teachers_tree.item(selected[0])["values"]
        teacher_id = values[6]
        teacher_name = values[5]
        
        confirm = messagebox.askyesno("تأكيد الحذف", 
                                     f"هل أنت متأكد من حذف المعلم '{teacher_name}'؟")
        if confirm:
            try:
                self.db.execute_query("DELETE FROM teachers WHERE id=?", (teacher_id,))
                messagebox.showinfo("نجاح", "تم حذف المعلم بنجاح!")
                self.clear_teacher_fields()
                self.load_teachers()
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل حذف المعلم:\n{str(e)}")
    
    def load_teachers(self):
        """تحميل قائمة المعلمين"""
        for item in self.teachers_tree.get_children():
            self.teachers_tree.delete(item)
        
        teachers = self.db.fetch_all(
            "SELECT id, name, phone, email, specialization FROM teachers ORDER BY name"
        )
        
        for idx, teacher in enumerate(teachers):
            teacher_id = teacher[0]
            teacher_name = teacher[1]
            
            # Count groups for this teacher
            group_count = self.db.fetch_one(
                "SELECT COUNT(*) FROM groups WHERE teacher = ?", (teacher_name,)
            )[0]
            
            # Count total students across all groups
            student_count = self.db.fetch_one("""
                SELECT COUNT(DISTINCT sg.student_id)
                FROM student_groups sg
                INNER JOIN groups g ON sg.group_id = g.id
                WHERE g.teacher = ?
            """, (teacher_name,))[0]
            
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            # Order: المجموعات، عدد الطلاب، التخصص، البريد، الهاتف، الاسم، ID
            values = [
                self.icons['info'],  # Icon for groups
                student_count,
                teacher[4],  # specialization
                teacher[3],  # email
                teacher[2],  # phone
                teacher[1],  # name
                teacher[0]   # id
            ]
            self.teachers_tree.insert("", tk.END, values=values, tags=(tag,))
        
        # Refresh the teacher dropdown in groups page
        self.refresh_group_teacher_combo()
    
    def select_teacher(self, event):
        """اختيار معلم من الجدول"""
        selected = self.teachers_tree.selection()
        if selected:
            values = self.teachers_tree.item(selected[0])["values"]
            # Order: المجموعات، عدد الطلاب، التخصص، البريد، الهاتف، الاسم، ID
            teacher_name = values[5]
            
            self.teacher_name.delete(0, tk.END)
            self.teacher_name.insert(0, teacher_name)
            self.teacher_phone.delete(0, tk.END)
            self.teacher_phone.insert(0, values[4])
            self.teacher_email.delete(0, tk.END)
            self.teacher_email.insert(0, values[3])
            self.teacher_specialization.delete(0, tk.END)
            self.teacher_specialization.insert(0, values[2])
            
            # Load teacher's groups in the display section
            self.load_teacher_groups_display(teacher_name)
    
    def load_teacher_groups_display(self, teacher_name):
        """تحميل مجموعات المعلم في قسم العرض"""
        # Clear existing data
        for item in self.teacher_groups_tree.get_children():
            self.teacher_groups_tree.delete(item)
        
        # Update label
        self.selected_teacher_label.config(text=f"{self.icons['groups']} مجموعات المعلم: {teacher_name}")
        
        # Fetch teacher's groups
        query = """
            SELECT id, name, subject, schedule, fee
            FROM groups
            WHERE teacher = ?
            ORDER BY name
        """
        groups = self.db.fetch_all(query, (teacher_name,))
        
        if not groups:
            # Show message if no groups
            self.teacher_groups_tree.insert("", tk.END, values=("", "", "", "لا توجد مجموعات", "", ""))
        else:
            for idx, group in enumerate(groups):
                group_id = group[0]
                
                # Count students in this group
                student_count_query = """
                    SELECT COUNT(*) FROM student_groups WHERE group_id = ?
                """
                student_count = self.db.fetch_one(student_count_query, (group_id,))[0]
                
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                values = [
                    student_count,  # عدد الطلاب
                    group[4],  # الرسوم
                    group[3],  # الجدول
                    group[2],  # المادة
                    group[1],  # اسم المجموعة
                    group[0]   # ID
                ]
                self.teacher_groups_tree.insert("", tk.END, values=values, tags=(tag,))
    
    def on_teacher_tree_click(self, event):
        """معالجة النقر على جدول المعلمين"""
        region = self.teachers_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.teachers_tree.identify_column(event.x)
            selected = self.teachers_tree.selection()
            
            if selected and column == "#1":  # المجموعات column (first column)
                values = self.teachers_tree.item(selected[0])["values"]
                teacher_name = values[5]  # الاسم
                self.show_teacher_groups(teacher_name)
            else:
                self.select_teacher(event)
        else:
            self.select_teacher(event)
    
    def clear_teacher_fields(self):
        """مسح حقول المعلم"""
        self.teacher_name.delete(0, tk.END)
        self.teacher_phone.delete(0, tk.END)
        self.teacher_email.delete(0, tk.END)
        self.teacher_specialization.delete(0, tk.END)
    
    # ========== وظائف التسجيل ==========
    
    def refresh_enrollment_combos(self):
        """تحديث قوائم الطلبة والمجموعات للتسجيل"""
        # الطلبة
        students = self.db.fetch_all("SELECT id, name FROM students")
        student_list = [f"{s[0]} - {s[1]}" for s in students]
        self.enroll_student_combo["values"] = student_list
        self.enroll_student_combo.all_values = student_list
        
        # المجموعات
        groups = self.db.fetch_all("SELECT id, name FROM groups")
        group_list = [f"{g[0]} - {g[1]}" for g in groups]
        self.enroll_group_combo["values"] = group_list
        self.enroll_group_combo.all_values = group_list
    
    def enroll_student(self):
        """تسجيل طالب في مجموعة"""
        student_sel = self.enroll_student_combo.get()
        group_sel = self.enroll_group_combo.get()
        
        if not student_sel or not group_sel:
            messagebox.showerror("خطأ", "يرجى اختيار الطالب والمجموعة")
            return
        
        student_id = self.get_id_from_combo(student_sel)
        group_id = self.get_id_from_combo(group_sel)
        
        if not student_id or not group_id:
            messagebox.showerror("خطأ", "يرجى اختيار طالب ومجموعة صحيحة من القائمة")
            return
        
        try:
            self.db.execute_query(
                "INSERT INTO student_groups (student_id, group_id) VALUES (?, ?)",
                (student_id, group_id)
            )
            messagebox.showinfo("نجح", "تم تسجيل الطالب في المجموعة")
            self.load_enrollments()
        except sqlite3.IntegrityError:
            messagebox.showerror("خطأ", "الطالب مسجل مسبقاً في هذه المجموعة")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل التسجيل: {str(e)}")
    
    def unenroll_student(self):
        """إلغاء تسجيل طالب من مجموعة"""
        selected = self.enrollment_tree.selection()
        if not selected:
            messagebox.showerror("خطأ", "يرجى اختيار تسجيل للإلغاء")
            return
        
        # ID في المكان الأخير (index 3)
        enrollment_id = self.enrollment_tree.item(selected[0])["values"][3]
        
        if messagebox.askyesno("تأكيد", "هل تريد إلغاء هذا التسجيل؟"):
            try:
                self.db.execute_query("DELETE FROM student_groups WHERE id=?", (enrollment_id,))
                messagebox.showinfo("نجح", "تم إلغاء التسجيل")
                self.load_enrollments()
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل الإلغاء: {str(e)}")
    
    def load_enrollments(self):
        """تحميل قائمة التسجيلات"""
        for item in self.enrollment_tree.get_children():
            self.enrollment_tree.delete(item)
        
        query = """
            SELECT sg.id, s.name, g.name, sg.joined_at
            FROM student_groups sg
            JOIN students s ON sg.student_id = s.id
            JOIN groups g ON sg.group_id = g.id
            ORDER BY sg.joined_at DESC
        """
        enrollments = self.db.fetch_all(query)
        for idx, enrollment in enumerate(enrollments):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            # الترتيب RTL: تاريخ التسجيل، المجموعة، الطالب، ID
            values = [enrollment[3][:10] if enrollment[3] else "", enrollment[2], enrollment[1], enrollment[0]]
            self.enrollment_tree.insert("", tk.END, values=values, tags=(tag,))
    
    # ========== وظائف الدفعات ==========
    
    def refresh_payment_combos(self):
        """تحديث قوائم الطلبة والمجموعات للدفعات"""
        # المجموعات أولاً
        groups = self.db.fetch_all("SELECT id, name FROM groups")
        group_list = [f"{g[0]} - {g[1]}" for g in groups]
        self.payment_group_combo["values"] = group_list
        self.payment_group_combo.all_values = group_list
        
        # الطلبة - جميع الطلاب مبدئياً
        students = self.db.fetch_all("SELECT id, name FROM students")
        student_list = [f"{s[0]} - {s[1]}" for s in students]
        self.payment_student_combo["values"] = student_list
        self.payment_student_combo.all_values = student_list
    
    def on_payment_group_change(self, event=None):
        """تحديث قائمة الطلاب عند تغيير المجموعة لإظهار طلاب المجموعة فقط"""
        group_sel = self.payment_group_combo.get()
        group_id = self.get_id_from_combo(group_sel)
        
        if group_id:
            # جلب طلاب المجموعة المحددة فقط
            students = self.db.fetch_all("""
                SELECT s.id, s.name 
                FROM students s
                JOIN student_groups sg ON s.id = sg.student_id
                WHERE sg.group_id = ?
                ORDER BY s.name
            """, (group_id,))
        else:
            # إذا لم يتم اختيار مجموعة، أظهر جميع الطلاب
            students = self.db.fetch_all("SELECT id, name FROM students ORDER BY name")
        
        student_list = [f"{s[0]} - {s[1]}" for s in students]
        self.payment_student_combo["values"] = student_list
        self.payment_student_combo.all_values = student_list
        
        # مسح الاختيار الحالي للطالب
        self.payment_student_combo.set('')
    
    def add_payment(self):
        """تسجيل دفعة"""
        student_sel = self.payment_student_combo.get()
        group_sel = self.payment_group_combo.get()
        
        if not student_sel or not group_sel:
            messagebox.showerror("خطأ", "يرجى اختيار الطالب والمجموعة")
            return
        
        student_id = self.get_id_from_combo(student_sel)
        group_id = self.get_id_from_combo(group_sel)
        
        if not student_id or not group_id:
            messagebox.showerror("خطأ", "يرجى اختيار طالب ومجموعة صحيحة من القائمة")
            return
        
        try:
            amount = float(self.payment_amount.get().strip())
        except ValueError:
            messagebox.showerror("خطأ", "المبلغ يجب أن يكون رقماً")
            return
        
        payment_date = self.payment_date.get().strip()
        notes = self.payment_notes.get().strip()
        
        try:
            self.db.execute_query(
                "INSERT INTO payments (student_id, group_id, amount, payment_date, notes) VALUES (?, ?, ?, ?, ?)",
                (student_id, group_id, amount, payment_date, notes)
            )
            
            # حذف إشعارات الدفع الخاصة بهذا الطالب والمجموعة
            self.db.execute_query("""
                DELETE FROM notifications 
                WHERE student_id=? AND group_id=? AND type='payment'
            """, (student_id, group_id))
            
            # تحديث عرض الإشعارات إذا كان التبويب موجوداً
            if hasattr(self, 'notifications_tree'):
                self.load_notifications()
            
            messagebox.showinfo("نجح", "تم تسجيل الدفعة وحذف الإشعار بنجاح")
            self.payment_amount.delete(0, tk.END)
            self.payment_notes.delete(0, tk.END)
            self.load_payments()
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل تسجيل الدفعة: {str(e)}")
    
    def delete_payment(self):
        """حذف دفعة"""
        selected = self.payments_tree.selection()
        if not selected:
            messagebox.showerror("خطأ", "يرجى اختيار دفعة للحذف")
            return
        
        # ID في المكان الأخير (index 5)
        payment_id = self.payments_tree.item(selected[0])["values"][5]
        
        if messagebox.askyesno("تأكيد", "هل تريد حذف هذه الدفعة؟"):
            try:
                self.db.execute_query("DELETE FROM payments WHERE id=?", (payment_id,))
                messagebox.showinfo("نجح", "تم حذف الدفعة")
                self.load_payments()
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل الحذف: {str(e)}")
    
    def load_payments(self):
        """تحميل قائمة الدفعات مع التلوين المتناوب"""
        for item in self.payments_tree.get_children():
            self.payments_tree.delete(item)
        
        query = """
            SELECT p.id, s.name, g.name, p.amount, p.payment_date, p.notes
            FROM payments p
            JOIN students s ON p.student_id = s.id
            JOIN groups g ON p.group_id = g.id
            ORDER BY p.payment_date DESC
        """
        payments = self.db.fetch_all(query)
        for idx, payment in enumerate(payments):
            # الترتيب RTL: ملاحظات، التاريخ، المبلغ، المجموعة، الطالب، ID
            values = [payment[5] or "", payment[4], payment[3], payment[2], payment[1], payment[0]]
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.payments_tree.insert("", tk.END, values=values, tags=(tag,))
    
    # ========== وظائف الحضور ==========
    
    def refresh_attendance_combos(self):
        """تحديث قوائم الطلبة والمجموعات للحضور"""
        # المجموعات
        groups = self.db.fetch_all("SELECT id, name FROM groups")
        group_list = [f"{g[0]} - {g[1]}" for g in groups]
        self.attendance_group_combo["values"] = group_list
        self.attendance_group_combo.all_values = group_list
        
        # الطلبة - جميع الطلاب مبدئياً
        students = self.db.fetch_all("SELECT id, name FROM students")
        student_list = [f"{s[0]} - {s[1]}" for s in students]
        self.attendance_student_combo["values"] = student_list
        self.attendance_student_combo.all_values = student_list
    
    def on_attendance_group_change(self, event=None):
        """تحديث قائمة الطلاب عند تغيير المجموعة لإظهار طلاب المجموعة فقط"""
        group_sel = self.attendance_group_combo.get()
        group_id = self.get_id_from_combo(group_sel)
        
        if group_id:
            # جلب طلاب المجموعة المحددة فقط
            students = self.db.fetch_all("""
                SELECT s.id, s.name 
                FROM students s
                JOIN student_groups sg ON s.id = sg.student_id
                WHERE sg.group_id = ?
                ORDER BY s.name
            """, (group_id,))
        else:
            # إذا لم يتم اختيار مجموعة، أظهر جميع الطلاب
            students = self.db.fetch_all("SELECT id, name FROM students ORDER BY name")
        
        student_list = [f"{s[0]} - {s[1]}" for s in students]
        self.attendance_student_combo["values"] = student_list
        self.attendance_student_combo.all_values = student_list
        
        # مسح الاختيار الحالي للطالب
        self.attendance_student_combo.set('')
    
    def add_attendance(self):
        """تسجيل حضور/غياب"""
        student_sel = self.attendance_student_combo.get()
        group_sel = self.attendance_group_combo.get()
        
        if not student_sel or not group_sel:
            messagebox.showerror("خطأ", "يرجى اختيار الطالب والمجموعة")
            return
        
        student_id = self.get_id_from_combo(student_sel)
        group_id = self.get_id_from_combo(group_sel)
        
        if not student_id or not group_id:
            messagebox.showerror("خطأ", "يرجى اختيار طالب ومجموعة صحيحة من القائمة")
            return
        status = self.attendance_status.get()
        attendance_date = self.attendance_date.get().strip()
        notes = self.attendance_notes.get().strip()
        
        try:
            self.db.execute_query(
                """INSERT OR REPLACE INTO attendance 
                (student_id, group_id, attendance_date, status, notes) 
                VALUES (?, ?, ?, ?, ?)""",
                (student_id, group_id, attendance_date, status, notes)
            )
            
            # فحص عدد الحضور وإنشاء إشعار عند الوصول لـ 4 حصص
            if status == 'حاضر':
                self.check_attendance_milestone(student_id, group_id)
            
            messagebox.showinfo("نجح", "تم تسجيل الحضور بنجاح")
            self.attendance_notes.delete(0, tk.END)
            self.load_attendance()
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل تسجيل الحضور: {str(e)}")
    
    def check_attendance_milestone(self, student_id, group_id):
        """فحص عدد الحضور وإنشاء إشعار عند الوصول لعدد محدد من الحصص"""
        # التحقق من تفعيل الميزة
        enabled = self.db.fetch_one(
            "SELECT setting_value FROM notification_settings WHERE setting_key='attendance_milestone_enabled'"
        )
        
        if not enabled or enabled[0] != '1':
            return
        
        # جلب عدد الحصص المطلوب للإشعار
        milestone_setting = self.db.fetch_one(
            "SELECT setting_value FROM notification_settings WHERE setting_key='attendance_milestone_count'"
        )
        milestone_count = int(milestone_setting[0]) if milestone_setting else 4
        
        # حساب عدد الحضور الكلي للطالب في هذه المجموعة
        attendance_count = self.db.fetch_one("""
            SELECT COUNT(*) 
            FROM attendance 
            WHERE student_id=? AND group_id=? AND status='حاضر'
        """, (student_id, group_id))
        
        if not attendance_count:
            return
        
        total_attendance = attendance_count[0]
        
        # إذا وصل عدد الحضور إلى العدد المطلوب أو مضاعفاته
        if total_attendance > 0 and total_attendance % milestone_count == 0:
            # جلب معلومات الطالب والمجموعة
            student = self.db.fetch_one("SELECT name FROM students WHERE id=?", (student_id,))
            group = self.db.fetch_one("SELECT name FROM groups WHERE id=?", (group_id,))
            
            if student and group:
                student_name = student[0]
                group_name = group[0]
                
                # التحقق من عدم وجود إشعار مماثل لنفس العدد
                existing = self.db.fetch_one("""
                    SELECT id FROM notifications 
                    WHERE student_id=? AND group_id=? AND type='attendance_milestone'
                    AND message LIKE ?
                """, (student_id, group_id, f"%{total_attendance} حصة%"))
                
                if not existing:
                    # إنشاء إشعار جديد
                    title = f"إنجاز حضور - {group_name}"
                    message = f"تهانينا! الطالب {student_name} أكمل {total_attendance} حصة في مجموعة {group_name}"
                    
                    self.db.execute_query("""
                        INSERT INTO notifications 
                        (student_id, group_id, type, title, message, priority)
                        VALUES (?, ?, 'attendance_milestone', ?, ?, 'normal')
                    """, (student_id, group_id, title, message))
                    
                    # تحديث عرض الإشعارات إذا كان التبويب موجوداً
                    if hasattr(self, 'notifications_tree'):
                        self.load_notifications()
    
    def delete_attendance(self):
        """حذف تسجيل حضور"""
        selected = self.attendance_tree.selection()
        if not selected:
            messagebox.showerror("خطأ", "يرجى اختيار تسجيل للحذف")
            return
        
        # ID في المكان الأخير (index 5)
        attendance_id = self.attendance_tree.item(selected[0])["values"][5]
        
        if messagebox.askyesno("تأكيد", "هل تريد حذف هذا التسجيل؟"):
            try:
                self.db.execute_query("DELETE FROM attendance WHERE id=?", (attendance_id,))
                messagebox.showinfo("نجح", "تم حذف التسجيل")
                self.load_attendance()
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل الحذف: {str(e)}")
    
    def load_attendance(self):
        """تحميل قائمة الحضور مع التلوين المتناوب"""
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        query = """
            SELECT a.id, s.name, g.name, a.status, a.attendance_date, a.notes
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            JOIN groups g ON a.group_id = g.id
            ORDER BY a.attendance_date DESC
        """
        attendance_records = self.db.fetch_all(query)
        for idx, record in enumerate(attendance_records):
            # الترتيب RTL: ملاحظات، التاريخ، الحالة، المجموعة، الطالب، ID
            values = [record[5] or "", record[4], record[3], record[2], record[1], record[0]]
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.attendance_tree.insert("", tk.END, values=values, tags=(tag,))
    
    # ========== التقارير ==========
    
    def show_students_report(self):
        """عرض تقرير الطلبة"""
        self.report_text.delete("1.0", tk.END)
        
        report = "=" * 60 + "\n"
        report += "تقرير الطلبة\n"
        report += "=" * 60 + "\n\n"
        
        # إحصائيات عامة
        total = self.db.fetch_one("SELECT COUNT(*) FROM students")[0]
        report += f"إجمالي عدد الطلبة: {total}\n\n"
        
        # قائمة الطلبة مع مجموعاتهم
        query = """
            SELECT s.name, s.phone, 
                   GROUP_CONCAT(g.name, ', ') as groups,
                   COUNT(DISTINCT sg.group_id) as group_count
            FROM students s
            LEFT JOIN student_groups sg ON s.id = sg.student_id
            LEFT JOIN groups g ON sg.group_id = g.id
            GROUP BY s.id
        """
        students = self.db.fetch_all(query)
        
        report += "-" * 60 + "\n"
        for student in students:
            name, phone, groups, count = student
            groups = groups if groups else "لا يوجد"
            report += f"الاسم: {name}\n"
            report += f"الهاتف: {phone}\n"
            report += f"عدد المجموعات: {count}\n"
            report += f"المجموعات: {groups}\n"
            report += "-" * 60 + "\n"
        
        self.report_text.insert("1.0", report)
    
    def show_groups_report(self):
        """عرض تقرير المجموعات"""
        self.report_text.delete("1.0", tk.END)
        
        report = "=" * 60 + "\n"
        report += "تقرير المجموعات\n"
        report += "=" * 60 + "\n\n"
        
        # إحصائيات عامة
        total = self.db.fetch_one("SELECT COUNT(*) FROM groups")[0]
        report += f"إجمالي عدد المجموعات: {total}\n\n"
        
        # تفاصيل المجموعات
        query = """
            SELECT g.name, g.subject, g.teacher, g.fee,
                   COUNT(DISTINCT sg.student_id) as student_count
            FROM groups g
            LEFT JOIN student_groups sg ON g.id = sg.group_id
            GROUP BY g.id
        """
        groups = self.db.fetch_all(query)
        
        report += "-" * 60 + "\n"
        for group in groups:
            name, subject, teacher, fee, count = group
            report += f"المجموعة: {name}\n"
            report += f"المادة: {subject}\n"
            report += f"المعلم: {teacher}\n"
            report += f"الرسوم: {fee}\n"
            report += f"عدد الطلبة: {count}\n"
            report += "-" * 60 + "\n"
        
        self.report_text.insert("1.0", report)
    
    def show_payments_report(self):
        """عرض تقرير الدفعات"""
        self.report_text.delete("1.0", tk.END)
        
        report = "=" * 60 + "\n"
        report += "تقرير الدفعات\n"
        report += "=" * 60 + "\n\n"
        
        # إجمالي الدفعات
        total = self.db.fetch_one("SELECT COALESCE(SUM(amount), 0) FROM payments")[0]
        count = self.db.fetch_one("SELECT COUNT(*) FROM payments")[0]
        
        report += f"إجمالي المبالغ المحصلة: {total} \n"
        report += f"عدد الدفعات: {count}\n\n"
        
        # الدفعات حسب المجموعات
        report += "الدفعات حسب المجموعات:\n"
        report += "-" * 60 + "\n"
        
        query = """
            SELECT g.name, COUNT(*) as payment_count, SUM(p.amount) as total_amount
            FROM payments p
            JOIN groups g ON p.group_id = g.id
            GROUP BY g.id
        """
        group_payments = self.db.fetch_all(query)
        
        for gp in group_payments:
            group_name, payment_count, total_amount = gp
            report += f"المجموعة: {group_name}\n"
            report += f"عدد الدفعات: {payment_count}\n"
            report += f"المبلغ الإجمالي: {total_amount}\n"
            report += "-" * 60 + "\n"
        
        self.report_text.insert("1.0", report)
    
    def show_attendance_report(self):
        """عرض تقرير الحضور"""
        self.report_text.delete("1.0", tk.END)
        
        report = "=" * 60 + "\n"
        report += "تقرير الحضور والغياب\n"
        report += "=" * 60 + "\n\n"
        
        # إحصائيات عامة
        total = self.db.fetch_one("SELECT COUNT(*) FROM attendance")[0]
        present = self.db.fetch_one("SELECT COUNT(*) FROM attendance WHERE status='حاضر'")[0]
        absent = self.db.fetch_one("SELECT COUNT(*) FROM attendance WHERE status='غائب'")[0]
        excused = self.db.fetch_one("SELECT COUNT(*) FROM attendance WHERE status='غياب بعذر'")[0]
        
        report += f"إجمالي السجلات: {total}\n"
        report += f"الحضور: {present}\n"
        report += f"الغياب: {absent}\n"
        report += f"الغياب بعذر: {excused}\n\n"
        
        # نسب الحضور
        if total > 0:
            present_pct = (present / total) * 100
            report += f"نسبة الحضور: {present_pct:.2f}%\n\n"
        
        # الحضور حسب الطلبة
        report += "الحضور حسب الطلبة:\n"
        report += "-" * 60 + "\n"
        
        query = """
            SELECT s.name,
                   SUM(CASE WHEN a.status='حاضر' THEN 1 ELSE 0 END) as present_count,
                   SUM(CASE WHEN a.status='غائب' THEN 1 ELSE 0 END) as absent_count,
                   COUNT(*) as total_count
            FROM students s
            LEFT JOIN attendance a ON s.id = a.student_id
            GROUP BY s.id
            HAVING total_count > 0
        """
        student_attendance = self.db.fetch_all(query)
        
        for sa in student_attendance:
            name, present_c, absent_c, total_c = sa
            attendance_rate = (present_c / total_c * 100) if total_c > 0 else 0
            report += f"الطالب: {name}\n"
            report += f"الحضور: {present_c} | الغياب: {absent_c} | المجموع: {total_c}\n"
            report += f"نسبة الحضور: {attendance_rate:.2f}%\n"
            report += "-" * 60 + "\n"
        
        self.report_text.insert("1.0", report)
    
    def show_about(self):
        """عرض معلومات عن البرنامج"""
        messagebox.showinfo(
            "عن البرنامج",
            "برنامج إدارة الطلبة والمجموعات\n\n"
            "نسخة 2.2\n\n"
            "برنامج سهل وبسيط لإدارة الطلبة والمجموعات الدراسية\n"
            "يدعم: التسجيل، الدفعات، الحضور والغياب، الإشعارات، والتقارير\n\n"
            "✨ جديد: إشعارات تلقائية عند إكمال الطالب لعدد محدد من الحصص\n\n"
            "مبني بـ: Python + Tkinter + SQLite"
        )
    
    # ========== الإشعارات ==========
    
    def load_notifications(self):
        """تحميل قائمة الإشعارات"""
        for item in self.notifications_tree.get_children():
            self.notifications_tree.delete(item)
        
        query = """
            SELECT n.id, n.is_read, n.priority, n.title, n.message, s.name, 
                   datetime(n.created_at, 'localtime') as created_at
            FROM notifications n
            JOIN students s ON n.student_id = s.id
            ORDER BY n.is_read ASC, n.created_at DESC
        """
        notifications = self.db.fetch_all(query)
        
        unread_count = 0
        for notif in notifications:
            n_id, is_read, priority, title, message, student, created = notif
            status = "✅ مقروء" if is_read else "🔴 جديد"
            
            if not is_read:
                unread_count += 1
            
            # تحديد التلوين
            if not is_read:
                tag = 'unread'
            elif priority == 'high':
                tag = 'high'
            elif is_read:
                tag = 'read'
            else:
                tag = 'normal'
            
            priority_text = "🔴 عالية" if priority == 'high' else "⚪ عادية"
            created_date = created[:16] if created else ""
            
            # الترتيب RTL: التاريخ، الطالب، الرسالة، العنوان، الأولوية، الحالة، ID
            self.notifications_tree.insert("", tk.END, 
                                          values=(created_date, student,
                                                 message[:50] + "..." if len(message) > 50 else message,
                                                 title, priority_text, status, n_id),
                                          tags=(tag,))
        
        # تحديث العدادات
        self.unread_count_label.config(text=str(unread_count))
        self.total_notif_label.config(text=str(len(notifications)))
    
    def check_notifications_on_startup(self):
        """فحص الإشعارات عند بدء التشغيل"""
        # جلب الإعدادات
        show_on_startup = self.db.fetch_one(
            "SELECT setting_value FROM notification_settings WHERE setting_key='show_notifications_on_startup'"
        )
        
        if show_on_startup and show_on_startup[0] == '1':
            # تنظيف الإشعارات القديمة للطلاب الذين دفعوا بالفعل
            self.cleanup_stale_payment_notifications()
            
            # توليد إشعارات الدفعات
            self.generate_payment_notifications()
            
            # عرض الإشعارات غير المقروءة
            unread = self.db.fetch_one(
                "SELECT COUNT(*) FROM notifications WHERE is_read=0"
            )[0]
            
            if unread > 0:
                response = messagebox.askyesno(
                    "إشعارات جديدة",
                    f"لديك {unread} إشعار جديد!\n\nهل تريد عرض الإشعارات الآن؟",
                    icon='info'
                )
                if response:
                    # الانتقال لتبويب الإشعارات
                    self.show_notifications_page()
    
    def cleanup_stale_payment_notifications(self):
        """حذف إشعارات الدفع القديمة للطلاب الذين دفعوا بالفعل"""
        # جلب فترة التذكير
        reminder_days = self.db.fetch_one(
            "SELECT setting_value FROM notification_settings WHERE setting_key='payment_reminder_days'"
        )
        days = int(reminder_days[0]) if reminder_days else 7
        
        # حذف إشعارات الدفع للطلاب الذين دفعوا خلال الفترة المحددة
        cutoff_date = (date.today() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        # حذف الإشعارات القديمة التي لم تعد صالحة (الطالب دفع بالفعل)
        self.db.execute_query("""
            DELETE FROM notifications 
            WHERE type='payment' AND id IN (
                SELECT n.id FROM notifications n
                WHERE n.type='payment'
                AND EXISTS (
                    SELECT 1 FROM payments p
                    WHERE p.student_id = n.student_id 
                    AND p.group_id = n.group_id
                    AND p.payment_date >= ?
                )
            )
        """, (cutoff_date,))
    
    def generate_payment_notifications(self):
        """توليد إشعارات الدفعات المتأخرة"""
        # جلب الإعدادات
        enabled = self.db.fetch_one(
            "SELECT setting_value FROM notification_settings WHERE setting_key='payment_alert_enabled'"
        )
        
        if not enabled or enabled[0] != '1':
            return
        
        reminder_days = self.db.fetch_one(
            "SELECT setting_value FROM notification_settings WHERE setting_key='payment_reminder_days'"
        )
        days = int(reminder_days[0]) if reminder_days else 7
        
        # البحث عن الطلبة الذين لم يدفعوا خلال الفترة المحددة
        cutoff_date = (date.today() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        query = """
            SELECT DISTINCT s.id, s.name, g.id, g.name, g.fee
            FROM student_groups sg
            JOIN students s ON sg.student_id = s.id
            JOIN groups g ON sg.group_id = g.id
            WHERE NOT EXISTS (
                SELECT 1 FROM payments p
                WHERE p.student_id = s.id 
                AND p.group_id = g.id
                AND p.payment_date >= ?
            )
        """
        
        overdue_students = self.db.fetch_all(query, (cutoff_date,))
        
        for student in overdue_students:
            student_id, student_name, group_id, group_name, fee = student
            
            # تحقق إذا كان الإشعار موجود مسبقاً
            existing = self.db.fetch_one("""
                SELECT id FROM notifications 
                WHERE student_id=? AND group_id=? AND type='payment' AND is_read=0
            """, (student_id, group_id))
            
            if not existing:
                # إنشاء إشعار جديد
                title = f"تذكير دفعة - {group_name}"
                message = f"الطالب {student_name} لم يدفع رسوم {group_name} ({fee} ج.م) منذ أكثر من {days} يوم"
                
                self.db.execute_query("""
                    INSERT INTO notifications 
                    (student_id, group_id, type, title, message, priority)
                    VALUES (?, ?, 'payment', ?, ?, 'high')
                """, (student_id, group_id, title, message))
        
        # تحديث عرض الإشعارات
        if hasattr(self, 'notifications_tree'):
            self.load_notifications()
    
    def refresh_notifications(self):
        """تحديث الإشعارات"""
        self.generate_payment_notifications()
        self.load_notifications()
        messagebox.showinfo("تم التحديث", "تم تحديث الإشعارات بنجاح!")
    
    def mark_all_read(self):
        """تعليم جميع الإشعارات كمقروءة"""
        self.db.execute_query("UPDATE notifications SET is_read=1")
        self.load_notifications()
        messagebox.showinfo("تم", "تم تعليم جميع الإشعارات كمقروءة")
    
    def view_notification_details(self, event):
        """عرض تفاصيل الإشعار"""
        selected = self.notifications_tree.selection()
        if not selected:
            return
        
        # ID في المكان الأخير (index 6)
        notif_id = self.notifications_tree.item(selected[0])["values"][6]
        
        # جلب تفاصيل الإشعار
        notif = self.db.fetch_one("""
            SELECT n.*, s.name as student_name, g.name as group_name
            FROM notifications n
            JOIN students s ON n.student_id = s.id
            LEFT JOIN groups g ON n.group_id = g.id
            WHERE n.id=?
        """, (notif_id,))
        
        if not notif:
            return
        
        # تعليم كمقروء
        self.db.execute_query("UPDATE notifications SET is_read=1 WHERE id=?", (notif_id,))
        
        # نافذة التفاصيل
        details_window = tk.Toplevel(self.root)
        details_window.title("تفاصيل الإشعار")
        details_window.geometry("600x400")
        details_window.configure(bg=self.colors['bg'])
        details_window.transient(self.root)
        details_window.grab_set()
        
        container = ttk.Frame(details_window)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header حسب الأولوية
        header_color = self.colors['danger'] if notif[7] == 'high' else self.colors['primary']
        header = tk.Frame(container, bg=header_color, height=80)
        header.pack(fill=tk.X, pady=(0, 20))
        header.pack_propagate(False)
        
        icon = "⚠️" if notif[7] == 'high' else "🔔"
        tk.Label(header, text=icon, bg=header_color, 
                font=('Arial', 32)).pack(side=tk.RIGHT, padx=20)
        
        info_frame = tk.Frame(header, bg=header_color)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        tk.Label(info_frame, text=notif[4], bg=header_color, 
                fg='white', font=('Arial', 14, 'bold')).pack(anchor=tk.E)
        tk.Label(info_frame, text=f"الطالب: {notif[9]}", bg=header_color, 
                fg='white', font=('Arial', 10)).pack(anchor=tk.E)
        
        # المحتوى
        content_card = tk.Frame(container, bg=self.colors['card'], relief='raised', bd=2)
        content_card.pack(fill=tk.BOTH, expand=True)
        
        content_inner = tk.Frame(content_card, bg=self.colors['card'])
        content_inner.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        tk.Label(content_inner, text="📝 الرسالة", 
                bg=self.colors['card'], font=('Arial', 12, 'bold')).pack(anchor=tk.E, pady=(0, 10))
        
        message_text = scrolledtext.ScrolledText(content_inner, height=8, font=('Arial', 11), wrap=tk.WORD)
        message_text.pack(fill=tk.BOTH, expand=True)
        message_text.insert(tk.END, notif[5])
        message_text.config(state=tk.DISABLED)
        
        # معلومات إضافية
        info_text = f"\n📅 تاريخ الإشعار: {notif[8][:16] if notif[8] else 'غير محدد'}"
        if notif[10]:
            info_text += f"\n📚 المجموعة: {notif[10]}"
        
        tk.Label(content_inner, text=info_text, bg=self.colors['card'], 
                font=('Arial', 9), justify=tk.RIGHT).pack(anchor=tk.E, pady=(10, 0))
        
        # أزرار
        btn_frame = tk.Frame(container)
        btn_frame.pack(pady=(15, 0))
        
        # زر تم السداد - يحذف الإشعار بدلاً من تعليمه كمقروء فقط
        tk.Button(btn_frame, text="💰 تم السداد", bg=self.colors['success'], 
                 fg='white', font=('Arial', 10, 'bold'), padx=20, pady=8,
                 border=0, cursor='hand2',
                 command=lambda: self.mark_notification_as_paid(notif_id, details_window)).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(btn_frame, text="حذف الإشعار", bg=self.colors['danger'], 
                 fg='white', font=('Arial', 10, 'bold'), padx=20, pady=8,
                 border=0, cursor='hand2',
                 command=lambda: self.delete_notification(notif_id, details_window)).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(btn_frame, text="إغلاق", bg=self.colors['text_light'], 
                 fg='white', font=('Arial', 10, 'bold'), padx=30, pady=8,
                 border=0, cursor='hand2', 
                 command=details_window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # تحديث القائمة
        self.load_notifications()
    
    def delete_notification(self, notif_id, window):
        """حذف إشعار"""
        self.db.execute_query("DELETE FROM notifications WHERE id=?", (notif_id,))
        window.destroy()
        self.load_notifications()
        messagebox.showinfo("تم الحذف", "تم حذف الإشعار بنجاح")
    
    def mark_notification_as_paid(self, notif_id, window):
        """تعليم الإشعار كمدفوع - يحذف الإشعار بالكامل بدلاً من تعليمه كمقروء فقط"""
        self.db.execute_query("DELETE FROM notifications WHERE id=?", (notif_id,))
        window.destroy()
        self.load_notifications()
        messagebox.showinfo("تم السداد", "تم تسجيل السداد وحذف الإشعار بنجاح")
    
    def show_notification_settings(self):
        """عرض نافذة إعدادات الإشعارات"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ إعدادات الإشعارات")
        settings_window.geometry("550x500")
        settings_window.configure(bg=self.colors['bg'])
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        container = ttk.Frame(settings_window)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header = tk.Frame(container, bg=self.colors['primary'])
        header.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(header, text="⚙️ إعدادات الإشعارات", 
                bg=self.colors['primary'], fg='white',
                font=('Arial', 14, 'bold')).pack(pady=15)
        
        # محتوى الإعدادات
        content_card = tk.Frame(container, bg=self.colors['card'], relief='raised', bd=2)
        content_card.pack(fill=tk.BOTH, expand=True)
        
        content_inner = tk.Frame(content_card, bg=self.colors['card'])
        content_inner.pack(padx=30, pady=20, fill=tk.BOTH)
        
        # جلب الإعدادات الحالية
        current_settings = {}
        for key in ['payment_reminder_days', 'show_notifications_on_startup', 'payment_alert_enabled', 
                    'attendance_milestone_enabled', 'attendance_milestone_count']:
            val = self.db.fetch_one(
                "SELECT setting_value FROM notification_settings WHERE setting_key=?", (key,)
            )
            current_settings[key] = val[0] if val else '0'
        
        # إعداد 1: عرض عند التشغيل
        tk.Label(content_inner, text="🔔 الإشعارات عند التشغيل", 
                bg=self.colors['card'], font=('Arial', 11, 'bold')).pack(anchor=tk.E, pady=(10, 5))
        
        show_startup_var = tk.BooleanVar(value=current_settings['show_notifications_on_startup'] == '1')
        tk.Checkbutton(content_inner, text="عرض الإشعارات عند فتح البرنامج", 
                      variable=show_startup_var, bg=self.colors['card'],
                      font=('Arial', 10)).pack(anchor=tk.E, padx=20)
        
        # إعداد 2: تنبيهات الدفعات
        tk.Label(content_inner, text="💰 تنبيهات الدفعات", 
                bg=self.colors['card'], font=('Arial', 11, 'bold')).pack(anchor=tk.E, pady=(20, 5))
        
        payment_enabled_var = tk.BooleanVar(value=current_settings['payment_alert_enabled'] == '1')
        tk.Checkbutton(content_inner, text="تفعيل تنبيهات الدفعات المتأخرة", 
                      variable=payment_enabled_var, bg=self.colors['card'],
                      font=('Arial', 10)).pack(anchor=tk.E, padx=20)
        
        # إعداد 3: مدة التذكير
        days_frame = tk.Frame(content_inner, bg=self.colors['card'])
        days_frame.pack(anchor=tk.E, padx=20, pady=(10, 0))
        
        tk.Label(days_frame, text="التذكير بعد:", 
                bg=self.colors['card'], font=('Arial', 10)).pack(side=tk.RIGHT, padx=5)
        
        days_var = tk.StringVar(value=current_settings['payment_reminder_days'])
        days_spinbox = ttk.Spinbox(days_frame, from_=1, to=90, textvariable=days_var,
                                   width=10, justify='right')
        days_spinbox.pack(side=tk.RIGHT, padx=5)
        
        tk.Label(days_frame, text="يوم من آخر دفعة", 
                bg=self.colors['card'], font=('Arial', 10)).pack(side=tk.RIGHT, padx=5)
        
        # إعداد 4: تنبيهات إنجاز الحضور
        tk.Label(content_inner, text="✅ تنبيهات إنجاز الحضور", 
                bg=self.colors['card'], font=('Arial', 11, 'bold')).pack(anchor=tk.E, pady=(20, 5))
        
        attendance_enabled_var = tk.BooleanVar(value=current_settings.get('attendance_milestone_enabled', '1') == '1')
        tk.Checkbutton(content_inner, text="تفعيل إشعار عند إكمال عدد محدد من الحصص", 
                      variable=attendance_enabled_var, bg=self.colors['card'],
                      font=('Arial', 10)).pack(anchor=tk.E, padx=20)
        
        # إعداد 5: عدد الحصص للإشعار
        milestone_frame = tk.Frame(content_inner, bg=self.colors['card'])
        milestone_frame.pack(anchor=tk.E, padx=20, pady=(10, 0))
        
        tk.Label(milestone_frame, text="إرسال إشعار كل:", 
                bg=self.colors['card'], font=('Arial', 10)).pack(side=tk.RIGHT, padx=5)
        
        milestone_var = tk.StringVar(value=current_settings.get('attendance_milestone_count', '4'))
        milestone_spinbox = ttk.Spinbox(milestone_frame, from_=1, to=20, textvariable=milestone_var,
                                       width=10, justify='right')
        milestone_spinbox.pack(side=tk.RIGHT, padx=5)
        
        tk.Label(milestone_frame, text="حصة حضور", 
                bg=self.colors['card'], font=('Arial', 10)).pack(side=tk.RIGHT, padx=5)
        
        # معلومات إضافية
        info_frame = tk.Frame(content_inner, bg='#E7F3FF', relief='solid', bd=1)
        info_frame.pack(fill=tk.X, pady=(30, 0))
        
        info_text = """
ℹ️ معلومات مهمة:

• سيتم فحص الدفعات المتأخرة تلقائياً
• سيتم إنشاء إشعار تلقائي عند إكمال الطالب لعدد الحصص المحدد
• ستظهر جميع الإشعارات في تبويب الإشعارات
• يمكنك تخصيص المدة الزمنية للتذكير وعدد الحصص
• الإشعارات ذات الأولوية العالية ستظهر بلون أحمر
        """
        
        tk.Label(info_frame, text=info_text, bg='#E7F3FF', 
                font=('Arial', 9), justify=tk.RIGHT).pack(padx=15, pady=10)
        
        # أزرار الحفظ والإلغاء
        btn_frame = tk.Frame(container)
        btn_frame.pack(pady=(15, 0))
        
        def save_settings():
            # تأكيد الحفظ
            confirm = messagebox.askyesno(
                "تأكيد الحفظ",
                "هل أنت متأكد من حفظ التغييرات على إعدادات الإشعارات؟",
                icon='question'
            )
            
            if not confirm:
                return
            
            # حفظ الإعدادات
            self.db.execute_query("""
                UPDATE notification_settings SET setting_value=? WHERE setting_key='show_notifications_on_startup'
            """, ('1' if show_startup_var.get() else '0',))
            
            self.db.execute_query("""
                UPDATE notification_settings SET setting_value=? WHERE setting_key='payment_alert_enabled'
            """, ('1' if payment_enabled_var.get() else '0',))
            
            self.db.execute_query("""
                UPDATE notification_settings SET setting_value=? WHERE setting_key='payment_reminder_days'
            """, (days_var.get(),))
            
            self.db.execute_query("""
                UPDATE notification_settings SET setting_value=? WHERE setting_key='attendance_milestone_enabled'
            """, ('1' if attendance_enabled_var.get() else '0',))
            
            self.db.execute_query("""
                UPDATE notification_settings SET setting_value=? WHERE setting_key='attendance_milestone_count'
            """, (milestone_var.get(),))
            
            messagebox.showinfo("تم الحفظ", "تم حفظ الإعدادات بنجاح!")
            settings_window.destroy()
        
        tk.Button(btn_frame, text="💾 حفظ الإعدادات", bg=self.colors['success'], 
                 fg='white', font=('Arial', 10, 'bold'), padx=20, pady=8,
                 border=0, cursor='hand2', command=save_settings).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(btn_frame, text="إلغاء", bg=self.colors['text_light'], 
                 fg='white', font=('Arial', 10, 'bold'), padx=30, pady=8,
                 border=0, cursor='hand2',
                 command=settings_window.destroy).pack(side=tk.RIGHT, padx=5)


def main():
    """نقطة دخول البرنامج"""
    root = tk.Tk()
    app = StudentManagementApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()


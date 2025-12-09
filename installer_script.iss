; Inno Setup Script لإنشاء Installer
; تحتاج لتثبيت Inno Setup من: https://jrsoftware.org/isinfo.php

#define MyAppName "Student Management System"
#define MyAppNameAr "نظام إدارة الطلبة والمجموعات"
#define MyAppVersion "2.1"
#define MyAppPublisher "Your Name"
#define MyAppExeName "StudentManager.exe"

[Setup]
; معلومات التطبيق
AppId={{A1B2C3D4-E5F6-7890-ABCD-1234567890AB}
AppName={#MyAppNameAr}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppNameAr}
AllowNoIcons=yes
; اسم ملف الـ installer
OutputBaseFilename=StudentManager_Setup_v{#MyAppVersion}
OutputDir=installer_output
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; أيقونة الـ installer
SetupIconFile=app_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; الملف التنفيذي الرئيسي
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; ملفات إضافية
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "FEATURES.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "RTL_SUPPORT.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; اختصارات في قائمة Start
Name: "{group}\{#MyAppNameAr}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppNameAr}}"; Filename: "{uninstallexe}"
; اختصار على سطح المكتب
Name: "{autodesktop}\{#MyAppNameAr}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
; اختصار في شريط المهام
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppNameAr}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; تشغيل البرنامج بعد التثبيت
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppNameAr, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// رسالة ترحيب بالعربية
function InitializeSetup(): Boolean;
begin
  Result := True;
  MsgBox('مرحباً بك في برنامج إدارة الطلبة والمجموعات' + #13#10 + 
         'النسخة ' + '{#MyAppVersion}', mbInformation, MB_OK);
end;


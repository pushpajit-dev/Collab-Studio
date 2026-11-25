; =====================================================================
; Collab Studio - Official Inno Setup Installer Script
; Developed by Aivorystudios (https://aivorygen.vercel.app)
; =====================================================================

#define MyAppName "Collab Studio"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "Aivorystudios"
#define MyAppURL "https://aivorygen.vercel.app"
#define MyAppExeName "CollabStudio.exe"
#define MySetupExeName "CollabStudioSetup.exe"

[Setup]
AppId={{5E28B93D-938C-4F7A-928A-5D19CA16F082}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\Collab Studio
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=dist
OutputBaseFilename=CollabStudio-Installer
SetupIconFile=logo.ico
UninstallDisplayIcon={app}\logo.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "setupfirst"; Description: "Run System Diagnostic & Model Manager on first launch"; GroupDescription: "Setup Options:"; Flags: checkedonce

[Files]
; Main Executables
Source: "dist\CollabStudio.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\CollabStudioSetup.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "logo.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

; Core Python & HTML Application Files
Source: "app.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "app.html"; DestDir: "{app}"; Flags: ignoreversion
Source: "doctor.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "clip.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "reframe.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "batch.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "nopick.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "watch.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "hunt.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "chat.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "live.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "translate.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "meme.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "ytstats.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "update.py"; DestDir: "{app}"; Flags: ignoreversion

; Configuration and Templates
Source: "brand.example.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "streamers.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "themes.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "clip_rules.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "version.json"; DestDir: "{app}"; Flags: ignoreversion

; Folders and Assets
Source: "fonts\*"; DestDir: "{app}\fonts"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "sounds\*"; DestDir: "{app}\sounds"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\logo.ico"
Name: "{autoprograms}\{#MyAppName} Setup & Diagnostics"; Filename: "{app}\{#MySetupExeName}"; IconFilename: "{app}\logo.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\logo.ico"
Name: "{autodesktop}\{#MyAppName} Setup"; Filename: "{app}\{#MySetupExeName}"; Tasks: desktopicon; IconFilename: "{app}\logo.ico"

[Run]
; Optional automated isolated venv setup if python is available
Filename: "py.exe"; Parameters: "-3 -m venv ""{app}\venv"""; WorkingDir: "{app}"; Flags: runhidden skipifdoesntexist
; First run launchers
Filename: "{app}\{#MySetupExeName}"; Description: "Launch Collab Studio Setup & System Check (Verify Models & YouTube OAuth)"; Flags: postinstall nowait skipifsilent; Tasks: setupfirst
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Collab Studio immediately"; Flags: postinstall nowait skipifsilent unchecked

[Code]
var
  WipeModels: Boolean;

function InitializeUninstall(): Boolean;
var
  Res: Integer;
begin
  Result := True;
  WipeModels := True;
  Res := MsgBox('Do you also want to permanently delete downloaded AI models (~500MB+ Whisper, YuNet, MediaPipe weights)?' + #13#10 + #13#10 +
                '• Click YES to completely delete all application files and AI models.' + #13#10 +
                '• Click NO to keep downloaded AI models for future reinstallations.' + #13#10 +
                '• Click CANCEL to abort uninstall.', mbConfirmation, MB_YESNOCANCEL);
  if Res = IDCANCEL then
  begin
    Result := False;
    Exit;
  end;
  WipeModels := (Res = IDYES);
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  AppPath: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    AppPath := ExpandConstant('{app}');
    if WipeModels then
    begin
      DelTree(AppPath + '\models', True, True, True);
      DelTree(AppPath + '\venv', True, True, True);
      DelTree(AppPath + '\workspace', True, True, True);
      DelTree(AppPath, True, True, True);
    end
    else
    begin
      DelTree(AppPath + '\venv', True, True, True);
      DelTree(AppPath + '\workspace', True, True, True);
      DelTree(AppPath + '\fonts', True, True, True);
      DelTree(AppPath + '\sounds', True, True, True);
      DelTree(AppPath + '\assets', True, True, True);
      DelTree(AppPath + '\__pycache__', True, True, True);
    end;
  end;
end;

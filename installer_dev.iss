; =====================================================
;  AI Voice Studio - DEVELOPER INSTALLER
;  Same as public but also installs source files.
;  Dev gets extra option to skip model download
;  if they already have their own models cached.
; =====================================================

#define AppName      "AI Voice Studio"
#define AppVersion   "1.0"
#define AppPublisher "domore100"
#define AppURL       "https://github.com/domore100"
#define AppExeName   "AI_Voice_Studio.exe"
#define AppShortName "Local TTS"

[Setup]
AppId={{D4E2A1B3-7F6C-4A8D-9E0B-DEV0000000001}
AppName={#AppName} (Developer)
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
DefaultDirName={autopf}\AI Voice Studio
DefaultGroupName={#AppName}
AllowNoIcons=yes
OutputDir=dev_setup
OutputBaseFilename=AI_Voice_Studio_Dev_Setup
SetupIconFile=logo.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardResizable=no
LicenseFile=LICENSE.txt
MinVersion=10.0
PrivilegesRequired=admin
ExtraDiskSpaceRequired=524288000
UninstallDisplayIcon={app}\logo.ico
UninstallDisplayName={#AppName} Developer Tools

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
; Shortcuts
Name: "desktopicon"; \
    Description: "Create desktop shortcut (named ""Local TTS"")"; \
    GroupDescription: "Shortcuts:"; \
    Flags: checked
Name: "startmenu"; \
    Description: "Add to Start Menu"; \
    GroupDescription: "Shortcuts:"; \
    Flags: checked

; Packages - checked by default
Name: "install_pkgs"; \
    Description: "Install Python dependencies  (pip install ...)"; \
    GroupDescription: "Setup:"; \
    Flags: checked

; Models - two exclusive options, download is default
Name: "download_models"; \
    Description: "Download AI models  (Whisper ~150MB + VCTK ~100MB + XTTS-v2 ~2GB)"; \
    GroupDescription: "AI Models:"; \
    Flags: checked exclusive

Name: "skip_models"; \
    Description: "Skip model download  (I already have models in my cache)"; \
    GroupDescription: "AI Models:"; \
    Flags: unchecked exclusive

[Dirs]
Name: "{app}"
Name: "{app}\source"
Name: "{app}\models\vctk"
Name: "{app}\models\xtts_v2"
Name: "{app}\models\whisper"
Name: "{app}\models\vosk"

[Files]
; Application (same as public)
Source: "dist\AI_Voice_Studio\*"; \
    DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs; \
    Check: DirExists(ExpandConstant('{src}\dist\AI_Voice_Studio'))
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "download_models.py"; DestDir: "{app}"; Flags: ignoreversion

; Source files
Source: "main.py";              DestDir: "{app}\source"; Flags: ignoreversion
Source: "hook_vosk.py";         DestDir: "{app}\source"; Flags: ignoreversion
Source: "download_models.py";   DestDir: "{app}\source"; Flags: ignoreversion
Source: "requirements.txt";     DestDir: "{app}\source"; Flags: ignoreversion
Source: "ai_voice_studio.spec"; DestDir: "{app}\source"; Flags: ignoreversion
Source: "build_manager.py";     DestDir: "{app}\source"; Flags: ignoreversion
Source: "build_manager.spec";   DestDir: "{app}\source"; Flags: ignoreversion
Source: "installer_public.iss"; DestDir: "{app}\source"; Flags: ignoreversion
Source: "installer_dev.iss";    DestDir: "{app}\source"; Flags: ignoreversion
Source: "logo.ico";             DestDir: "{app}\source"; Flags: ignoreversion
Source: "logo.png";             DestDir: "{app}\source"; Flags: ignoreversion; \
    Check: FileExists(ExpandConstant('{src}\logo.png'))

[Icons]
Name: "{group}\{#AppName}"; \
    Filename: "{app}\{#AppExeName}"; \
    IconFilename: "{app}\logo.ico"; Tasks: startmenu
Name: "{group}\Uninstall {#AppName}"; \
    Filename: "{uninstallexe}"; Tasks: startmenu
Name: "{commondesktop}\{#AppShortName}"; \
    Filename: "{app}\{#AppExeName}"; \
    IconFilename: "{app}\logo.ico"; Tasks: desktopicon

[Run]
; Install Python packages
Filename: "py.exe"; \
    Parameters: "-3.10 -m pip install TTS ""torch torchaudio --index-url https://download.pytorch.org/whl/cpu"" openai-whisper vosk pygame SpeechRecognition PyAudio numpy librosa pyinstaller"; \
    StatusMsg: "Installing Python dependencies..."; \
    Flags: runhidden waituntilterminated; \
    Tasks: install_pkgs

; Download models (only if download_models task selected)
Filename: "py.exe"; \
    Parameters: "-3.10 ""{app}\download_models.py"" --whisper"; \
    StatusMsg: "Downloading Whisper model (~150MB)..."; \
    Flags: runhidden waituntilterminated; \
    Tasks: download_models

Filename: "py.exe"; \
    Parameters: "-3.10 ""{app}\download_models.py"" --vctk"; \
    StatusMsg: "Downloading VCTK voices (~100MB)..."; \
    Flags: runhidden waituntilterminated; \
    Tasks: download_models

Filename: "py.exe"; \
    Parameters: "-3.10 ""{app}\download_models.py"" --xtts"; \
    StatusMsg: "Downloading XTTS-v2 voices (~2GB)..."; \
    Flags: runhidden waituntilterminated; \
    Tasks: download_models

; Open source folder on finish
Filename: "{app}\source"; \
    Description: "Open source folder"; \
    Flags: postinstall shellexec skipifsilent nowait

; Launch app
Filename: "{app}\{#AppExeName}"; \
    Description: "Launch {#AppName} now"; \
    Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Messages]
WelcomeLabel1=AI Voice Studio - Developer Install
WelcomeLabel2=Version {#AppVersion} by {#AppPublisher}%n%nInstalls the app + full Python source files and build tools.%n%nRequires Python 3.10.%n%nYou can choose whether to download AI models or skip if you already have them cached from a previous install.%n%nClick Next to continue.
FinishedLabel=Developer install complete!%n%nSource files: {app}\source\%n%nRun BuildManager.exe to rebuild the app or compile installers.

[Code]
function InitializeSetup(): Boolean;
var
  RC: Integer;
begin
  Result := True;
  if not Exec('py.exe', '-3.10 --version', '', SW_HIDE, ewWaitUntilTerminated, RC) or (RC <> 0) then
    if MsgBox('Python 3.10 not detected.' + #13#10 + #13#10 +
              'Download: https://python.org/downloads/release/python-31012/' + #13#10 + #13#10 +
              'Continue anyway?',
              mbConfirmation, MB_YESNO) = IDNO then
      Result := False;
end;

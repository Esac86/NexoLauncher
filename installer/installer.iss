#define MyAppName "Nexo Launcher"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Nexo Launcher"
#define MyAppURL "https://nexoabierto.com"
#define MyAppExeName "Nexo Launcher.exe"
#define MyAppId "{{8F5A4D2E-9B3C-4F1A-A8E7-2D1C3B4A5E6F}"

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DisableDirPage=no
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=..\dist
OutputBaseFilename=NexoLauncher_Setup
SetupIconFile=..\assets\favicon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMADictionarySize=1048576
LZMANumFastBytes=273
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline
WizardStyle=modern
DisableWelcomePage=yes
DisableProgramGroupPage=yes
DisableReadyPage=yes
DisableFinishedPage=no
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Installer
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source: "..\dist\Nexo Launcher.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\Updater.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{userstartmenu}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
  UninstallString: String;
  UninstallExe: String;
begin
  Result := True;
  
  if RegQueryStringValue(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppId}_is1', 
    'UninstallString', UninstallString) then
  begin
    if MsgBox('Nexo Launcher ya está instalado. ¿Desea desinstalar la versión anterior antes de continuar?', 
      mbConfirmation, MB_YESNO) = IDYES then
    begin
      UninstallExe := RemoveQuotes(UninstallString);
      Exec(UninstallExe, '/SILENT', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
      Result := True;
    end
    else
    begin
      Result := False;
    end;
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  
  if CheckForMutexes('NexoLauncherMutex') then
  begin
    if MsgBox('Nexo Launcher está ejecutándose. ¿Desea cerrarlo automáticamente?', 
      mbConfirmation, MB_YESNO) = IDYES then
    begin
      Sleep(2000);
      Result := '';
    end
    else
    begin
      Result := 'Por favor cierre Nexo Launcher antes de continuar con la instalación.';
    end;
  end;
end;
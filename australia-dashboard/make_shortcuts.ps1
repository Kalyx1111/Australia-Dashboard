# Creates the GLOBAL DASHBOARD shortcut on the Desktop and in the Start menu.
# start.bat runs this each time, so the shortcuts always point at the folder the dashboard is running from.
$ErrorActionPreference = 'Stop'
$Root   = Split-Path -Parent $MyInvocation.MyCommand.Path
$Target = Join-Path $Root 'start.bat'
$Icon   = Join-Path $Root 'assets\global-dashboard.ico'
$Name   = 'AUSTRALIA Dashboard'
try {
    $shell  = New-Object -ComObject WScript.Shell
    $places = @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))
    foreach ($dir in $places) {
        if ([string]::IsNullOrEmpty($dir)) { continue }
        $lnk = Join-Path $dir ($Name + '.lnk')
        $s = $shell.CreateShortcut($lnk)
        $s.TargetPath       = $Target
        $s.WorkingDirectory = $Root
        $s.Description      = 'Start the AUSTRALIA Dashboard on this computer (127.0.0.1:8830)'
        if (Test-Path -LiteralPath $Icon) { $s.IconLocation = $Icon + ',0' }
        $s.Save()
        Write-Host ('  [OK] Shortcut ready: ' + $lnk)
    }
} catch {
    Write-Host ('  [NOTE] Shortcut could not be created: ' + $_.Exception.Message)
}
exit 0

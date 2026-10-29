#requires -Version 5.1
[CmdletBinding()]
param(
    [ValidateSet('Menu','Diagnose','Install','Run','Status','Pause','Resume','Uninstall')]
    [string] $Mode = 'Menu',
    [switch] $NoPause
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'CameraPolicy.psm1') -Force
$script:SourceDir = $PSScriptRoot
$script:TaskName = 'A4techCameraPriority'
$programRoot = if ($env:ProgramW6432) { $env:ProgramW6432 } else { $env:ProgramFiles }
$script:InstallDir = Join-Path $programRoot 'A4techCameraPriority'
$script:ConfigPath = Join-Path $script:InstallDir 'config.json'
$script:StatePath = Join-Path $script:InstallDir 'state.json'
$script:StopPath = Join-Path $script:InstallDir 'stop.request'
$script:LogPath = Join-Path $script:InstallDir 'camera-priority.log'
$script:PowerShell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'

function Write-JsonAtomic($Path, $Value) {
    $Value | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath ($Path + '.tmp') -Encoding UTF8
    Move-Item -LiteralPath ($Path + '.tmp') -Destination $Path -Force
}

function Write-Log([string] $Message) {
    if ((Test-Path -LiteralPath $script:LogPath) -and (Get-Item -LiteralPath $script:LogPath).Length -gt 1MB) {
        Move-Item -LiteralPath $script:LogPath -Destination ($script:LogPath + '.1') -Force
    }
    Add-Content -LiteralPath $script:LogPath -Encoding UTF8 `
        -Value ('{0} {1}' -f [DateTimeOffset]::Now.ToString('o'), $Message)
}

function Read-Config {
    $config = Get-Content -LiteralPath $script:ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-CameraConfig $config
    return $config
}

function Read-Owned($Config) {
    if (-not (Test-Path -LiteralPath $script:StatePath)) { return $false }
    $state = Get-Content -LiteralPath $script:StatePath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($state.InternalId -ne $Config.InternalId -or $state.Owned -isnot [bool]) {
        throw 'Invalid recovery state. Use Device Manager to check the laptop camera.'
    }
    return $state.Owned
}

function Save-Owned($Config, [bool] $Owned) {
    Write-JsonAtomic $script:StatePath @{
        InternalId = $Config.InternalId; Owned = $Owned
        Updated = [DateTimeOffset]::Now.ToString('o')
    }
}

function Get-Internal($Config, $Devices) {
    $found = @($Devices | Where-Object { $_.Id -eq $Config.InternalId })
    if ($found.Count -gt 1) { throw 'Ambiguous internal camera ID.' }
    if ($found.Count -eq 1) { return $found[0] }
    return $null
}

function Test-Preferred($Config, $Devices) {
    return @($Devices | Where-Object {
        $_.Class -eq 'Camera' -and $_.Code -eq 0 -and
        $_.Id.StartsWith($Config.PreferredPrefix, [StringComparison]::OrdinalIgnoreCase)
    }).Count -eq 1
}

function Restore-Camera($Config) {
    if (-not (Read-Owned $Config)) { return }
    $device = Get-Internal $Config (Get-CameraInventory)
    if ($null -eq $device) { throw 'Laptop camera absent; recovery state kept. Reconnect/reboot, then Pause again.' }
    if ($device.Code -eq 22) {
        Enable-PnpDevice -InstanceId $Config.InternalId -Confirm:$false -ErrorAction Stop
        Start-Sleep -Milliseconds 700
        $device = Get-Internal $Config (Get-CameraInventory)
    }
    if ($null -eq $device -or $device.Code -ne 0) { throw 'Laptop camera did not become ready. Recovery files retained.' }
    Save-Owned $Config $false
    Write-Log 'RESTORED laptop camera; ownership released.'
}

function Sync-Camera($Config) {
    $devices = Get-CameraInventory
    $ready = Test-Preferred $Config $devices
    if ($ready) {
        Start-Sleep -Milliseconds 1000
        $devices = Get-CameraInventory
        $ready = Test-Preferred $Config $devices
    }
    $internal = Get-Internal $Config $devices
    $code = if ($null -ne $internal) { $internal.Code } else { $null }
    $decision = Get-CameraDecision $code $ready (Read-Owned $Config)
    switch ($decision) {
        'Disable' {
            if (Test-Path -LiteralPath $script:StopPath) { return }
            # Persist before disabling, so abrupt termination still leaves recovery data.
            Save-Owned $Config $true
            Disable-PnpDevice -InstanceId $Config.InternalId -Confirm:$false -ErrorAction Stop
            Start-Sleep -Milliseconds 500
            $after = Get-Internal $Config (Get-CameraInventory)
            if ($null -eq $after -or $after.Code -ne 22) { throw 'Disable not confirmed by PnP; will attempt recovery.' }
            Write-Log 'PREFERRED A4tech healthy in PnP; laptop camera disabled.'
        }
        'Restore' { Restore-Camera $Config }
        'Release' { Save-Owned $Config $false; Write-Log 'Laptop already enabled; ownership released.' }
    }
}

function Get-OurTask {
    return Get-ScheduledTask -TaskName $script:TaskName -TaskPath '\' -ErrorAction SilentlyContinue
}

function Stop-Worker {
    $task = Get-OurTask
    if ($null -ne $task) {
        Disable-ScheduledTask -TaskName $script:TaskName -TaskPath '\' | Out-Null
        Set-Content -LiteralPath $script:StopPath -Value 'stop' -Encoding ASCII
        $until = [DateTime]::UtcNow.AddSeconds(12)
        while ((Get-OurTask).State -eq 'Running' -and [DateTime]::UtcNow -lt $until) { Start-Sleep -Milliseconds 300 }
        if ((Get-OurTask).State -eq 'Running') {
            Stop-ScheduledTask -TaskName $script:TaskName -TaskPath '\'
            Start-Sleep -Milliseconds 800
            if ((Get-OurTask).State -eq 'Running') { throw 'Worker still running; restore deferred.' }
        }
    }
}

function Install-Tool {
    if ((Test-Path -LiteralPath $script:InstallDir) -or $null -ne (Get-OurTask)) {
        throw 'Already installed (or old files exist). Use Status / Uninstall before installing again.'
    }
    $devices = @(Get-CameraInventory)
    $preferred = @($devices | Where-Object {
        $_.Name -eq 'A4tech HD 720P PC Camera' -and $_.Class -eq 'Camera' -and
        $_.Id -match '^USB\\VID_09DA&PID_2697(?:&MI_[0-9A-F]{2})?\\' -and $_.Code -eq 0
    })
    if ($preferred.Count -ne 1) { throw 'Connect one healthy A4tech HD 720P PC Camera (VID 09DA/PID 2697), then retry.' }
    $others = @($devices | Where-Object {
        $_.Id -ne $preferred[0].Id -and $_.Class -eq 'Camera' -and $_.Code -eq 0 -and
        $_.Name -notmatch '(?i)(\bIR\b|infrared|depth|virtual)' -and $_.Id -match '^USB\\'
    })
    if ($others.Count -eq 0) { throw 'No healthy fallback camera found. Enable the laptop camera first.' }
    Write-Host "`nChoose the LAPTOP RGB camera to manage (not IR/Windows Hello):" -ForegroundColor Cyan
    for ($i = 0; $i -lt $others.Count; $i++) {
        Write-Host ('[{0}] {1} -- {2}' -f ($i + 1), $others[$i].Name, $others[$i].Id)
    }
    $choice = 0
    $answer = Read-Host 'Camera number'
    if (-not [int]::TryParse($answer, [ref] $choice) -or $choice -lt 1 -or $choice -gt $others.Count) { throw 'No camera selected. Nothing installed.' }
    $internal = $others[$choice - 1]
    $config = [pscustomobject]@{
        Product = 'A4techCameraPriority'; Version = 1
        PreferredPrefix = Get-PreferredPrefix $preferred[0].Id
        PreferredName = $preferred[0].Name; InternalId = $internal.Id; InternalName = $internal.Name
    }
    Assert-CameraConfig $config
    Write-Host "`nA4tech present and PnP healthy -> DISABLE: $($internal.Name)" -ForegroundColor Yellow
    Write-Host 'A4tech unplugged/not healthy -> restore that laptop camera.'
    Write-Host 'This affects ALL users/apps using that camera, including Hello if it shares that device.'
    Write-Host 'Active calls may stop; apps with a saved device may need reopening.'
    Write-Host 'No guarantee of seamless switching. No microphone/IR/other device will be targeted.'
    Write-Host "Folder: $script:InstallDir; boot task runs as SYSTEM."
    if ((Read-Host 'Type INSTALL to install and start; anything else cancels') -cne 'INSTALL') { Write-Host 'Cancelled. No changes.'; return }
    $registered = $false
    try {
        New-Item -ItemType Directory -Path $script:InstallDir | Out-Null
        $acl = New-Object System.Security.AccessControl.DirectorySecurity
        $acl.SetAccessRuleProtection($true, $false)
        foreach ($entry in @(@('S-1-5-18','FullControl'), @('S-1-5-32-544','FullControl'), @('S-1-5-32-545','ReadAndExecute'))) {
            $sid = New-Object System.Security.Principal.SecurityIdentifier($entry[0])
            $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
                $sid, $entry[1], 'ContainerInherit,ObjectInherit', 'None', 'Allow')
            $acl.AddAccessRule($rule)
        }
        Set-Acl -LiteralPath $script:InstallDir -AclObject $acl
        Write-JsonAtomic $script:ConfigPath $config
        Save-Owned $config $false
        foreach ($file in @('CameraPriority.ps1','CameraPolicy.psm1','CameraPriority.cmd','README.md','VALIDATION.md')) {
            Copy-Item -LiteralPath (Join-Path $script:SourceDir $file) -Destination $script:InstallDir
        }
        $action = New-ScheduledTaskAction -Execute $script:PowerShell -Argument (
            '-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File "{0}" -Mode Run' -f
            (Join-Path $script:InstallDir 'CameraPriority.ps1')) -WorkingDirectory $script:InstallDir
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
            -StartWhenAvailable -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew `
            -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1)
        $principal = New-ScheduledTaskPrincipal -UserId 'S-1-5-18' -LogonType ServiceAccount -RunLevel Highest
        Register-ScheduledTask -TaskName $script:TaskName -TaskPath '\' -Action $action `
            -Trigger (New-ScheduledTaskTrigger -AtStartup) -Settings $settings -Principal $principal `
            -Description 'Prefer A4tech by temporarily disabling only the selected laptop RGB camera.' | Out-Null
        $registered = $true
        Write-Log 'INSTALLED; starting automatic priority worker.'
        Start-ScheduledTask -TaskName $script:TaskName -TaskPath '\'
        Write-Host 'Installed and start requested. Use Status after a few seconds, then test unplug/replug.' -ForegroundColor Green
    } catch {
        $installError = $_
        if ($registered) { Stop-Worker }
        if (Test-Path -LiteralPath $script:ConfigPath) { Restore-Camera $config }
        Write-Warning 'Install failed. Files kept for recovery; use Uninstall after checking Status.'
        throw $installError
    }
}

function Run-Worker {
    if ([IO.Path]::GetFullPath($script:SourceDir).TrimEnd('\') -ne [IO.Path]::GetFullPath($script:InstallDir).TrimEnd('\')) { throw 'Worker must run from its protected installation folder.' }
    if ([Security.Principal.WindowsIdentity]::GetCurrent().User.Value -ne 'S-1-5-18') { throw 'Start the worker through its scheduled task.' }
    $config = Read-Config
    $failed = $false
    try {
        if (Test-Path -LiteralPath $script:StopPath) { return }
        Register-WmiEvent -Query 'SELECT * FROM Win32_DeviceChangeEvent' -SourceIdentifier 'A4techDeviceChange' | Out-Null
        Write-Log 'WORKER started (device events plus 15-second reconciliation).'
        $nextScan = [DateTime]::MinValue
        while (-not (Test-Path -LiteralPath $script:StopPath)) {
            $events = @(Get-Event -SourceIdentifier 'A4techDeviceChange' -ErrorAction SilentlyContinue)
            foreach ($event in $events) { Remove-Event -EventIdentifier $event.EventIdentifier }
            if ($events.Count -gt 0 -or [DateTime]::UtcNow -ge $nextScan) {
                Sync-Camera $config
                $nextScan = [DateTime]::UtcNow.AddSeconds(15)
            }
            Wait-Event -SourceIdentifier 'A4techDeviceChange' -Timeout 3 | Out-Null
        }
    } catch { $failed = $true; Write-Log ('ERROR ' + $_.Exception.Message) }
    finally {
        Unregister-Event -SourceIdentifier 'A4techDeviceChange' -ErrorAction SilentlyContinue
        Get-Event -SourceIdentifier 'A4techDeviceChange' -ErrorAction SilentlyContinue | Remove-Event
        try { Restore-Camera $config } catch { $failed = $true; Write-Log ('RECOVERY ERROR ' + $_.Exception.Message) }
        Write-Log 'WORKER exited.'
    }
    if ($failed) { exit 1 }
}

function Show-Status {
    Write-Host "`nPresent cameras (Code 0 = ready in PnP; 22 = disabled):" -ForegroundColor Cyan
    Get-CameraInventory | Format-Table Name, Code, Id -AutoSize | Out-Host
    if (-not (Test-Path -LiteralPath $script:ConfigPath)) { Write-Host 'Not installed.'; return }
    $config = Read-Config
    Write-Host "Managed laptop camera: $($config.InternalName)"
    Write-Host "Disabled/claimed by tool: $(Read-Owned $config)"
    $task = Get-OurTask
    if ($null -eq $task) { Write-Host 'Scheduled task missing.' } else {
        $task | Select-Object TaskName, State | Format-Table | Out-Host
        Get-ScheduledTaskInfo -TaskName $script:TaskName -TaskPath '\' | Select-Object LastRunTime, LastTaskResult | Format-List | Out-Host
    }
    if (Test-Path -LiteralPath $script:LogPath) { Get-Content -LiteralPath $script:LogPath -Tail 12 -Encoding UTF8 | Out-Host }
    Write-Host 'PnP ready is not a video-frame test. Check the image in your application.'
}

function Remove-Tool {
    if (-not (Test-Path -LiteralPath $script:ConfigPath)) { throw 'No installation config. Check Status / Device Manager.' }
    $config = Read-Config
    Stop-Worker
    Restore-Camera $config
    if ($null -ne (Get-OurTask)) { Unregister-ScheduledTask -TaskName $script:TaskName -TaskPath '\' -Confirm:$false }
    $target = Get-Item -LiteralPath $script:InstallDir
    $expected = [IO.Path]::GetFullPath((Join-Path $programRoot 'A4techCameraPriority')).TrimEnd('\')
    if ($target.FullName.TrimEnd('\') -ne $expected -or ($target.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Unexpected uninstall target; files retained.' }
    foreach ($item in Get-ChildItem -LiteralPath $script:InstallDir -Recurse -Force) {
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse point found; files retained.' }
    }
    Remove-Item -LiteralPath $target.FullName -Recurse -Force
    Write-Host 'Uninstalled. Laptop camera restored if it was disabled by this tool.' -ForegroundColor Green
}

try {
    if ($Mode -eq 'Menu') {
        Write-Host "`nA4tech Camera Priority`n1. Diagnose (read only)`n2. Install`n3. Status`n4. Pause + restore laptop`n5. Resume`n6. Uninstall`n0. Exit"
        $selected = Read-Host 'Choose'
        $modes = @{ '1'='Diagnose'; '2'='Install'; '3'='Status'; '4'='Pause'; '5'='Resume'; '6'='Uninstall' }
        if (-not $modes.ContainsKey($selected)) { exit 0 }
        $Mode = $modes[$selected]
    }
    if ($Mode -in @('Install','Pause','Resume','Uninstall')) {
        $admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        if (-not $admin) {
            $arguments = '-NoProfile -ExecutionPolicy Bypass -File "{0}" -Mode {1}' -f $PSCommandPath, $Mode
            if ($NoPause) { $arguments += ' -NoPause' }
            $child = Start-Process -FilePath $script:PowerShell -ArgumentList $arguments -Verb RunAs -Wait -PassThru
            exit $child.ExitCode
        }
    }
    switch ($Mode) {
        'Diagnose' {
            Write-Host 'READ ONLY: no device, task, registry or camera stream will be changed.'
            Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber | Format-List | Out-Host
            Get-CameraInventory | Format-Table Name, Class, Code, Id -AutoSize | Out-Host
        }
        'Install' { Install-Tool }
        'Run' { Run-Worker }
        'Status' { Show-Status }
        'Pause' { $config = Read-Config; Stop-Worker; Restore-Camera $config; Write-Host 'Paused across reboots; laptop restored. Use Resume to restart.' }
        'Resume' {
            $null = Read-Config
            if ($null -eq (Get-OurTask)) { throw 'Task missing. Uninstall and install again.' }
            Remove-Item -LiteralPath $script:StopPath -Force -ErrorAction SilentlyContinue
            Enable-ScheduledTask -TaskName $script:TaskName -TaskPath '\' | Out-Null
            Start-ScheduledTask -TaskName $script:TaskName -TaskPath '\'
            Write-Host 'Automatic priority enabled; use Status to check.'
        }
        'Uninstall' { Remove-Tool }
    }
} catch {
    Write-Host ('ERROR: ' + $_.Exception.Message) -ForegroundColor Red
    if ($Mode -ne 'Run' -and -not $NoPause) { Read-Host 'Press Enter to close' | Out-Null }
    exit 1
}
if ($Mode -ne 'Run' -and -not $NoPause) { Read-Host 'Press Enter to close' | Out-Null }

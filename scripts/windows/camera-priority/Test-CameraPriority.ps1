#requires -Version 5.1
# All device/task/ACL mutations below are fake. Never installs or toggles hardware.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'CameraPolicy.psm1') -Force
$sourcePath = Join-Path $PSScriptRoot 'CameraPriority.ps1'
$tokens = $null; $errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($sourcePath, [ref]$tokens, [ref]$errors)
if ($errors.Count) { throw ($errors | Out-String) }
# Load only function definitions, never the executable entrypoint/elevation logic.
foreach ($definition in $ast.FindAll({ param($a) $a -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $false)) {
    # Never even load the installer/worker into this simulation process.
    if ($definition.Name -in @('Install-Tool','Run-Worker')) { continue }
    . ([scriptblock]::Create($definition.Extent.Text))
}
$script:Passed = 0
$script:Calls = New-Object 'System.Collections.Generic.List[string]'
$script:TaskName = 'A4techCameraPriority'
$script:SourceDir = $PSScriptRoot
$script:Task = $null
$script:FailDisable = $false
$script:FailEnable = $false
$script:FailInventory = $false
$script:PowerShell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
$script:TestRoot = Join-Path $PSScriptRoot ('.test-work-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $script:TestRoot | Out-Null
$programRoot = $script:TestRoot

function Assert-Equal($Actual, $Expected, [string]$Message) {
    if ($Actual -ne $Expected) { throw "$Message expected=[$Expected] actual=[$Actual]" }
}
function Assert-Throws([scriptblock]$Body, [string]$Message) {
    $thrown = $false
    try { & $Body } catch { $thrown = $true }
    if (-not $thrown) { throw "Expected failure: $Message" }
}
function Test-Case([string]$Name, [scriptblock]$Body) {
    # Refuse to run if any provider fake was replaced by an imported command.
    foreach ($provider in @('Enable-PnpDevice','Disable-PnpDevice','Get-CameraInventory',
        'Disable-ScheduledTask','Stop-ScheduledTask','Unregister-ScheduledTask','Register-ScheduledTask','Set-Acl')) {
        $command = Get-Command $provider -ErrorAction Stop
        if ($command.CommandType -ne 'Function' -or $command.ScriptBlock.File -ne $PSCommandPath) {
            throw "Simulation provider is not local: $provider"
        }
    }
    & $Body
    $script:Passed++
    Write-Host "PASS $Name"
}
function Set-TestPaths {
    $script:InstallDir = Join-Path $script:TestRoot 'A4techCameraPriority'
    $script:ConfigPath = Join-Path $script:InstallDir 'config.json'
    $script:StatePath = Join-Path $script:InstallDir 'state.json'
    $script:StopPath = Join-Path $script:InstallDir 'stop.request'
    $script:LogPath = Join-Path $script:InstallDir 'camera-priority.log'
}
Set-TestPaths
$script:Config = [pscustomobject]@{
    Product='A4techCameraPriority'; Version=1
    PreferredPrefix='USB\VID_09DA&PID_2697&MI_00\'
    PreferredName='A4tech HD 720P PC Camera'
    InternalId='USB\VID_13D3&PID_5463&MI_00\fixture-laptop'
    InternalName='USB2.0 HD UVC WebCam'
}
function Reset-Fixture {
    $script:Task = $null
    $script:FailDisable = $false; $script:FailEnable = $false; $script:FailInventory = $false
    $script:Calls.Clear()
    $script:Inventory = @(
        [pscustomobject]@{ Name=$script:Config.InternalName; Id=$script:Config.InternalId; Class='Camera'; Code=0 },
        [pscustomobject]@{ Name=$script:Config.PreferredName; Id=($script:Config.PreferredPrefix+'fixture-usb'); Class='Camera'; Code=0 }
    )
    if (-not (Test-Path -LiteralPath $script:InstallDir)) { New-Item -ItemType Directory -Path $script:InstallDir | Out-Null }
    Remove-Item -LiteralPath $script:StopPath -Force -ErrorAction SilentlyContinue
    Write-JsonAtomic $script:ConfigPath $script:Config
    Save-Owned $script:Config $false
}

# Fakes shadow production providers. No live PnP or Scheduled Task writes occur.
function Get-CameraInventory {
    if ($script:FailInventory) { throw 'FAKE inventory failure' }
    return $script:Inventory
}
function Disable-PnpDevice {
    [CmdletBinding(SupportsShouldProcess)] param([string]$InstanceId)
    if (-not (Read-Owned $script:Config)) { throw 'Ownership must be durable before Disable.' }
    $script:Calls.Add('Disable:'+ $InstanceId)
    if ($script:FailDisable) { throw 'FAKE disable failure' }
    ($script:Inventory | Where-Object Id -eq $InstanceId).Code = 22
}
function Enable-PnpDevice {
    [CmdletBinding(SupportsShouldProcess)] param([string]$InstanceId)
    $script:Calls.Add('Enable:'+ $InstanceId)
    if ($script:FailEnable) { throw 'FAKE enable failure' }
    ($script:Inventory | Where-Object Id -eq $InstanceId).Code = 0
}
function Start-Sleep { param($Milliseconds, $Seconds) }
function Get-OurTask { return $script:Task }
function Disable-ScheduledTask { param($TaskName,$TaskPath) $script:Calls.Add('TaskDisable'); $script:Task.State='Ready' }
function Stop-ScheduledTask { param($TaskName,$TaskPath) $script:Calls.Add('TaskStop'); $script:Task.State='Ready' }
function Unregister-ScheduledTask {
    [CmdletBinding(SupportsShouldProcess)] param($TaskName,$TaskPath)
    $script:Calls.Add('TaskDelete'); $script:Task=$null
}
function Register-ScheduledTask {
    throw 'Installer/task registration is forbidden in this simulation.'
}
function Start-ScheduledTask { throw 'Starting real/background workers is forbidden in this simulation.' }
function Set-Acl { throw 'Changing ACLs is forbidden in this simulation.' }

try {
    Test-Case 'policy: A4tech ready -> disable laptop' { Assert-Equal (Get-CameraDecision 0 $true $false) 'Disable' 'decision' }
    Test-Case 'policy: unplug/error -> restore owned laptop' { Assert-Equal (Get-CameraDecision 22 $false $true) 'Restore' 'decision' }
    Test-Case 'policy: manual disable must remain untouched' { Assert-Equal (Get-CameraDecision 22 $false $false) 'None' 'decision' }
    Test-Case 'policy: missing laptop -> wait' { Assert-Equal (Get-CameraDecision $null $true $true) 'Wait' 'decision' }
    Test-Case 'policy: existing enabled laptop -> no-op' { Assert-Equal (Get-CameraDecision 0 $false $false) 'None' 'decision' }
    Test-Case 'policy: laptop error -> no disable' { Assert-Equal (Get-CameraDecision 10 $true $false) 'None' 'decision' }
    Test-Case 'config: USB port independent prefix' {
        Assert-Equal (Get-PreferredPrefix ($script:Config.PreferredPrefix+'other-port')) $script:Config.PreferredPrefix 'prefix'
        Assert-CameraConfig $script:Config
    }
    Test-Case 'config: wildcard ID, wrong preferred hardware, identical devices rejected' {
        foreach ($kind in @('wildcard','hardware','same')) {
            $bad=$script:Config | ConvertTo-Json | ConvertFrom-Json
            switch ($kind) {
                'wildcard' { $bad.InternalId='USB\*' }
                'hardware' { $bad.PreferredPrefix='USB\VID_0000&PID_0000\' }
                'same' { $bad.InternalId=$bad.PreferredPrefix+'same-camera' }
            }
            Assert-Throws { Assert-CameraConfig $bad } $kind
        }
    }
    Test-Case 'orchestration: repeated arrival is idempotent; ownership precedes disable' {
        Reset-Fixture; Sync-Camera $script:Config; Sync-Camera $script:Config
        Assert-Equal $script:Calls.Count 1 'single toggle'
        Assert-Equal $script:Calls[0] ('Disable:'+$script:Config.InternalId) 'exact ID'
        Assert-Equal (Read-Owned $script:Config) $true 'owned'
    }
    Test-Case 'orchestration: unplug restores only managed laptop' {
        $script:Inventory=@($script:Inventory[0]); Sync-Camera $script:Config
        Assert-Equal $script:Inventory[0].Code 0 'enabled'
        Assert-Equal (Read-Owned $script:Config) $false 'released'
    }
    Test-Case 'orchestration: replug on another port works' {
        Reset-Fixture; $script:Inventory[1].Id=$script:Config.PreferredPrefix+'new-port'; Sync-Camera $script:Config
        Assert-Equal $script:Inventory[0].Code 22 'disabled'
    }
    Test-Case 'orchestration: unhealthy preferred camera restores laptop' {
        $script:Inventory[1].Code=10; Sync-Camera $script:Config
        Assert-Equal $script:Inventory[0].Code 0 'restored'
    }
    Test-Case 'orchestration: two matching A4tech devices -> restore' {
        Reset-Fixture; Sync-Camera $script:Config
        $script:Inventory+= [pscustomobject]@{Name='A4tech';Id=($script:Config.PreferredPrefix+'second');Class='Camera';Code=0}
        Sync-Camera $script:Config; Assert-Equal $script:Inventory[0].Code 0 'restored'
    }
    Test-Case 'orchestration: preexisting disabled laptop never claimed/enabled' {
        Reset-Fixture; $script:Inventory[0].Code=22
        Sync-Camera $script:Config; $script:Inventory=@($script:Inventory[0]); Sync-Camera $script:Config
        Restore-Camera $script:Config; Assert-Equal $script:Calls.Count 0 'no toggles'
    }
    Test-Case 'orchestration: inventory exception cannot be interpreted as preferred ready' {
        Reset-Fixture; $script:FailInventory=$true
        Assert-Throws { Sync-Camera $script:Config } 'inventory failure'
        Assert-Equal $script:Calls.Count 0 'no toggles'
    }
    Test-Case 'recovery: failed disable retains durable ownership; restore releases it' {
        Reset-Fixture; $script:FailDisable=$true
        Assert-Throws { Sync-Camera $script:Config } 'disable failure'
        Assert-Equal (Read-Owned $script:Config) $true 'durable state'
        Restore-Camera $script:Config; Assert-Equal (Read-Owned $script:Config) $false 'recovered'
    }
    Test-Case 'recovery: lost process with saved ownership and USB absent' {
        Reset-Fixture; Save-Owned $script:Config $true
        $script:Inventory[0].Code=22; $script:Inventory=@($script:Inventory[0])
        Sync-Camera $script:Config; Assert-Equal $script:Inventory[0].Code 0 'restored after restart'
    }
    Test-Case 'recovery: absent laptop retains ownership for later retry' {
        Reset-Fixture; Save-Owned $script:Config $true; $script:Inventory=@($script:Inventory[1])
        Assert-Throws { Restore-Camera $script:Config } 'laptop absent'
        Assert-Equal (Read-Owned $script:Config) $true 'retained'
    }
    Test-Case 'recovery: corrupt state fails closed before any toggle' {
        Reset-Fixture; Set-Content -LiteralPath $script:StatePath -Value '{bad-json' -Encoding UTF8
        Assert-Throws { Sync-Camera $script:Config } 'corrupt state'
        Assert-Equal $script:Calls.Count 0 'no toggles'
    }
    Test-Case 'stop marker prevents new disable' {
        Reset-Fixture; Set-Content -LiteralPath $script:StopPath -Value stop
        Sync-Camera $script:Config; Assert-Equal $script:Calls.Count 0 'no toggles'
    }
    Test-Case 'pause flow: task disabled before restoring laptop' {
        Reset-Fixture; Sync-Camera $script:Config
        $script:Task=[pscustomobject]@{State='Running'}; $script:Calls.Clear()
        Stop-Worker; Restore-Camera $script:Config
        Assert-Equal $script:Calls[0] 'TaskDisable' 'disable task first'
        Assert-Equal (Test-Path -LiteralPath $script:StopPath) $true 'stop marker'
        Assert-Equal $script:Inventory[0].Code 0 'restored'
    }
    Test-Case 'uninstall failure retains config/task when restore fails' {
        Reset-Fixture; Sync-Camera $script:Config
        $script:Task=[pscustomobject]@{State='Running'}; $script:FailEnable=$true
        Assert-Throws { Remove-Tool } 'enable failed'
        Assert-Equal (Test-Path -LiteralPath $script:ConfigPath) $true 'config retained'
        Assert-Equal ($null -ne $script:Task) $true 'task retained'
    }
    Test-Case 'uninstall success restores before deleting task and scoped folder' {
        $script:FailEnable=$false; $script:Calls.Clear(); Remove-Tool
        Assert-Equal $script:Calls[1] ('Enable:'+$script:Config.InternalId) 'enable before deletion'
        Assert-Equal $script:Calls[2] 'TaskDelete' 'delete task after restore'
        Assert-Equal (Test-Path -LiteralPath $script:InstallDir) $false 'folder removed'
    }
    Write-Host "PASS $script:Passed test cases (SIMULATION; no hardware/task/ACL writes)."
} finally {
    # Resolved, task-specific workspace subtree only; reject junctions before recursive deletion.
    $testTarget = Get-Item -LiteralPath $script:TestRoot
    $testParent = [IO.Path]::GetFullPath($PSScriptRoot).TrimEnd('\')+'\'
    if (-not $testTarget.FullName.StartsWith($testParent, [StringComparison]::OrdinalIgnoreCase) -or
        -not $testTarget.Name.StartsWith('.test-work-') -or
        ($testTarget.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Unsafe test cleanup path.' }
    foreach ($child in Get-ChildItem -LiteralPath $testTarget.FullName -Recurse -Force) {
        if ($child.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Unsafe test cleanup reparse point.' }
    }
    Remove-Item -LiteralPath $testTarget.FullName -Recurse -Force
}

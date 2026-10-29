#requires -Version 5.1
Set-StrictMode -Version Latest

function Get-CameraDecision {
    param([AllowNull()] $InternalCode, [bool] $PreferredReady, [bool] $Owned)
    if ($null -eq $InternalCode) { return 'Wait' }
    if ($PreferredReady -and $InternalCode -eq 0) { return 'Disable' }
    if (-not $PreferredReady -and $Owned -and $InternalCode -eq 22) { return 'Restore' }
    if (-not $PreferredReady -and $Owned -and $InternalCode -eq 0) { return 'Release' }
    return 'None'
}

function Get-CameraInventory {
    @(Get-PnpDevice -PresentOnly -ErrorAction Stop | Where-Object {
        $_.Class -in @('Camera', 'Image')
    } | ForEach-Object {
        $code = Get-PnpDeviceProperty -InstanceId $_.InstanceId `
            -KeyName 'DEVPKEY_Device_ProblemCode' -ErrorAction Stop
        [pscustomobject]@{
            Name = $_.FriendlyName; Id = $_.InstanceId
            Class = $_.Class; Code = [int] $code.Data
        }
    })
}

function Get-PreferredPrefix {
    param([string] $Id)
    if ($Id -notmatch '^(USB\\VID_[0-9A-F]{4}&PID_[0-9A-F]{4}(?:&MI_[0-9A-F]{2})?\\)') {
        throw 'Preferred device must have a USB VID/PID camera interface ID.'
    }
    return $Matches[1]
}

function Assert-CameraConfig {
    param($Config)
    if ($Config.Product -ne 'A4techCameraPriority' -or $Config.Version -ne 1) { throw 'Unknown config format.' }
    if ($Config.InternalId -notmatch '^USB\\' -or $Config.InternalId.Contains('*') -or
        $Config.InternalId.Contains('?') -or $Config.InternalId.Contains('[')) {
        throw 'Internal camera ID must be an exact USB instance ID.'
    }
    if ($Config.PreferredPrefix -notmatch '^USB\\VID_09DA&PID_2697(?:&MI_[0-9A-F]{2})?\\$') {
        throw 'Unexpected A4tech hardware ID. Re-run setup with the intended camera.'
    }
    if ($Config.InternalId.StartsWith($Config.PreferredPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Preferred camera and fallback camera must be different.'
    }
}

Export-ModuleMember -Function Get-CameraDecision, Get-CameraInventory, Get-PreferredPrefix, Assert-CameraConfig

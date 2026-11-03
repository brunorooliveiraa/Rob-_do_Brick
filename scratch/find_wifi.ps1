$classKey = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
Get-ChildItem $classKey | ForEach-Object {
    $props = Get-ItemProperty $_.PSPath
    if ($props.DriverDesc -like "*8822*") {
        Write-Host "Realtek Key: $($_.PSPath)"
        Write-Host "DriverDesc: $($props.DriverDesc)"
        Write-Host "PnPCapabilities: $($props.PnPCapabilities)"
        $props | Get-Member -MemberType NoteProperty | ForEach-Object {
            $name = $_.Name
            if ($name -match "Power|Sleep|Save|Idle|PnP|Lid|Suspend") {
                Write-Host "  $name = $($props.$name)"
            }
        }
    }
}

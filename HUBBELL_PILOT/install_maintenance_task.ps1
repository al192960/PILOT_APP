$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = Join-Path $ProjectDir ".venv\Scripts\python.exe"
$MaintenanceScript = Join-Path $ProjectDir "maintenance.py"
$TaskName = "PalletID Weekly Cleanup"

if (-not (Test-Path $PythonExe)) {
    Write-Host "ERROR: Python virtual environment was not found:"
    Write-Host $PythonExe
    exit 1
}

if (-not (Test-Path $MaintenanceScript)) {
    Write-Host "ERROR: maintenance.py was not found:"
    Write-Host $MaintenanceScript
    exit 1
}

$Action = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument "`"$MaintenanceScript`"" `
    -WorkingDirectory $ProjectDir

$Trigger = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek Monday `
    -At 4:00AM

$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -WakeToRun `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew

$Principal = New-ScheduledTaskPrincipal `
    -UserId "SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel Highest

$Task = New-ScheduledTask `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "Deletes all generated QR and label files every Monday at 4:00 AM. If the PC was off, it runs when Windows is available."

Register-ScheduledTask `
    -TaskName $TaskName `
    -InputObject $Task `
    -Force | Out-Null

Write-Host ""
Write-Host "Task created successfully:"
Write-Host $TaskName
Write-Host ""
Write-Host "Schedule: Every Monday at 4:00 AM"
Write-Host "Missed run: Start as soon as possible when Windows is available"
Write-Host "Wake from sleep: Enabled"
Write-Host "Runs as: SYSTEM"

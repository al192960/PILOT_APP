$TaskName = "PalletID Weekly Cleanup"

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Task removed successfully: $TaskName"
}
else {
    Write-Host "Task was not found: $TaskName"
}

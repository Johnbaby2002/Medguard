$backendPath = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$matches = Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -and
    $_.CommandLine -like "*uvicorn*" -and
    $_.CommandLine -like "*app.main:app*" -and
    $_.CommandLine -like "*$backendPath*"
  }

if (-not $matches) {
  Write-Host "No MedGuard uvicorn backend processes found."
  exit 0
}

foreach ($process in $matches) {
  Write-Host "Stopping MedGuard backend process $($process.ProcessId)"
  Stop-Process -Id $process.ProcessId -Force
}

$ports = @()

foreach ($port in 8000..8010) {
  $connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
  foreach ($connection in $connections) {
    $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
    $ports += [pscustomobject]@{
      Port = $port
      ProcessId = $connection.OwningProcess
      ProcessName = $process.ProcessName
      Path = $process.Path
    }
  }
}

if ($ports.Count -eq 0) {
  Write-Host "No listening processes found on ports 8000-8010."
} else {
  $ports | Format-Table -AutoSize
}

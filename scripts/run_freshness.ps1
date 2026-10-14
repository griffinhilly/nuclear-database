# Monthly freshness run (Windows Task Scheduler "NuclearDB Freshness", 1st of each month).
# Purpose: pull IAEA PRIS, then list facts that time has made stale. Read-only on the database.
# Outputs: audit/freshness/<yyyy-MM-dd>.txt (report) and audit/freshness/<yyyy-MM-dd>.log (run log).
# Review the report with Griffin; any data change still goes through a migration.
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$py = 'C:\Python314\python.exe'
$day = Get-Date -Format 'yyyy-MM-dd'
$dir = Join-Path $root 'audit\freshness'
New-Item -ItemType Directory -Force -Path $dir | Out-Null
$log = Join-Path $dir "$day.log"
"run started $(Get-Date -Format o)" | Out-File -FilePath $log -Encoding utf8
& $py scripts\pris_api_pull.py --force 2>&1 | Out-File -FilePath $log -Append -Encoding utf8
& $py scripts\freshness_check.py --out (Join-Path $dir "$day.txt") 2>&1 | Out-File -FilePath $log -Append -Encoding utf8
"freshness exit code $LASTEXITCODE (1 = action items listed, not a failure)" | Out-File -FilePath $log -Append -Encoding utf8

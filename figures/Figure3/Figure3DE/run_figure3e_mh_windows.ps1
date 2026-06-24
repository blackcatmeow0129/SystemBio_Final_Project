param(
    [string]$Fits = "$HOME\cre_reproduction\neoParSA\tests\transcpp\fits",
    [string]$Transcpp = "$HOME\cre_reproduction\transcpp\transcpp.exe",
    [int]$Parallel = 6
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Set-Location $Fits
Write-Host "=== Figure 3E multi-hit prediction start: parallel=$Parallel ==="

$jobs = New-Object System.Collections.Generic.List[object]
Get-ChildItem "fig3de_mh_xmls\*_mh_v2.xml" | ForEach-Object {
    $xml = $_.FullName
    $rates = $xml -replace "\.xml$", ".xml.rates"
    if (Test-Path $rates) { return }

    while (($jobs | Where-Object { $_.HasExited -eq $false }).Count -ge $Parallel) {
        Start-Sleep -Seconds 3
    }

    $log = Join-Path $_.DirectoryName "$($_.BaseName).log"
    $process = Start-Process -FilePath $Transcpp -ArgumentList @($xml) -NoNewWindow -PassThru -RedirectStandardOutput $log -RedirectStandardError "$log.err"
    $jobs.Add($process)
}

while (($jobs | Where-Object { $_.HasExited -eq $false }).Count -gt 0) {
    Start-Sleep -Seconds 5
}
Write-Host "Done."

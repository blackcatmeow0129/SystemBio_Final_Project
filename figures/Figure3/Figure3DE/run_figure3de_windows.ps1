param(
    [string]$Fits = "$HOME\cre_reproduction\neoParSA\tests\transcpp\fits",
    [string]$Transcpp = "$HOME\cre_reproduction\transcpp\transcpp.exe",
    [int]$Parallel = 6,
    [string[]]$TfCounts = @("1", "2", "3", "4")
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Set-Location $Fits
Write-Host "=== Figure 3D fitting start: n=$($TfCounts -join ',') parallel=$Parallel ==="

$jobs = New-Object System.Collections.Generic.List[object]
foreach ($n in $TfCounts) {
    Get-ChildItem "fig3de_xmls\fig3de_n${n}_*.xml" | ForEach-Object {
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
}

while (($jobs | Where-Object { $_.HasExited -eq $false }).Count -gt 0) {
    Start-Sleep -Seconds 5
}
Write-Host "Done."

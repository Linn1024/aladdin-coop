param(
    [Parameter(Mandatory=$true)][string]$BizHawkDirectory,
    [string]$ToolchainBin = $env:ALADDIN_MINGW_BIN
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath (Join-Path $BizHawkDirectory 'EmuHawk.exe'))) {
    throw 'BizHawkDirectory must contain EmuHawk.exe.'
}
& (Join-Path (Split-Path $PSScriptRoot) 'build.ps1') -ToolchainBin $ToolchainBin -CoreOnly
$destination = Join-Path $BizHawkDirectory 'Libretro/Cores/AladdinCoop'
New-Item -ItemType Directory -Path $destination -Force | Out-Null
foreach ($name in @('aladdin_coop_libretro.dll', 'aladdin_engine.dll')) {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot $name) -Destination (Join-Path $destination $name)
}
Write-Host "Installed in $destination. Restart BizHawk to load the new core."

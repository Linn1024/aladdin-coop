param([string]$ToolchainBin = $env:ALADDIN_MINGW_BIN)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Push-Location $root
try {
    & (Join-Path $root 'build.ps1') -ToolchainBin $ToolchainBin
    # Use a fresh staging folder so local ROMs, saves and old artifacts cannot leak in.
    $stage = Join-Path $root ('dist\installer-build-' + [guid]::NewGuid().ToString('N'))
    $package = Join-Path $stage 'Aladdin-Coop-Windows-Setup'
    $payload = Join-Path $package 'payload'
    $source = Join-Path $stage 'source'
    $null = New-Item -ItemType Directory -Path "$payload\engine", "$package\installer", $source -Force
    Copy-Item -LiteralPath 'Aladdin-Coop.exe' -Destination $payload
    Copy-Item -LiteralPath 'engine\genesis_plus_gx_libretro.dll', 'engine\LICENSE.txt' -Destination "$payload\engine"
    Copy-Item -LiteralPath 'README.md', 'THIRD_PARTY_NOTICES.md' -Destination $payload
    Copy-Item -LiteralPath 'Install.cmd' -Destination $package
    Copy-Item -LiteralPath 'installer\install.ps1' -Destination "$package\installer"
    Copy-Item -LiteralPath 'installer\START-HERE.txt' -Destination $package
    $tracked = @(& git -c "safe.directory=$($root.Replace('\', '/'))" ls-files)
    if ($LASTEXITCODE) { throw 'Cannot enumerate source files using Git.' }
    $files = @($tracked) + @('Install.cmd', 'installer/install.ps1', 'installer/build-package.ps1', 'installer/START-HERE.txt')
    foreach ($relative in ($files | Sort-Object -Unique)) {
        if ($relative -match '(?i)\.(bin|gen|rom|mdrom|smd|state|sav|srm|exe|dll|o|a)$') {
            throw "Unexpected game data or compiled output in source list: $relative"
        }
        $destination = Join-Path $source $relative
        $null = New-Item -ItemType Directory -Path (Split-Path $destination -Parent) -Force
        Copy-Item -LiteralPath (Join-Path $root $relative) -Destination $destination
    }
    # ZipFile includes dotfiles required to reproduce the build.
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [IO.Compression.ZipFile]::CreateFromDirectory($source, "$payload\source.zip")
    $zip = Join-Path $stage 'Aladdin-Coop-Windows-Setup.zip'
    [IO.Compression.ZipFile]::CreateFromDirectory($package, $zip)
    $output = Join-Path $root 'dist\Aladdin-Coop-Windows-Setup.zip'
    Copy-Item -LiteralPath $zip -Destination $output -Force
    Write-Host "Installer package: $output"
} finally { Pop-Location }

param(
    [string]$RomPath,
    [string]$InstallDirectory = (Join-Path $env:LOCALAPPDATA 'Aladdin Co-op'),
    [switch]$NonInteractive,
    [switch]$NoShortcuts
)
$ErrorActionPreference = 'Stop'
try {
    if (-not [Environment]::Is64BitOperatingSystem) { throw 'Aladdin Co-op requires 64-bit Windows.' }
    $package = Split-Path $PSScriptRoot -Parent
    $payload = Join-Path $package 'payload'
    foreach ($file in @('Aladdin-Coop.exe', 'engine\genesis_plus_gx_libretro.dll', 'source.zip', 'README.md', 'THIRD_PARTY_NOTICES.md', 'engine\LICENSE.txt')) {
        if (-not (Test-Path -LiteralPath (Join-Path $payload $file) -PathType Leaf)) {
            throw 'This is not a built installer package. Download and extract Aladdin-Coop-Windows-Setup.zip, or build it with installer\build-package.ps1.'
        }
    }
    if (-not $RomPath) {
        if ($NonInteractive) { throw 'Specify -RomPath when using -NonInteractive.' }
        Add-Type -AssemblyName System.Windows.Forms
        $picker = New-Object System.Windows.Forms.OpenFileDialog
        $picker.Title = 'Select your original Aladdin USA ROM'
        $picker.Filter = 'Genesis ROM (*.bin;*.gen;*.md)|*.bin;*.gen;*.md|All files (*.*)|*.*'
        try {
            if ($picker.ShowDialog() -ne 'OK') { Write-Host 'Installation cancelled.'; exit 0 }
            $RomPath = $picker.FileName
        } finally { $picker.Dispose() }
    }
    $RomPath = (Resolve-Path -LiteralPath $RomPath).Path
    if ((Get-FileHash -LiteralPath $RomPath -Algorithm SHA256).Hash -ne 'a3779fc77994780e80d05bb557f800110d0398d34b951baa8c0a14910014ded3') {
        throw 'This ROM is not the supported Aladdin USA version. Select the original unmodified ROM; ZIP and SMD files must be extracted or converted first.'
    }
    $InstallDirectory = [IO.Path]::GetFullPath($InstallDirectory)
    if ($InstallDirectory.TrimEnd('\') -eq $payload.TrimEnd('\')) { throw 'Choose an installation folder outside the installer payload.' }
    $null = New-Item -ItemType Directory -Path $InstallDirectory -Force
    # Copy only distributed files; existing saves and other player files are preserved.
    foreach ($file in Get-ChildItem -LiteralPath $payload -File -Recurse) {
        $relative = $file.FullName.Substring($payload.Length + 1)
        $destination = Join-Path $InstallDirectory $relative
        $null = New-Item -ItemType Directory -Path (Split-Path $destination -Parent) -Force
        Copy-Item -LiteralPath $file.FullName -Destination $destination -Force
    }
    $installedRom = Join-Path $InstallDirectory 'Aladdin_(U)_[!].bin'
    if ($RomPath -ne $installedRom) { Copy-Item -LiteralPath $RomPath -Destination $installedRom -Force }
    if (-not $NoShortcuts) {
        $shell = New-Object -ComObject WScript.Shell
        foreach ($folder in @([Environment]::GetFolderPath('DesktopDirectory'), [Environment]::GetFolderPath('Programs'))) {
            $shortcut = $shell.CreateShortcut((Join-Path $folder 'Aladdin Co-op.lnk'))
            $shortcut.TargetPath = Join-Path $InstallDirectory 'Aladdin-Coop.exe'
            $shortcut.WorkingDirectory = $InstallDirectory
            $shortcut.Description = 'Play Aladdin with two players'
            $shortcut.Save()
        }
    }
    Write-Host "Installed Aladdin Co-op to $InstallDirectory"
    if (-not $NonInteractive) {
        Add-Type -AssemblyName System.Windows.Forms
        $null = [System.Windows.Forms.MessageBox]::Show("Aladdin Co-op is installed!`n`nOpen Aladdin Co-op from your desktop or Start menu to play.`n`nP1: WASD, F/G/Space. P2: arrows, J/K/L.`n`nInstalled in: $InstallDirectory", 'Aladdin Co-op')
    }
} catch {
    Write-Host "Installation failed: $($_.Exception.Message)" -ForegroundColor Red
    if (-not $NonInteractive) {
        Add-Type -AssemblyName System.Windows.Forms
        $null = [System.Windows.Forms.MessageBox]::Show($_.Exception.Message, 'Aladdin Co-op installation failed')
    }
    exit 1
}

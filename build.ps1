param(
    [string]$ToolchainBin = $env:ALADDIN_MINGW_BIN,
    [switch]$CoreOnly
)
$ErrorActionPreference = 'Stop'
$oldPath = $env:PATH
Push-Location $PSScriptRoot
try {
    if ($ToolchainBin) { $env:PATH = $ToolchainBin + ';' + $oldPath }
    foreach ($command in @('mingw32-make', 'g++')) {
        if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
            throw "Missing $command. Install a 64-bit MinGW-w64 toolchain and pass -ToolchainBin its bin directory."
        }
    }
    $target = & g++ -dumpmachine
    if ($LASTEXITCODE -or $target -notmatch '^x86_64-') {
        throw 'A 64-bit MinGW-w64 compiler is required. Pass -ToolchainBin the directory containing x86_64 g++ and mingw32-make.'
    }
    (Get-Item engine/core/m68k/m68kcpu.c).LastWriteTime = Get-Date
    & mingw32-make -C engine -f Makefile.libretro platform=win HAVE_CHD=0 HAVE_SYS_PARAM=0 GIT_VERSION= -j8 -s
    if ($LASTEXITCODE) { throw 'Core build failed' }
    if (-not $CoreOnly) {
        & g++ launcher.cpp -o Aladdin-Coop.exe -O2 -std=c++17 -static -mwindows -lwinmm -lgdi32 -luser32 -lbcrypt
        if ($LASTEXITCODE) { throw 'Launcher build failed; close the standalone game before rebuilding' }
    }
    & g++ bizhawk/aladdin_libretro.cpp -o bizhawk/aladdin_coop_libretro.dll -O2 -std=c++17 -static -shared -lbcrypt -lgdi32
    if ($LASTEXITCODE) { throw 'Adapter build failed' }
    Copy-Item -LiteralPath engine/genesis_plus_gx_libretro.dll -Destination bizhawk/aladdin_engine.dll
} finally {
    $env:PATH = $oldPath
    Pop-Location
}

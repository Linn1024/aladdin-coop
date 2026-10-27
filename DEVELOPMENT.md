# Development guide

Shared workflow: [common co-op development guide](../coop-guides/COOP-DEVELOPMENT.md).

## Building

Requires Windows x64, PowerShell, and a 64-bit MinGW-w64 toolchain providing
`mingw32-make` and `g++`. The complete engine sources are included.

```powershell
.\build.ps1 -ToolchainBin 'C:\path\to\mingw64\bin'
```

If the compiler tools are already on PATH, omit `-ToolchainBin`. Alternatively
set `ALADDIN_MINGW_BIN`. Close the standalone game before rebuilding its EXE.
The build produces the standalone launcher and both DLLs for BizHawk.

For BizHawk, close the emulator and run:

```powershell
.\bizhawk\build-install.ps1 -BizHawkDirectory 'C:\path\to\BizHawk' -ToolchainBin 'C:\path\to\mingw64\bin'
```

See [BizHawk setup](bizhawk/README.md) for loading the custom Libretro core and
mapping controllers. Runtime does not require a first-level save state.

For standalone play, put your supported ROM in the project root with the exact
filename `Aladdin_(U)_[!].bin`, then run `Aladdin-Coop.exe` from that directory.

Recent co-op fixes include independent horizontal-rope animation, P2 look-up
scrolling, the optional Rooftops flute, the palace key passage, and scripted
carpets boarding correctly for either player. Older palace saves with the key
collected by P2 recover the blocked passage when loaded.

## Windows installer package

Run `powershell -NoProfile -File .\installer\build-package.ps1 -ToolchainBin 'C:\path\to\mingw64\bin'`
to rebuild the game and create `dist\Aladdin-Coop-Windows-Setup.zip`.
Omit `-ToolchainBin` when the tools are on PATH. Distribute this ZIP; users
extract it and double-click `Install.cmd`. Windows PowerShell 5.1 is sufficient.
The package includes the standalone game, complete tracked source from the working
tree, and license notices. ROMs, saves, and untracked local files are excluded.
Generated packages are not committed to Git.

For automated installation checks, extract the ZIP and run:

```powershell
powershell -NoProfile -File .\installer\install.ps1 -NonInteractive -NoShortcuts -RomPath 'C:\games\Aladdin.bin' -InstallDirectory 'C:\temp\Aladdin test'
```

The normal installer creates shortcuts and installs under `%LOCALAPPDATA%\Aladdin Co-op`.
Close the game before reinstalling. Updates preserve player files.

## Development tests

Python checks require Python 3, `ctypes`, and Pillow (`pip install Pillow`).
They require your own supported ROM at the filename above. Most gameplay checks
also require a local `first-level.state` in the inner core's serialization format;
a BizHawk ZIP save is not interchangeable. These development fixtures, user saves,
screenshots and generated reports are deliberately excluded from Git.
The scripts under `bizhawk/` include local reproduction harnesses whose fixture
paths must be adapted. Some older checks predate the current startup/menu flow.

`python bizhawk/verify_normal_options.py` exercises boot, original options and
the hidden pause debug menu without a first-level fixture.
With local fixtures available, key checks include `tools/verify_campaign.py`,
`tools/verify_enemy_death.py`, `tools/verify_window_hands.py`, and
`tools/verify_object_physics.py`. Test output is written locally to `diagnostics/`;
create that directory before running the checks.

Sprite audits: `tools/audit_sprite_art.py` generates native/P2 contact sheets
and checks recolor memory boundaries; `tools/verify_world_sprite_tiles.py`
compares sampled native sprite uploads across all stages.

Core implementation: `engine/core/m68k/aladdin_coop.h`; frontends: `launcher.cpp`
and `bizhawk/aladdin_libretro.cpp`; shared menu: `debug_menu.h`.
The exact supported ROM SHA-256 is
`a3779fc77994780e80d05bb557f800110d0398d34b951baa8c0a14910014ded3`.
Keep the engine source and its notices when redistributing modified builds;
see `engine/LICENSE.txt` for its existing terms.

### Portable standalone startup and settings

coop_desktop.h implements the shared ROM picker, Unicode remembered ROM path,
per-user settings, screen-size/fullscreen menu and settings-folder shortcut.
The original ROM bytes are validated before remembering a location; cancel
exits normally and a missing/changed file returns to the picker. Engine loading
uses the executable's absolute directory, while normal saves/settings use the
per-user Linn1024Coop folder. Existing standalone saves/controls migrate without
overwriting files already there. Test mode keeps isolated legacy diagnostics;
--rom and --settings-dir allow automated checks without changing user settings.
Keyboard/XInput configuration is available from Settings and F2. The source
copy of coop_desktop.h matches coop-releases/desktop/coop_desktop.h. Build
scripts link shell32 and comdlg32. verify_desktop.py in that repository drives
real picker input, external Unicode paths, relaunch, controls, screen resizing,
fullscreen and cancellation for all four games using isolated test folders.


## Portable launcher repaint fix (2026-10-28)

The standalone launcher now composes the entire client area, including black
letterboxing and the pause/debug overlay, into a reusable compatible bitmap.
One BitBlt presents the completed frame. Previously FillRect cleared the visible
window before StretchDIBits drew the game, exposing black during repaint.
WM_ERASEBKGND is handled because paint supplies the whole background.
The back buffer is reused at a stable size and replaced safely on resize.
Core emulation and ROM contents are unchanged.

Validation: actual-window capture found 2 black frames in 90 with the original
launcher and 0 in 90 with the buffered renderer. GDI resources stayed stable
after repeated resizing and fullscreen transitions.

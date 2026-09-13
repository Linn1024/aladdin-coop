# Development guide

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

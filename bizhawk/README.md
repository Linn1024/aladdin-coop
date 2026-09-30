# Aladdin co-op in BizHawk

This adapter has been tested with Windows x64 BizHawk 2.4. Other versions have
not been verified. A stock Genesis core runs the original single-player game.

## Build and install the custom core

The standalone setup package does not install the BizHawk adapter binaries.
Use the complete source repository (or extract the installer's `source.zip`)
and build them as follows. Co-op is implemented in the custom emulator core;
there is no ROM patch or Lua script to load.

1. Have Windows x64, a separate Windows x64 BizHawk installation, and a 64-bit
   MinGW-w64 toolchain with `g++` and `mingw32-make` ready. Close BizHawk.
2. Open PowerShell in the source folder containing `build.ps1`. Run:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\bizhawk\build-install.ps1 -BizHawkDirectory 'C:\Games\BizHawk' -ToolchainBin 'C:\Tools\mingw64\bin'
   ```

   Replace both example paths with your own. `BizHawkDirectory` must contain
   `EmuHawk.exe`. Omit `-ToolchainBin` if the tools are already on `PATH`.
   The script builds the engine and adapter, then copies both DLLs into
   BizHawk's `Libretro\Cores\AladdinCoop` folder.
3. Start BizHawk and select **File > Open Advanced > Libretro**.
4. Select `Libretro/Cores/AladdinCoop/aladdin_coop_libretro.dll` inside your
   BizHawk installation as the core, and your Aladdin USA ROM as the content.
   Opening the ROM normally uses a stock core and will not enable co-op.
5. Under **Config > Controllers**, configure both P1 and P2 RetroPad controls.
   Start a new game; both players should appear during gameplay.

For a manual install after building, copy these two files from the project's
`bizhawk` folder to the same directory in your BizHawk installation:

```text
BizHawk/
  EmuHawk.exe
  Libretro/Cores/AladdinCoop/
    aladdin_coop_libretro.dll
    aladdin_engine.dll
```

Use your own unmodified USA ROM. The adapter checks its SHA-256:

```text
a3779fc77994780e80d05bb557f800110d0398d34b951baa8c0a14910014ded3
```

Check it with `Get-FileHash -LiteralPath 'C:\Games\Aladdin.bin' -Algorithm SHA256`,
substituting your ROM path. When selecting content manually, its filename does
not have to match the standalone launcher's filename.

## Controls

Keep `aladdin_engine.dll` beside `aladdin_coop_libretro.dll`.
No ROM, emulator profile or save state is distributed here. The keyboard bindings
below are suggested mappings; configure them in your own BizHawk profile.
Map RetroPad B to sword, Y to apple, A to jump, L to rejoin, and Start to pause.

The game boots from the beginning with its original title screen and Options.
In Options, press Up from Difficulty to select DEATH, then A/B/C to toggle
PARTNER or CHECKPOINT. Each recovery costs one shared life, shown in the HUD.
All 13 stage records are enabled, including the Abu rooms and boss stages.
Rug Ride has two independently steered carpets.

| Action | Player one | Player two |
| --- | --- | --- |
| Move / climb / crouch | WASD | Arrow keys |
| Sword | F | J |
| Apple | G | K |
| Jump | Space | L |
| Rejoin partner | X | O |

Bind RetroPad Start to Enter / controller Start for normal pause during gameplay
and native Start during interludes. Configure emulator pause, reset, and
save/load shortcuts under **Config > Hotkeys**; they depend on your BizHawk
profile. Avoid assigning emulator hotkeys to your gameplay keys.

Controllers: D-pad/left stick moves, X swings the sword, B throws an apple,
A jumps, Y rejoins. Physical controllers still need manual testing.
Mappings are under Config > Controllers, P1/P2 RetroPad.

## Debug menu

Pause first, then press Genesis A+B+C together (F+G+Space for P1, J+K+L for P2).
Resuming hides debug again. Up/Down selects; Jump applies; Enter resumes. Commands include invincibility,
unlimited apples, healing, a checkpoint at P1, damage tests, and noclip.
For **STAGE**, Left/Right chooses any of the 13 stages; Jump queues the load,
then resume. This also lets you restart a chosen stage without restarting the game.

Noclip lets P1 fly while P2 waits hidden. Turning it off brings both to P1's
position on resume; normal physics then applies. Rug Ride resumes its two-carpet
formation. Stage changes cancel noclip. The other cheat toggles persist across
stages; resetting the core clears them. Damage tests disable invincibility.

## Saves and verification

Restart BizHawk after replacing the core DLLs. Use this custom core to load its
co-op saves; stock Genesis cores do not understand the extra player state.
No first-level save is needed to start playing.
Use BizHawk's own save/load commands. Standalone saves and BizHawk save files
are not interchangeable. Back up saves before updating; compatibility across
custom core revisions is not guaranteed.

## Updates and troubleshooting

- **Only one player:** reopen through Open Advanced > Libretro and select the
  adapter DLL, not the ROM alone or `aladdin_engine.dll`.
- **Core cannot load:** use Windows x64 BizHawk and keep both matching DLLs
  together. The engine DLL alone is not the adapter.
- **ROM rejected:** compare the checksum above; renaming another ROM revision
  does not make it compatible.
- **P2 does not respond:** bind P2 RetroPad as well as P1 and resume emulation.
  To open the debug menu, use the game's Start pause, not emulator pause.
- **Update fails or old behavior remains:** close BizHawk, rerun the build/install
  command, and restart it. Replace both DLLs together.

The source checkout does not include a controller profile or portable launch
shortcut. Manual core selection above works without the developer's local paths.

Development Python/Lua harnesses require local fixtures and may contain local
reproduction paths. See the project README for test limitations.
A complete two-player campaign playthrough has not yet been verified.

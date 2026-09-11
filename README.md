# Aladdin campaign co-op experiment

Two-player co-op for the USA Genesis version of Aladdin, using a custom emulator
core. Boots from the beginning, including the original title screen, Options,
story and campaign. See Building below for setup; no game ROM is included.
All 13 stage records are enabled: the main stages, Iago and Jafar encounters,
and both Abu bonus rooms. P1 wears purple and white; P2 wears a black vest,
brown trousers, a lighter brown sash, and a lighter, warm skin tone.

This is an **experimental emulator-assisted build**. The player-supplied USA ROM is
unchanged. The emulator runs the original player routines with separate player
state and a shared world. It is not a hardware-compatible Genesis ROM patch.

## Controls

| Action | Player one | Player two | Xbox-style controller |
| --- | --- | --- | --- |
| Move / climb / crouch | WASD | Arrow keys | D-pad / left stick |
| Sword | F | J | X |
| Apple | G | K | B |
| Jump | Space | L | A |
| Rejoin partner (Genesis X) | X | O | Y |
| Pause | Enter | Enter | Start |

**BizHawk:** F5 saves slot 1, F8 loads it, P pauses the emulator, Ctrl+R starts
again from the beginning. During gameplay, Enter pauses. Press Genesis A+B+C
(sword + apple + jump: F+G+Space) together while paused to open debug cheats.
During native interludes, Enter acts as the game's Start button.

**Standalone:** open Aladdin-Coop.exe from the project directory. F5 starts again
from the beginning, Enter/F9 pauses, and Esc quits. The standalone has
no quicksave. Use the debug stage selector to restart a particular stage.

## Co-op rules

- Independent movement, attacks, apples, and health; shared enemies and pickups.
  Enemy movement and attack animation callbacks target the nearest living player.
- Two native lamp health meters and one shared native lives counter; score is hidden.
- Midpoint camera and separation limits on normal platform stages.
- Rejoin moves the requesting player to a living, grounded partner while
  preserving health. Successful rejoins and partner revives use the Genie/Abu
  pickup sparkles and sound; leaving noclip uses them too. On Rug Ride, rescue
  can use a living airborne partner.
- In title-screen **Options**, choose **DEATH: PARTNER / CHECKPOINT** (Up from
  Difficulty, then A/B/C to change). Partner mode revives the dead player beside a
  safe survivor; Checkpoint mode resets both when either dies. Both deaths together
  always use the checkpoint. Fatal-hit/drowning presentation finishes before
  recovery (a one-second delay); dead players cannot move or manually rejoin.
  Each recovery costs one shared spare life. At zero,
  the next death opens the original continue/game-over flow. The option persists
  across stages and saves. Full reset restores the default Partner mode.
- Native stage loading and story interludes run between stages. Both players are
  recreated at the next stage's safe starting position.
- Agrabah's exit waits for both players to enter the native exit region. Later
  native exit requests wait for the players to be within 128 pixels on each axis.
  Original exit delays are retained for scripted animations.
- Rug Ride uses two carpets with independent Up/Down steering. The shared camera
  and obstacle sequence advance only once. Forward progression is automatic.

## Debug pause menu

First pause, then hold Genesis A+B+C together (F+G+Space or J+K+L).
Use Up/Down to select and Jump to apply. Enter/Start resumes and hides cheats again.

- Damage invincibility, unlimited apples, and refill both health bars.
- Set a checkpoint at grounded P1; defeat both to test respawn.
- Remove one health point from P1 or P2. Damage tests disable invincibility.
- Noclip / Fly P1: P1 flies through terrain with directional controls; P2 waits
  hidden and enemy simulation pauses. Turn it off and resume to bring both to
  P1's location. Gravity/collisions resume there; on Rug Ride the carpet formation
  resumes. Noclip stays within map bounds.
- **Stage selector:** select STAGE, use Left/Right to choose, then Jump and resume
  to load it. All 13 stages are available.

Health/checkpoint and stage-load actions apply on resume. Stage loading cancels
noclip. Invincibility and unlimited apples persist across stage changes; a full
restart clears them. Saves include the menu, cheats, queued actions, and player
state. Damage tests and setting a checkpoint require noclip to be off.

## Verification and current limits

Automated checks cover loading all 13 stages, P2 movement in each, state replay,
standard-stage checkpoint respawns, native transition routing, carpet steering,
scripted carpet deaths, shared rescue, debug controls, and first-level gameplay.
The user's exit save is tested read-only with ordinary movement into Desert,
including save/load during the transition. Native BizHawk tests exercise the
same exit and the stage selector.

**This is not yet a fully playtested campaign.** Stage-loading and injected
exit/death tests do not prove every puzzle, bonus-room outcome, or boss fight can
be completed normally. A complete two-player run, physical controllers, and
later-stage edge cases still need playtesting. Later-stage bugs should be saved
with F5 so they can be reproduced and fixed.

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

Core implementation: `engine/core/m68k/aladdin_coop.h`; frontends: `launcher.cpp`
and `bizhawk/aladdin_libretro.cpp`; shared menu: `debug_menu.h`.
The exact supported ROM SHA-256 is
`a3779fc77994780e80d05bb557f800110d0398d34b951baa8c0a14910014ded3`.
Keep the engine source and its notices when redistributing modified builds;
see `engine/LICENSE.txt` for its existing terms.

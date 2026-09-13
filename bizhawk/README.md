# Aladdin co-op in BizHawk

This adapter has been tested with Windows x64 BizHawk 2.4. Other versions have
not been verified. A stock Genesis core runs the original single-player game.

1. Build and install using the command in the [developer guide](../DEVELOPMENT.md).
2. Start BizHawk and select File > Open Advanced > Libretro.
3. Select `Libretro/Cores/AladdinCoop/aladdin_coop_libretro.dll` as the core,
   and your supported Aladdin USA ROM as the content.
4. Under Config > Controllers, configure both P1 and P2 RetroPad controls.

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

- F5: save slot 1. F8: load slot 1.
- Enter / controller Start: normal pause during gameplay; native Start
  during interludes.
- P: pause the emulator itself.
- Ctrl+R: restart from the beginning.

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
stages; Ctrl+R clears them. Damage tests disable invincibility.

## Saves and verification

Restart BizHawk after replacing the core DLLs. Use this custom core to load its
co-op saves; stock Genesis cores do not understand the extra player state.
No first-level save is needed to start playing.

Development Python/Lua harnesses require local fixtures and may contain local
reproduction paths. See the project README for test limitations.
A complete two-player campaign playthrough has not yet been verified.

# Implementation notes

## Verified layout for the supplied USA ROM

The header says ALADDIN, MK-1058, USA. ROM size is 2 MiB. Executable gameplay
code lies predominantly around ROM addresses `1A8000` through `1Bxxxx`.
The original cartridge has not been patched.

| Location | Observed role |
| --- | --- |
| FF7DF6 / FF7DF8 | Camera origin X / Y |
| FF7DFA / FF7DFC | Player position relative to camera, with native Y bias |
| FF7DFE / FF7E00 | Camera's desired player position |
| FF7E02 / FF7E04 | Player world X / Y |
| FF7E40 | Original player object; object records are 0x42 bytes |
| FF863E | Final object slot, reserved by the prototype for player two |
| Object +02 / +04 | World X / Y |
| Object +14 | Current graphics frame descriptor |
| Object +1E | Tile attributes, including palette bank |
| Object +20 | Animation bytecode cursor |
| Object +2A / +2E | Sprite allocation bookkeeping / VRAM address |
| FFEFFA | Health |
| FFEFE0..FFEFE1 | Shared apple count, ASCII digits |
| FFF07C onward | Player controls, collision scratch, movement flags |
| FFF155 / FFF156 | Polled control bytes |
| 1A8C16 | Gameplay loop entry |
| 1A8CCA | End of player simulation, before animation/render work |
| 1AA8FA | Camera update |
| 1ADE36 | Object simulation loop |
| 1AC796 | Animation interpreter and graphics upload queue |
| 1AB7C4 | Sprite attribute table construction |

All RAM addresses in Python dumps use normal 68000 byte order; the emulator's
backing RAM is word-swapped on this host.

## Prototype architecture

An explicitly enabled CPU hook keeps separate snapshots of the player globals
and original player object. The second player executes the original simulation
with their own inputs, then the original player context is restored. Enemies
advance once, with the nearer player's context supplied to their logic. The
second player's animation uses a reserved object record and independently
allocated VRAM. Both players retain original palette bank 3. After graphics DMA,
player two's private tiles use the supplied black/brown outfit. The current
animation descriptor supplies original ROM tiles, so older saves recover from
previous destructive recolors. Connected cream/grey/white regions with a broad
white interior identify trousers across sprite-piece boundaries; their folds use
a consistent brown ramp (1 -> 4, 2 -> 5, 12 -> 6, 13 -> 7, 14 -> 5).
Enclosed tan folds also darken. Thin sword highlights and exposed skin retain
their original inks; vest 11 becomes black 15 and red sash 8 becomes brown 4.
This remains a recolor, not new clothing geometry. The derived frame is cached
and written in the core's word-swapped VRAM order, invalidating changed tile-cache
entries. The cache is disposable and adds no save-state fields. Palette RAM and
P1 tiles remain unchanged. No framebuffer compositing or duplicate second game
is involved.

The animation interpreter itself writes some fixed player globals. It must run
under the corresponding player context as well. Duplicating the object without
handling those writes causes the two characters to affect each other's state.

The snapshots are intentionally experimental. Additional global state may need
separation as first-level routes are tested. The final object slot is unavailable
to ordinary spawns while occupied by player two. Sprite/tile capacity and CPU
timing under a completely full scene have not been established for real hardware.

The original code still contains level exit logic and object animation scripts,
including in the first level. An absence of cinematic sequences does not mean
the level has no scripts to adapt.

## Historical first-level MVP checklist

1. Play the entire first level with two people, including the upper/rope routes.
2. Reach the exit through normal gameplay; its paired condition is already
   covered with injected boundary states.
3. Verify pit recovery and hazardous rejoin destinations throughout the level.
   Native checkpoint activation and team respawn are covered with injected
   collision fixtures; full-route checkpoint traversal still needs playtesting.
4. Check camera bounds during uneven vertical movement and at every map edge.
5. Test two physical controllers and sound on the user's setup.
6. If real Genesis compatibility is required, replace emulator hooks with a
   ROM-level implementation and budget RAM, VRAM, sprite count, and CPU time.

Research reference: the Video Game History Foundation's source-code study
describes Aladdin's assembly, Chopper graphics data, and animation scripting:
https://gamehistory.org/aladdin-source-code/

## Shared checkpoints and native HUD

The checkpoint collision handler at 1AE64C (object type 43 hex) calls 1B0490
to store shared player/camera coordinates at FF7E0A..FF7E11. Both simulation
passes can activate it. Once both players have zero health, the next P1 death
call enters the original rebuild at 1A90CA, bypassing the life decrement.
Co-op interception is suspended until the next gameplay loop. P2 is then
reinitialized at P1's restored checkpoint position with a fresh tile allocation.
This retains the native object/map rebuild and checkpoint state in Genesis RAM;
the frontend no longer reloads first-level.state automatically on team death.

At 1AB9BC, the health sprite routine is replayed with P2's health. Its appended
sprites move 160 pixels right; original health and animation cursor are restored.
Execution skips the score renderer to 1ABA0A. The lives HUD is skipped separately.
Co-op snapshot version 2 includes the HUD pass context and the pending native
respawn state. Tests restore during the multi-frame world rebuild and compare
the resulting video, in addition to the adapter and native BizHawk replay tests.

## Exit approach regression

The user's slot 1 had both players at (4724,466), camera X=4444. The global
screen-X cap of 280 blocked the native gate at X>=4744, Y<470 (1B5B4A).
At the right camera boundary the cap is now 304, enough to enter that region
while remaining visible. The original paired exit condition remains unchanged.
The adapter and standalone render a persistent completion panel. Verification
loads the supplied save read-only and uses ordinary controller movement: P1
crossing alone does not finish; P2 crossing does, and completed saves restore.

## Campaign extension

Native stage definitions are 66-byte records at ROM 2C78, IDs 0..12. The
sequence at 4082 includes bonus commands as well as main-stage IDs. The old
completion latch now queues native transition entry at 1A8E5C; level loading
suspends co-op until the main gameplay loop returns. Native exit countdowns are
retained. Later exits require a native request and both players within 128 pixels
on each axis; Agrabah retains its exact paired coordinate gate.

The debug stage selector enters native loading at 1A8ED8 with the selected ID
and its corresponding campaign-sequence cursor. The existing serialized latch
encodes queued stage selection, preserving the size of version 3 extension saves.
Frontend state uses previously reserved header bits for the selector. Legacy
completion headers no longer freeze the adapter. During native interludes, Start
reaches the game instead of opening the debug menu.

Rug Ride (ID 8) needs one shared scroll/script update. P2 skips the native
1A9D18 shared camera/carpet increment and updates only its own flight position.
A reserved visual carpet record shares the native carpet tiles and follows P2;
it is excluded from object simulation and animation execution. The normal
midpoint camera is bypassed in favor of the native autoscroll. Scripted deaths
with nonzero HP now enter co-op death handling, and carpet rescue permits a
living airborne partner. Debug protection bypasses hurt-blink so P1 stays visible.

Campaign reports explicitly distinguish direct stage loads, injected exit/death
tests, native BizHawk checks, and a full normal playthrough (still outstanding).

Desert noclip regression (2026-09-11): flying right at the spawn height froze
gameplay at X3954. The custom camera allowed Y=height-240 (272), whereas native
1AAA08/1AAA0E rejects that value. Column streaming then read row 32 beyond the
32-row Desert map, encountered an odd tile offset at RAM 7286, and entered the
native exception loop at 1B24F8. Clamp noclip camera Y to height-241. The scout's
movement bounds are unchanged. tools/verify_desert_noclip.py checks per-frame
gameplay progress across the map edges, deterministic save replay, and handoff.
The Windows crash report was ntdll 0xc0000028; its connection to the reproduced
native game trap is suspected, not independently established. The user's slot 1
still contained the earlier Agrabah exit state and was preserved.

Rooftops rope regression (2026-09-11, newer slot 1 at 17:18): native stage ID 0
is Agrabah Rooftops; ID 4 is Sultan's Dungeon. Corrected their swapped debug-menu
and test labels. Slot 1 has the first flute flag F12A=FF and pending spawn tag BA
at CEEB, with both players below the first flagpole. The shared camera keeps the
basket in view during flute pickup, so native column/row streaming never retries
its conditional spawn. Scrolling away and back reproduces the native recovery.

At the Rooftops stage-update return (1B5B92), retry one visible, eligible pending
rope through its original 1B70F8..1B71A0 spawn routine. Registers are saved on the
emulated stack and restored by native MOVEM/RTS at 1ADB56. Native allocation,
trigger consumption, animation, and ride behavior remain authoritative. Retry
stops once the native routine consumes the trigger; noclip skips it. F126..F12A
remain shared across player context installations in this stage. Save restoration
merges old player-local flute flags, preserving version 3 compatibility.
tools/verify_rooftop_rope.py uses the extracted user fixture read-only to check
stationary recovery, both players riding, no duplicate, deterministic replay,
no unlock without a flute, and migration of an old P2-only unlock.

Drowning regression (2026-09-11, slot 1 at 17:43): Cave of Wonders, P1 object
type 0 with HP 8, death flag 0, and invincibility enabled. Native water death
1B53B0 sets F0E6=20, removes the primary object and frees its sprite allocation.
The next debug_apply used to restore HP and erase F0E6, leaving an invisible
player. Damage protection now only refreshes living player objects and preserves
scripted deaths. The coordinated death check also treats a removed gameplay
object without an exit request as dead, recovering already affected saves.
verify_drowning.py checks the actual saved ghost, native water collision for
either player with protection on/off, simultaneous drowning/checkpoint recovery,
and deterministic replay of a save taken during the checkpoint rebuild.

Shared object physics (2026-09-11): 1ADB5C is a separate terrain/gravity loop
over slots 1..31. Although co-op limited the earlier object-script update to the
current player on P2's pass, it still ran this shared loop a second time. A
falling 7C object gained 180 velocity units per frame versus native 60 in the
measured sequence (the script applies its own velocity adjustment too). Skip
1ADB5C on P2's pass; retain 1ABB40 player/object collisions for both players.
verify_object_physics.py instantiates six native templates (7C, 7D, two 31
variants, 2F, 2E) and compares 60-frame positions, velocities, facing and contact
flags against co-op-disabled native execution, plus save replay. Bouncing
templates must exhibit both falling and upward velocity. All six match.

Apple HUD/Iago completion (2026-09-11, user save at 18:05 and refreshed 18:07):
the saved Iago defeat has P1 F0E9=FF but a 137-pixel player separation, just past
the generic 128-pixel exit gate. Dedicated Iago/Jafar arenas now accept the native
victory request regardless of separation; normal level exits retain their gate.
The supplied save advances through the original Genie bonus round to Jafar.

Skipping lives drawing at 1AB7E6 left D1 sprite size A00 instead of zero. The
low-ammo blink branch jumps straight to the ones digit, inheriting that size and
displaying adjacent tiles as corrupt digits. Clear D1 size bits when skipping.

Iago's 1B6302/1B632A calls overwrite fixed object slot 1 every 128 ticks and zero
its allocation pointers without freeing the previous six blocks. This occurs
in native execution too but the extra player reduces available sprite memory.
Release the previous allocation before those calls. On restoring old Iago saves,
reclaim orphaned bitmap entries F008..F07B by checking all 32 live object owners.
verify_apples_boss.py covers all low-ammo blink phases, 24 throws by both players,
1024 arena frames without leaked blocks, actual saved victory and bonus replay.


## Original startup, death option and hidden pause cheats

Both frontends now retain a freshly booted core state for reset rather than
loading first-level.state. Normal title Options includes a native-font DEATH row
above Difficulty (selection 6; Up from Difficulty). Hooked wrap/selection/cursor
paths preserve all six original options. The setting occupies debug_flags bit 3,
retained across stage changes and existing version-3 save layouts.

At the paired end-of-update boundary, Partner mode pays once when a safe rescue
can happen; Checkpoint mode pays once when either player dies. Simultaneous
team death is one recovery. Native ASCII lives at 7E3C are shared and their HUD
is restored. A pending checkpoint uses restart=1; exhausted spare lives use
restart=3 to enter native 1A9088 continue/game-over handling. Paid checkpoint
rebuilds enter 1A90CA to avoid a second deduction. Zero is a valid last active
life, following the original game's spare-lives convention.

The frontend initially shows only normal pause. A+B+C (RetroPad bits 0,1,8)
while paused unlocks debug for that pause; resume clears the unlock and waits
for action buttons to release. Header bit 6 serializes the unlock, preserving
existing state size and older saves (which resume as ordinary pause).

Verification: tools/verify_death_options.py covers both policies, either player,
a team wipe, payment once, landing wait, save replay and native continue entry.
bizhawk/verify_normal_options.py covers cold boot, native option navigation,
choice persistence, ABC gating, paused saves and reset. Co-op, drowning and
apple/boss regressions also pass with the restored lives HUD.


## Enemy animation targeting and visible death recovery

Nearest living player selection now covers both object movement (1ADE5E to
1AE0A6) and animation callbacks (1AC7DC to 1AC846). Enemy attacks can branch
inside the animation interpreter; previously those branches saw only P1 even
when movement had selected P2. enemy_second=2 distinguishes an animation-context
swap in version-3 saves. The target distance includes both world coordinates,
and zero-health players are excluded while a living partner exists.

Death recovery waits 60 simulation frames. A fatal hit uses the original hit
frames, holds the final stagger pose from frame 20, and hides the defeated body
from frame 40 until recovery. Water retains its native splash object animation.
This is an in-world co-op presentation rather than the original full-screen
single-player death interlude. Dead controls and manual rejoin are blocked.
The timer uses byte 0 in each player snapshot's RAM buffer, outside all RAM
ranges installed into the emulated game; existing states initialize it to zero.
It resets on recovery/new-stage initialization and survives mid-death saves.
Payment still occurs once when the selected recovery can actually happen.

Verification: verify_enemy_death.py compares actual Agrabah guard attack frames
and damage against P1/P2, checks fatal-hit poses and blocked premature rejoin,
and replays mid-death saves through a single life deduction. Death-policy,
drowning, native object-physics, apple/boss, co-op, campaign and normal-options
checks pass. Direct stage checks do not constitute a full campaign playthrough.


## Teleport pickup effects and paler P2 skin

Genie (1AF2B0) and Abu (1AF2FA) pickup handlers share sound 64 and movement
script 121618, which emits the sparkle template at 1B7B5C. Successful partner
teleports now spawn four of those native sparkle objects around the arrival.
Native animation 122F80 advances and frees them normally. Rejoin, paid partner
revival, and noclip handoff all schedule the same effect. No pickup reward or
bonus flags execute. Full object pools gracefully omit particles.

Snapshot RAM byte 1 in P1 queues sound, outside installed gameplay ranges.
At the next primary 1A8C20 boundary, a saved-register trampoline invokes the
original sound-only tail 1AF2D6, which respects the native SFX option. All call
state is on the emulated stack, so mid-call saves remain compatible. The sound
is coalesced for simultaneous arrivals, and failed/held-button teleports do not
retrigger it. Ordinary checkpoint loading is not an Aladdin-to-Aladdin teleport.

Outside classified trouser regions, P2 skin inks 1/3 now become white 14 and
2/4 become cream 1. Darker outlines remain. Cloth shading, black vest and brown
sash mappings remain separate; P1 and palette RAM are unchanged.

verify_teleport_effects.py covers both manual directions, paid rescue, noclip,
refusal, native SFX mute, held-button suppression, mid-effect save replay, no
pickup rewards, and allocation cleanup across 20 teleports. Enemy/death, co-op,
normal-options and apple/boss regressions pass.


P2 skin refinement: pure-white skin highlights were too harsh against the dark
shadows. Non-cloth skin now shifts 3 -> 2 and 4 -> 3, retaining original 1/2
highlights and deeper outlines. This is a moderate warm lightening, with no
white substitution in the skin. The ROM-derived recolor also corrects old saves.


## Consistent outfit materials across poses

The former enclosed-tan heuristic was incorrect: tan patches inside the trousers
are exposed knees, not fabric folds. It recolored the same skin differently
between standing and climbing. Skin inks 3/4 now always use the same 2/3 ramp,
including knee patches. Cloth connectivity only follows cream/tan/white inks
1/2/14; grey inks 12/13 are recolored only along its immediate border, avoiding
flood-fill propagation into adjoining sword/climbing details. Vest ink 11 now
uses charcoal 13 while original black 15 remains the outline, preserving the
vest shape in large back-facing climbing frames instead of a flat black mass.

Verified standing and rope previews and 61,279 skin/vest pixels across 30 distinct
animation frames (movement, attack, jump and rope poses) with
verify_outfit_materials.py. Teleport effect/replay/allocation checks also pass.


Small trouser-fragment follow-up: the broad-interior minimum rejected isolated
white knee/cuff folds during movement. A second pass now includes white regions
with cream/tan edging, within eight pixels of established trousers and no more
than three pixels above their top. Secondary regions do not seed further growth,
so this cannot propagate recursively into the face. Grey outlines remain local.
Compared old/new native output over 500 movement/crouch/attack updates: 14 distinct
frame descriptors contained corrected white fragments. The outfit regression
now explicitly checks all 19 missed white pixels in walking frame 1EA3C2 become
brown, while white sword highlights remain. Skin/vest and teleport checks pass.


## Retracted window hands detect P2

The native window-hand template 1B7C88 begins as non-colliding type 84, with
animation 123D34. Its FD proximity opcode checks the active player's world X
against a 64-pixel band; only after this check does the animation switch the
object to attacking type 0E. The generic target filter accepted types below 7F,
so it never installed P2 during the dormant hand's proximity check.

The targeting whitelist now includes type 84/0E specifically within the hand's
123D34..123DE2 animation program. Player selection prefers a living player inside
the native horizontal trigger band. Other decorative/effect objects remain
excluded. Movement and animation still run once per shared object.

verify_window_hands.py uses the native hidden-hand template and demonstrates
that the installed pre-fix core activates for P1 but fails for P2. The new core
activates for either with identical 240-frame attack timelines, refuses players
outside the trigger band, and replays saves deterministically. Guard/death and
native barrel/stone physics regression checks also pass.

Window trigger follow-up: actual September 11 20:25 QuickSave1 has hidden type84 knife throwers at 8260/8326/8368, animation12320E. Prior hand fix only covered123D34 family. Added123200..123274 family (84/06) to targeting and its native FD30 horizontal range48, retaining64 for original hands. Reproduced no activation over600frames before fix; actual save now activates8326 above P2 within180frames with deterministic replay. verify_window_hands.py, verify_enemy_death.py, verify_object_physics.py pass. Installed updated core; restart emulator required.


## September 13 checklist fixes

- P2 hurt blinking now checks its own saved F0F2 timer at renderer entry. The
  native check at 1ABA14 only applies to the first object. Debug protection
  still suppresses blinking for both players.
- Sprite drawing visits objects 0,31,1..30 using the native DBRA counter at
  1ABA20. Both players precede world sprites in the SAT priority chain. Changing
  only the loop epilogue is unsafe: native skip branches bypass that hook.
  Simulation order and VRAM allocation remain unchanged.
- Abu bonus stages 2/6 use a separate P2 tile remap, darkening tan inks 1..6 by
  one step and preserving the other inks. Tiles still originate from ROM, so
  loading old recolored saves cannot compound the darkening.
- Camera separation and midpoint rules only apply when both players are alive.
  If P1 dies, native scrolling temporarily receives P2's coordinates, then
  restores P1's real coordinates. Dead P2 imposes no limits on P1. Both dead
  freezes scroll until existing team recovery. Paid respawn timing is unchanged.
- Rug Ride F10B is a shared scripted duck cue. P2's free-ride animation loop
  122336 is normalized to the stage loop 122350, which branches into ducking.
- Genie slot-machine input reads at 1B190E and 1B1954 include A/B/C from both
  frontend pads. The native debounce, token deduction, timing and rewards run
  unchanged. This works outside the gameplay-ready state.
- Trampoline families 01,4E,4F and 65/66 keep shared recoil animations but use
  individual cooldowns. Hidden type84 recoil sprites remain collision candidates
  for the other player and dispatch the original launch routine. Native observed
  recoil durations are 23/19/35/19 frames from a forced animation start; per-player
  counters initialize to 24/20/36/20 and decrement at paired update completion.
  Saved metadata at player RAM 0200..02FF records cooldown, object position and
  family by slot, and resets on stage creation. It is outside installed ranges,
  so state version/size stays unchanged. Both player orders, immediate same-player
  blocking, expiration, all four spring families and saved replay are tested.

Verification: tools/verify_a_fixes.py covers all seven reported items (Genie
fixture is local diagnostics/task-a-slot.core/.extra). Enemy/death, all 13 stage
loads, outfit materials, object physics, death options and teleport checks pass.
The tests do not replace a full normal two-player campaign playthrough.

## Escape slope separation regression

Reproduced from a fresh stage 7 load with either player holding Right while the
other stays on the starting ledge at world (55,391). Once the leader descends
more than 120 pixels, the previous camera hook classified the idle player's
zero vertical velocity as ascent and assigned Y=partnerY-120. This forced the
idle player through the solid slope. It was a position clamp, not corrupted tiles.

The vertical limit now requires an airborne, rising player (negative velocity,
F0BE set and F0C0 clear). Its correction cannot move the player below their
previous world Y, so attempting a jump when already beyond the separation band
also cannot snap through the ledge. The change applies to normal platform stages.

verify_escape_separation.py verifies both leaders, 100-frame idle ground
stability, jumping while separated, and deterministic save replay. The seven
September 13 checklist checks, death policies, and all 13 stage load checks pass.
Updated standalone build and installed BizHawk core; restart required.


## Rope, look-up, optional flute, palace passage and scripted carpet fixes

- Horizontal-rope animation at 1A99F0 uses F16A as a 40-step phase counter.
  Capture/install it per player so two moving climbers do not advance one phase
  twice. Tests compare each player's solo and simultaneous timelines; the initial
  idle poses can differ but movement phases match.
- Either player's settled F0DF look-up pose can raise the native camera target
  7E00. The primary pass temporarily uses the larger requested target, preserving
  P1's own target in snapshot metadata 2..4 and restoring it at 1A8CA2. Releasing
  P2 Up therefore cannot latch P1 into permanent look-up scrolling.
- Rooftops optional flute 4B (native spawner 1B70B0, pickup 1AF060) sets shared
  F116. This differs from the five ordinary flute rope flags F126..12A. The native
  snake movement at 12070E now sees P2's pickup even when P1 rides. Its tested
  branch advances to 1207A0 with the flute versus 12073C without it.
- Palace QS1 had P2 F11C=FF but P1 F11C=0, plus the stationary type5F carpet
  from map tag82 still covering the passage at (2925,596). Share the key flag
  in stage10 and merge either context when restoring old saves. Native spawner
  1B68D6 suppresses that carpet after the key, but only on map streaming. At
  animation entry, an already-loaded type5F/tag82 instance is retired with native
  1ABE6E cleanup and returns to the normal 1AC846 loop. No terrain is fabricated
  or removed. The reported save now lets P2 descend, and native key pickups by
  either player also retire the carpet while the camera remains nearby.
- Scripted carpets use shared destination F094/F096. Their invisible type84
  route controllers now get the rider's player context when reciprocally linked
  to native carpet types 5E/60/61. Prefer a player already standing on the carpet
  over another nearby player. The same native paired carpet/controller scripts
  follow identical paths for P1/P2 boarding and keep the rider aboard.

Verification: tools/verify_rope_camera_scripts.py covers all five issues, native
pickups, release of look-up, and deterministic carpet/passage save replay. It
requires the local blocked-cage.core/.extra fixture extracted from the user's
QS1; those files and screenshots are excluded from Git. verify_a_fixes,
verify_escape_separation, verify_campaign, verify_object_physics and
verify_death_options also pass. This is targeted native-script testing and stage
loading, not a complete campaign playthrough.


## P2 reversed outfit colors

P2 now uses native violet ink 11 for classified trouser interiors and white
ink 14 for the original vest ink 11. Dark trouser borders retain ink 15.
Skin, sword highlights, and the bonus-stage Abu remap are preserved.
verify_outfit_materials.py passes across 30 animation frames and 61,279
skin/vest pixels, including the previously reported isolated walking folds.


## Player pieces missing behind lamp meters

Reproduced both players overlapping the top HUD. Two native full lamp meters
can exceed the Genesis 20-sprite scanline limit even before player sprites;
combined player poses can also exceed the 320-pixel sprite budget. The Mode 5
renderer now uses its existing expanded 80-sprite/2560-pixel capacity while
co-op is enabled and ready. Outside active co-op it retains configured limits.
Native HUD art, sprite order, masking, palette and health animation are unchanged.
Simply combining adjacent smoke sprites was insufficient because it did not
resolve pixel-budget overflow; no such HUD compaction remains in the build.
verify_lamp_sprites.py exercises top-HUD overlap at health 1..8 and confirms
that native limits are exceeded by the fixture, expanded capacity is sufficient,
and disabling co-op disables the override. Appearance and checklist tests pass.


## P2 red and blue outfit

Requested outfit now uses native red ink 8 for the classified trouser regions
and blue ink 9 for the original vest ink. Skin, hair, sword highlights and the
bonus-stage Abu remap are unchanged. Appearance verification retains the
walking-fold and skin consistency checks with the updated clothing colors.


## Expanded sprite-art audit and material fixes

The red/blue remap flattened cream fold shadows into the trouser base color.
Ink2 fold shadows and ink13 cloth borders now use dark red ink7, while the red
interior remains ink8. Small cream-edged white fabric components (at least four
white pixels, two warm pixels and a 2x2 interior) count as cloth even when they
fall below the old 16-white-pixel threshold. This catches bent-leg fragments.

Native purple ink11 is shared by vest panels and thin sword edges. Connected
regions with a broad interior or a skin neighbor map to blue; isolated thin
edges retain the native purple shadow. This avoids applying the vest color to
all sword details. The Genie's portion of composite descriptor1E8034 preserves
its original inks. Pure teleport-effect descriptors1ED230..1ED2E4 bypass clothing
recoloring; the previous broad-white rule had turned the final flash red.
Exposed knees remain skin, as in the original art.

`tools/audit_sprite_art.py` decodes 279 Aladdin descriptors and body fragments
from1E8034 through1EE088. Side-by-side native/P2 contact sheets were inspected.
It checks560,064 pixels for preserved transparency, allocation guards, and
repeatable reconstruction after overwriting the destination with stale tiles.
Pure teleport frames additionally must match native ROM bytes exactly. The
probe-only recolor export exercises the production path, including its cache.
The generated sheets and JSON report are local diagnostics, excluded from Git.

`tools/verify_world_sprite_tiles.py` runs240 frames in each of13 stages and
compares stable P1/world uploads against original ROM graphics:15,400 complete
sprite comparisons passed. This covers sampled native world objects, not every
possible world-object animation or every path through the campaign.

Also passed: outfit material checks, lamp scanline checks, checklist regressions,
rope/camera/flute/palace/carpet checks, Escape separation, campaign stage loads,
enemy/death, object physics, death policies, teleport effects, drowning,
Desert no-clip, window hands, and Rooftops ropes. No full campaign playthrough
or claim that all possible sprite bugs are eliminated.


## Reported face shadows and trouser patches

The previous broad audit verified uploads, transparency, and memory safety; it
was not a semantic pixel oracle. The two supplied close-ups exposed mistakes it
could not detect. Tiny purple components adjacent to skin were incorrectly
classified as blue vest panels. Vest classification now requires either a broad
interior or at least four connected pixels with three skin-adjacent edges.
One- and three-pixel facial shadows retain their original dark ink.

At the user's request, small warm islands enclosed inside trousers now become
red cloth. Components must be disconnected from the transparent exterior,
contain at most64 pixels, and touch fabric on at least4 edges. Large body regions
and exposed limbs remain skin. Immediate cream rims of these filled islands are
also red, so removing the yellow patch does not leave a dotted dark outline.
This supersedes the earlier decision to preserve every enclosed knee patch.

verify_reported_materials.py checks hand-labelled coordinates in1EC114 (standing)
and1EC27C (apple toss), plus nearby face/hand/foot colors, and renders enlarged
previews of six related poses. The existing broad material test now permits red
inside formerly skin-colored trouser islands; the targeted landmarks ensure it
is not accepting red on the face or exposed hands/feet. Re-ran the279-frame
transparency, allocation-guard and stale-VRAM audit as well.


## Idle apple and original fold comparison

Cream ink1 trouser strokes previously mapped to the red base ink8, erasing
fold contours. They now use dark red7, alongside the existing ink2 shadow
mapping. Filled warm patches and their rims remain red as previously requested.
The vest and facial-shadow classification is unchanged.

Native red ink8 outside cloth remains red instead of mapping to skin ink4.
The four pure idle-apple tiles at ROM AD9A0..ADA00 retain every original ink,
including highlight ink4. Descriptor1EC5DC packs the descending apple into a
body tile; preserve its small apple rectangle at x144..148,y93..97. The caught
apple uses red8 while the surrounding hand retains P2's skin mapping.

verify_idle_apple_folds.py checks all8 idle-apple poses and320 restored dark-red
fold pixels. The102 face/trouser/limb landmarks,30-frame material check and
279-frame transparency/VRAM/stale-tile audit also pass. A native/P2 comparison
is saved locally at diagnostics/idle-apple-fold-comparison.png.


## Darker blue vest and restored trouser patch

P2 vest panels now use native blue ink10 instead of the lighter ink9. Facial
shadows still retain ink11. At the user's request, the enclosed tan patch and
its cream rim now retain their original ROM inks rather than being filled red.
This uses the existing bounded patch mask, retaining red fold strokes elsewhere
and preserving the idle apple fixes. The reported-pose tests now require native
patch colors and the darker blue vest, alongside unchanged face/hand/foot checks.

Patch restoration is limited to enclosed islands centered in the lower half
of the detected trousers; upper waistband fold islands remain red. This avoids
restoring the previously reported yellow waistband marks along with the knee.


## Complete patch shape, warm fold leaks and narrow vest pieces

The prior enclosed-island heuristic split the patch's cream interior from its
tan border and missed warm fold chains connected to the waistband. Replace it
with per-row fabric bounds, extended through contiguous native warm strokes.
Warm colors inside that silhouette are fabric. Compact lower-trouser tan-pixel
clusters define the patch; restore the full cream/tan row span around each
cluster, including interior pixels, instead of only its seed colors. Warm
strokes outside the patch use dark red, preserving the original fold geometry.

Narrow purple regions can join nearby established vest panels only when they
have no silver edge or dense skin/hair neighborhood. This recovery stays within
two pixels and does not spread above the vest. Native torso pieces at7D780 and
93880 have separately identified vest ink, so their thin front/back panels use
blue10 without relying on a broad-area threshold. Head and sword shadows retain
their existing protection; idle apple tiles still retain native colors.

New verify_material_regions.py checks13 idle poses:247 complete patch pixels,
430 warm fold pixels above the patch, and87 narrow vest pixels. These checks
include the patch interior missed by the earlier landmark tests. Also pass:
reported material landmarks,30-frame material checks, all8 idle apple poses,
279-frame transparency/VRAM/stale-tile audit, teleport effects and checklist
regressions. Contact sheets remain a visual aid, not a complete semantic oracle
for every possible pose; the explicit regression claims apply to these fixtures.

Coal flames (2026-09-13): the native 8C -> 7B delayed flame was shared,
so a runner could reach their partner's armed flame even while moving. Track
its triggering player in snapshot metadata 0300..031F, clear ownership when
native 1AE30A initializes a reused slot, and stamp it at coal spawn 1B535A.
At 1B5332, search for this player's pending flame instead of the game's single
shared pending 8C. At 1AE9D4, only that player receives its damage. Original
arming, animation, health loss, and stationary-coal behavior remain native.
Metadata is cleared on stage initialization and uses the existing save layout.
verify_coals.py covers either runner leading, both stopping, either stopping
alone, and save/replay. Vertical-rope descriptors 1E6AE6..1E6D50 are now included
in the sprite-art audit; the reported stray blue pixel still needs an exact
pose/location before a further recolor change.

Vertical-rope white fragments (2026-09-13): the supplied climbing screenshot
identified isolated cream/white cuff and fold pixels missed by connected-region
classification. For the eight native vertical-rope descriptors 1E6AE6..1E6D50,
map native inks 1/2/14 below the waist (Y>=114) to the trouser ramp. Native skin
uses 3..7 here, and the hanging sword uses 12/13. Comparing the new core with
the installed predecessor showed exactly ten changed pixels in five poses;
every other pixel in all eight poses was identical. verify_climbing_cloth.py
checks 2,114 fabric pixels, 479 retained steel pixels and all ten landmarks.
Coals, idle material regions, bending patches and the 287-frame audit pass.

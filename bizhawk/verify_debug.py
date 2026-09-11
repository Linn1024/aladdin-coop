"""Drive the actual pause menu through RetroPad inputs, then inspect engine state."""
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import probe
probe.CORE=Path(__file__).resolve().parent/'aladdin_coop_libretro.dll'
from probe import *
p=Probe();c=C.CDLL(str(ROOT/'bizhawk/aladdin_engine.dll'))
c.al_probe_player.restype=C.c_void_p
c.retro_get_memory_data.restype=C.c_void_p
p.ram_ptr=c.retro_get_memory_data(2)
def tick():
    s=(C.c_uint*7)();c.al_coop_status(s);return list(s)
def hp():
    d=(C.c_uint*6)();c.al_coop_details(d);return list(d)[:2]
def tap(button,who=0):
    if who:p.buttons[1]={button};p.run();p.buttons[1]=set();p.run()
    else:p.run(1,{button});p.run()
def choose(n):
    # Selection persists while this menu is open; tests reset to zero explicitly.
    global selected
    while selected!=n:tap(5);selected=(selected+1)%10
    tap(8)
def resume():tap(3)

p.run(20);selected=0;before=tick();tap(3);p.run(60)
assert tick()==before,'World advanced while debug pause was open'
p.screenshot(ROOT/'bizhawk/debug-menu.png')
choose(1);assert c.al_coop_debug_flags()==1
choose(2);assert c.al_coop_debug_flags()==3
state=p.save();choose(1);assert c.al_coop_debug_flags()==2
p.restore(state);selected=2;assert c.al_coop_debug_flags()==3
frozen=tick();p.run(30);assert tick()==frozen,'Paused save did not restore pause'
resume();p.run(120);assert hp()==[8,8] and p.ram()[0xefe0:0xefe2]==b'99'
# Simulate damage in both contexts; protection restores both on the next loop.
p.write(0xeffa,b'\x02');C.c_ubyte.from_address(c.al_probe_player(1)+0xeffa).value=3
p.run(2);assert hp()==[8,8]
tap(3);choose(6);assert c.al_coop_debug_flags()==2
assert hp()==[8,8],'Queued damage executed while paused'
resume();p.run(2);assert hp()==[7,8]
tap(3);choose(7);resume();p.run(2);assert hp()==[7,7]
tap(3);choose(3);queued=p.save();resume();p.run(2);assert hp()==[8,8]
p.restore(queued);assert hp()==[7,7];resume();p.run(2);assert hp()==[8,8]
# Move to a new grounded location, then set a shared debug checkpoint there.
p.run(25,{7});p.run(30);x=tick()[3];assert x>103
tap(3);choose(4);resume();p.run(2)
ram=p.ram();assert int.from_bytes(ram[0x7e0a:0x7e0c],'big')+int.from_bytes(ram[0x7e0e:0x7e10],'big')==x
tap(3);choose(5);resume();p.run(110)
s=tick();assert s[3]==s[5]==x and hp()==[8,8],(s,hp())
# P2 can open/control the menu. Holding Start must not repeatedly toggle it.
before=tick();p.buttons[1]={3};p.run(20);p.buttons[1]=set();p.run()
assert tick()==before
tap(3,1);p.run(2);assert tick()[1]>before[1]
# Checkpoint command refuses an airborne P1.
p.run(10,{8});assert not c.al_coop_debug(4)
p.core.retro_reset();p.run(10);assert c.al_coop_debug_flags()==0
tap(3);before=tick();p.run(20,{8})
assert tick()==before,'Held resume button advanced gameplay before release'
p.run();p.run(5);assert tick()[4]==before[4],'Resume caused an accidental jump'
report={'pause_freezes_world':True,'toggles_and_pause_saved':True,
 'invincibility_and_apples':True,'independent_damage_and_heal':True,
 'debug_checkpoint_and_team_respawn':True,'p2_menu_controls':True,
 'held_start_edge_triggered':True,'resume_jump_suppressed':True,
 'queued_action_saved':True,'airborne_checkpoint_refused':True,'reset_clears_cheats':True}
(ROOT/'bizhawk/debug-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
p.core.retro_unload_game();p.core.retro_deinit()

"""Noclip menu, camera, state replay, and two-player handoff against the ROM."""
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import probe
probe.CORE=Path(__file__).resolve().parent/'aladdin_coop_libretro.dll'
from probe import *
p=Probe();c=C.CDLL(str(ROOT/'bizhawk/aladdin_engine.dll'))
c.retro_get_memory_data.restype=C.c_void_p;p.ram_ptr=c.retro_get_memory_data(2)
def status():
    s=(C.c_uint*7)();c.al_coop_status(s);return list(s)
def health():
    d=(C.c_uint*6)();c.al_coop_details(d);return list(d)[:2]
def tap(b):p.run(1,{b});p.run()
p.run(10);start=status();hp=health()
tap(3);tap(4);tap(4);tap(8) # Wrap up past Stage to Noclip.
assert c.al_coop_debug_flags()&4
p.screenshot(ROOT/'bizhawk/noclip-menu.png')
paused=p.save();tap(3);p.run(100,{7});s=status()
assert s[3]==start[3]+400 and s[5:]==start[5:] and s[1]>start[1]
assert p.ram()[0x863e]==0x83,'Waiting P2 must retain its sprite allocation'
cam=int.from_bytes(p.ram()[0x7df6:0x7df8],'big');assert 100<s[3]-cam<260
assert health()==hp
p.run(100,{4});s=status();assert s[4]==start[4]-400
p.screenshot(ROOT/'bizhawk/noclip-flight.png')
flying=p.save()
def replay():
    p.run(100,{7});p.run(40,{5});return status(),hashlib.sha256(p.frame[0]).hexdigest()
a=replay();p.restore(flying);b=replay();assert a==b
# Save after switching OFF but before resuming, then verify the queued handoff.
tap(3);tap(8);assert not c.al_coop_debug_flags()&4
queued=p.save();target=status()[3:5]
def handoff():
    tap(3);p.run();s=status()
    assert s[3:5]==s[5:7]==target,(s,target)
    assert health()==hp
    p.run(100);s=status();assert s[3:5]==s[5:7]
    return hashlib.sha256(p.frame[0]).hexdigest()
a=handoff();p.restore(queued);b=handoff();assert a==b
p.screenshot(ROOT/'bizhawk/noclip-handoff.png')
before=status();p.run(15,{7});after=status()
assert after[3]>before[3] and after[5]==before[5],'Independent movement did not resume'
# All four directions cross terrain, but the scout stays inside map bounds.
p.restore(flying);p.run(1500,{7});p.run(400,{5});s=status();r=p.ram()
assert s[3]==int.from_bytes(r[0x7db8:0x7dba],'big')-32
assert s[4]==int.from_bytes(r[0x7dbc:0x7dbe],'big')+240
p.run(1500,{6});p.run(400,{4});assert status()[3:5]==[16,288]
p.restore(paused);assert c.al_coop_debug_flags()&4
before=status();p.run(30);assert status()==before
p.core.retro_reset();p.run(10);assert c.al_coop_debug_flags()==0
report={'menu_toggle':True,'four_direction_flight':True,'camera_follows_scout':True,
 'p2_waits_hidden':True,'health_preserved':True,'flight_save_replay_matches':True,
 'queued_handoff_save_replay_matches':True,'both_placed_at_scout':True,
 'normal_movement_resumes':True,'map_bounds':True,'paused_noclip_state_restored':True}
(ROOT/'bizhawk/noclip-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
p.core.retro_unload_game();p.core.retro_deinit()

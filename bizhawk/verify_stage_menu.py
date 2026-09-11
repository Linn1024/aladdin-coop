"""Exercise the stage selector, including saving a queued stage load."""
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import probe
probe.CORE=Path(__file__).resolve().parent/'aladdin_coop_libretro.dll'
from probe import *
p=Probe();c=C.CDLL(str(ROOT/'bizhawk/aladdin_engine.dll'))
def tap(b):p.run(1,{b});p.run()
p.run(20);tap(3);tap(4);tap(7);tap(7);tap(8)
assert c.al_coop_level()==1 and c.al_coop_transition_pending()==5
p.screenshot(ROOT/'bizhawk/stage-selector.png');queued=p.save()
def load():
    tap(3)
    for n in range(2000):
        p.run(1,{3} if not c.al_coop_ready() and n%90==0 else set())
        if c.al_coop_ready() and c.al_coop_level()==3:break
    else:raise AssertionError('Stage selector failed to load Desert')
    p.buttons[1]={7};p.run(20);p.buttons[1]=set()
    return hashlib.sha256(p.frame[0]).hexdigest()
a=load();p.screenshot(ROOT/'bizhawk/campaign-desert.png')
p.restore(queued);b=load();assert a==b
assert not c.al_coop_debug_stage(13)
(ROOT/'bizhawk/stage-menu-verification.json').write_text(json.dumps({
 'controller_stage_selection':True,'queued_load_saved':True,'load_replay_matches':True,
 'invalid_stage_rejected':True
},indent=2)+'\n')
print('PASS: Stage selector and queued-load save replay')
p.core.retro_unload_game();p.core.retro_deinit()

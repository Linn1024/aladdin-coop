"""Reproduce the blocked exit from the user's unmodified quick-save slot 1."""
import sys,struct,zipfile,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import probe
probe.CORE=Path(__file__).resolve().parent/'aladdin_coop_libretro.dll'
from probe import *
source=Path(r'C:\TEMP2\Bizhawk\Libretro\State\aladdin_coop_libretro\Aladdin_(U)_[!].QuickSave1.State')
original=source.read_bytes();source_hash=hashlib.sha256(original).hexdigest()
with zipfile.ZipFile(source) as z:raw=z.read('Core.bin')
size=struct.unpack_from('<I',raw)[0];state=raw[4:4+size]
p=Probe();c=C.CDLL(str(ROOT/'bizhawk/aladdin_engine.dll'))
def status():
    s=(C.c_uint*7)();d=(C.c_uint*6)();c.al_coop_status(s);c.al_coop_details(d)
    return list(s),list(d)
p.restore(state);s,d=status();assert s[3:]==[4724,466,4724,466] and not d[5]
p.run(60,{7});s,d=status()
assert s[3]>=4744 and s[5]==4724 and not d[5],(s,d)
p.buttons[1]={7};p.run(20)
p.buttons[1]=set();transition=p.save()
assert not c.al_coop_ready()
def finish():
    for n in range(1800):
        p.run(1,{3} if n%90==0 else set())
        if c.al_coop_ready() and c.al_coop_level()==3:break
    else:raise AssertionError('Desert did not load')
    p.run(10);s,d=status();assert d[:2]==[8,8] and s[3:5]==s[5:7]
    return hashlib.sha256(p.frame[0]).hexdigest()
a=finish();p.screenshot(ROOT/'bizhawk/verified-user-exit.png')
p.restore(transition);b=finish();assert a==b
p.core.retro_reset();p.run(10);assert c.al_coop_level()==1
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash,'User save was modified'
report={'source_save_sha256':source_hash,'source_save_unchanged':True,
 'exit_reached_with_normal_movement':True,'waits_for_both_players':True,
 'desert_loaded_with_two_players':True,'mid_transition_save_replays':True,'reset_works':True}
(ROOT/'bizhawk/exit-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
p.core.retro_unload_game();p.core.retro_deinit()

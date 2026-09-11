"""Boot, original Options row, hidden pause cheats, and frontend state replay."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import probe
probe.CORE=Path(__file__).resolve().parent/'aladdin_coop_libretro.dll'
from probe import *
p=Probe();c=C.CDLL(str(ROOT/'bizhawk/aladdin_engine.dll'))
c.retro_get_memory_data.restype=C.c_void_p;p.ram_ptr=c.retro_get_memory_data(2)
def tap(button):p.run(1,{button});p.run(2)
def flags():return c.al_coop_debug_flags()
def menu_state():return int.from_bytes(p.save()[28:32],'little')
p.run(300);assert not c.al_coop_ready();tap(3);p.run(180)
p.screenshot(ROOT/'diagnostics/verified-title.png')
tap(5);tap(3);p.run(90);tap(4);assert p.ram()[0xf13c:0xf13e]==b'\0\6'
tap(8);assert flags()==8
p.screenshot(ROOT/'diagnostics/death-normal-options.png')
option_save=p.save();tap(8);assert flags()==0;p.restore(option_save);assert flags()==8
# Navigate around the extended list and exercise an unchanged original option.
tap(5);assert p.ram()[0xf13c:0xf13e]==b'\0\0'
before=p.ram()[0x7e21];tap(8);assert p.ram()[0x7e21]==(before+1)%3;tap(8);tap(8)
tap(3);p.run(90);tap(4);tap(3)
for n in range(2000):
 p.run(1,{3} if n%150==0 else set())
 if c.al_coop_ready():break
assert c.al_coop_ready() and flags()==8
p.run(30);tap(3);normal=menu_state();assert normal&1 and not normal&64
frozen=p.ram();p.run(20);assert p.ram()==frozen
p.screenshot(ROOT/'diagnostics/normal-pause.png')
tap(5);tap(8);assert menu_state()&1 and flags()==8,'Normal pause exposed cheats'
p.run(1,{0,1});p.run(2);assert not menu_state()&64
p.run(1,{0,1,8});p.run(2);assert menu_state()&64
p.screenshot(ROOT/'diagnostics/hidden-debug.png')
saved=p.save();tap(5);tap(8);assert flags()==9
p.restore(saved);assert flags()==8 and menu_state()&64
# Resuming re-locks cheats, and holding the chord does not leak an attack/jump.
p.run(1,{3,0,1,8});p.run(10,{0,1,8});assert p.ram()==frozen
p.run(3);tap(3);assert menu_state()&1 and not menu_state()&64
p.core.retro_reset();p.run(3);assert not c.al_coop_ready() and flags()==0
print('PASS: ROM boot, native Options and setting persistence, normal pause, ABC unlock, paused save/replay, clean resume and reset')

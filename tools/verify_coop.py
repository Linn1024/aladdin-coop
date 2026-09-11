"""Behavioral checks against the real ROM and experimental emulator core."""
from probe import *
import json
import subprocess

p = Probe()
seed = (ROOT/'first-level.state').read_bytes()
results = []

def fresh():
    p.core.al_coop_enable(0)
    p.restore(seed)
    p.core.al_coop_enable(1)
    step(5)

def step(n=1, one=0, two=0):
    for _ in range(n):
        p.core.al_coop_buttons(0,one)
        p.core.al_coop_buttons(1,two)
        p.run()

def status():
    s=(C.c_uint*7)();d=(C.c_uint*6)()
    p.core.al_coop_status(s);p.core.al_coop_details(d)
    return list(s),list(d)

def passed(name):
    results.append(name)
    print('PASS:',name,flush=True)

fresh();start,_=status();step(25,two=1<<7);moved,_=status()
assert moved[3]==start[3] and moved[5]>start[5]+50
passed('Player two moves independently')
fresh();start,_=status();step(25,one=1<<7);moved,_=status()
assert moved[5]==start[5] and moved[3]>start[3]+50
passed('Player one moves independently')

for who in (0,1):
    fresh();start,_=status()
    step(20,one=(1<<8) if who==0 else 0,two=(1<<8) if who==1 else 0)
    jumped,_=status()
    assert jumped[4+who*2]<start[4+who*2]-30
    assert jumped[6-who*2]==start[6-who*2]
    step(65);landed,_=status();assert landed[4+who*2]==start[4+who*2]
passed('Both players jump and land independently')

fresh();step(400,two=1<<7);s,_=status()
camera=int.from_bytes(p.ram()[0x7df6:0x7df8],'big')
assert 24<=s[3]-camera<=288 and 24<=s[5]-camera<=288
assert abs(s[5]-s[3])<=240
p.screenshot(ROOT/'diagnostics/verified-camera.png')
passed('Separation stops the leading player and keeps both visible')

for who in (0,1):
    fresh();step(25,two=1<<7);step(35)
    step(3,one=(1<<10) if who==0 else 0,two=(1<<10) if who==1 else 0)
    s,d=status();assert s[3]==s[5] and s[4]==s[6] and d[2+who]==1
    assert d[0:2]==[8,8]
passed('Rejoin works in both directions, triggers once per press, and preserves health')

fresh();step(15,one=1<<8);step(1,one=1<<8,two=1<<10)
_,d=status();assert d[3]==0
passed('Rejoin refuses an airborne destination')

fresh();step(15,two=1<<1);step(30)
assert p.ram()[0xefe0:0xefe2]==b'09'
passed('Player two throws an apple from shared inventory')

fresh();step(120);ram=p.ram();slot=0x7e40+31*66
assert ram[0x7e40]==ram[slot]==0x83
assert int.from_bytes(ram[0x7e5e:0x7e60],'big')&0x6000==0x6000
assert int.from_bytes(ram[slot+0x1e:slot+0x20],'big')&0x6000==0x6000
assert ram[0x7e6e:0x7e72]!=ram[slot+0x2e:slot+0x32]
p.core.al_probe_vram.restype=C.c_void_p
vram=C.string_at(p.core.al_probe_vram(),65536)
def has_purple(a):
    start=int.from_bytes(ram[a+0x2e:a+0x32],'big')
    tiles=vram[start:start+(ram[a+0x29]+1)*128]
    return any((v&15)==11 or (v>>4)==11 for v in tiles)
assert has_purple(0x7e40) and not has_purple(slot)
p.screenshot(ROOT/'diagnostics/verified-two-players.png')
passed('P1 colors retained; P2 private tiles use pale skin and the black/brown outfit')

fresh();lowest=[8,8]
for n in range(600):
    step(one=(1<<7) if n<220 else 0,two=(1<<7) if n<220 else 0)
    _,d=status();lowest=[min(lowest[i],d[i]) for i in range(2)]
assert max(lowest)<8
assert d[2]+d[3]>0
passed('Both players take damage; a defeated player respawns beside a safe partner')

guard_counts=[]
for use_sword in (False,True):
    p.core.al_coop_enable(0);p.restore(seed);p.core.al_coop_enable(1)
    for n in range(300):
        walk=(1<<7) if n<155 else 0
        step(one=walk,two=walk|((1<<0) if use_sword and n%32<16 else 0))
    ram=p.ram()
    guard_counts.append(sum(ram[a]==31 for a in range(0x7e82,0x84b2,66)))
assert guard_counts==[1,0],guard_counts
passed('Player two sword attacks defeat a shared-world guard that survives without attacks')

p.core.al_coop_enable(0);p.restore(seed);p.core.al_coop_enable(1)
for n in range(1500):
    if n<1300:
        b=(1<<7)|((1<<8) if n%80<35 else 0)|((1<<0) if n%36<18 else 0)
    elif n<1336:b=1<<6
    elif n<1366:b=(1<<4)|(1<<8)
    else:b=1<<4
    step(one=b,two=b)
s,_=status()
assert s[3]==s[5]==2104 and 600<s[4]<700 and 600<s[6]<700,s
p.screenshot(ROOT/'diagnostics/verified-rope.png')
passed('Both players traverse to the central rope and climb it together')

# Inject boundary states to exercise failures without claiming a full playthrough.
p.core.al_probe_player.restype=C.c_void_p
fresh()
p2=p.core.al_probe_player(1)
p.write(0xeffa,b'\0');C.c_ubyte.from_address(p2+0xeffa).value=0
step(180);s,d=status();assert d[:2]==[8,8] and d[4]==0 and s[3]==s[5]==103
passed('Both players at zero health return together to the initial checkpoint')

def place(who,x,y):
    if who==0:
        ram=p.ram();cx=int.from_bytes(ram[0x7df6:0x7df8],'big');cy=int.from_bytes(ram[0x7df8:0x7dfa],'big')
        writer=p.write
    else:
        ptr=p.core.al_probe_player(1);ram=C.string_at(ptr,65536)
        u=lambda a:int.from_bytes(ram[a:a+2],'big')
        cx=u(0x7e42)-u(0x7dfa);cy=u(0x7e44)-u(0x7dfc)
        writer=lambda a,data:C.memmove(ptr+a,data,len(data))
    for a,v in [(0x7dfa,x-cx),(0x7dfc,y-cy),(0x7e02,x),(0x7e04,y),(0x7e42,x),(0x7e44,y)]:
        writer(a,(v&65535).to_bytes(2,'big'))

fresh();p.write(0x7df6,(4600).to_bytes(2,'big'));p.write(0x7df8,(32).to_bytes(2,'big'))
place(0,4780,440);place(1,4660,500);step();_,d=status();assert p.core.al_coop_transition_pending()==0
place(0,4780,440);place(1,4780,500);step();_,d=status();assert p.core.al_coop_transition_pending()==0
place(0,4780,440);place(1,4780,440);step();_,d=status();assert p.core.al_coop_transition_pending()==1
passed('Injected exit states: completion waits for both players, including their vertical positions')

# Exercise the compiled frontend too, including ROM validation and startup state.
subprocess.run([str(ROOT/'Aladdin-Coop.exe'),'--test','180'],cwd=ROOT,check=True,timeout=30)
values=(ROOT/'diagnostics/launcher-status.txt').read_text().split()
assert values[0]=='0', 'Launcher should boot the original introduction before gameplay'
passed('Compiled Windows launcher boots the original game for 180 frames')

report={'passed':results,'rom_sha256':hashlib.sha256(p.rom_path.read_bytes()).hexdigest(),
        'limitations':['No full first-level completion playthrough yet.','Physical controllers and speakers require manual testing.','Emulator-assisted prototype; not a hardware-compatible ROM patch.']}
(ROOT/'diagnostics/verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('All',len(results),'checks passed.')

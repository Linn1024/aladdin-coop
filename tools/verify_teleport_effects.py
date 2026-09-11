"""Teleport pickup effects: both players, rescue, noclip, mute, replay and cleanup."""
exec(compile(open(__file__.replace('verify_teleport_effects.py','verify_campaign.py')).read().split('for level,name in enumerate(names):')[0],__file__,'exec'))
c.al_probe_player.restype=C.POINTER(C.c_ubyte)
def fresh():
 c.al_coop_enable(0);p.restore(seed);c.al_coop_enable(1);step(90)
def effects():return [a for a in range(0x7e82,0x85fc,66) if p.ram()[a]==0x84 and 0x122f80<=int.from_bytes(p.ram()[a+32:a+36],'big')<0x122fa0]
def trace_step(n=1,one=0,two=0):
 c.al_probe_start();step(n,one,two);ptr=C.POINTER(C.c_uint)();n=c.al_probe_stop(C.byref(ptr));return set(ptr[:n])
for who in (0,1):
 fresh();r=p.ram();lives=r[0x7e3c];bonus=r[0xf176:0xf17a]
 events=trace_step(1,one=(1<<10) if who==0 else 0,two=(1<<10) if who==1 else 0)
 assert len(effects())==4 and 0x1af2d6 in events
 assert p.ram()[0xf176:0xf17a]==bonus and p.ram()[0x7e3c]==lives
 for _ in range(10):step(one=(1<<10) if who==0 else 0,two=(1<<10) if who==1 else 0)
 assert status()[1][2+who]==1,'Held teleport retriggered'
 mid=save();step(30);expected=status(),hashlib.sha256(p.frame[0]).hexdigest()
 assert not effects(),'Sparkles leaked objects'
 restore(mid);step(30);assert (status(),hashlib.sha256(p.frame[0]).hexdigest())==expected
 print('PASS: P'+str(who+1)+' rejoin pickup effects, one trigger, no rewards, mid-effect save and cleanup')
fresh();step(10,two=1<<8);events=trace_step(1,one=1<<10)
assert not effects() and 0x1af2d6 not in events,'Refused teleport played effects'
fresh();p.write(0xf57d,b'\0');events=trace_step(1,two=1<<10)
assert 0x1af2d6 in events and 0x1af2e6 not in events,'Ignored native sound-effects mute'
fresh();assert c.al_coop_debug(8);step(10,one=1<<7);assert c.al_coop_debug(8)
events=trace_step(1);assert len(effects())==4 and 0x1af2d6 in events
fresh();c.al_probe_player(1)[0xeffa]=0;c.al_probe_player(1)[0xf0e6]=255
step(60);assert len(effects())==4 and p.ram()[0x7e3c]==ord('2');events=trace_step(2);assert 0x1af2d6 in events
# Repeated arrivals must release their own graphics allocations.
fresh();initial=sum(bool(x) for x in p.ram()[0xf008:0xf07c])
for _ in range(20):step(1,two=1<<10);step(35)
assert not effects() and sum(bool(x) for x in p.ram()[0xf008:0xf07c])==initial
fresh();p.screenshot(ROOT/'diagnostics/p2-pale-skin.png');step(1,two=1<<10);step(11);p.screenshot(ROOT/'diagnostics/teleport-sparkles.png')
print('PASS: refusal, muted sound, noclip handoff, paid revival and repeated-effect allocation cleanup')

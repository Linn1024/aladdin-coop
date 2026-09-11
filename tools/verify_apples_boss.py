"""Saved low-ammo HUD, sustained throws, Iago tile ownership and actual victory."""
exec(compile(open(__file__.replace('verify_apples_boss.py','verify_campaign.py')).read().split('for level,name in enumerate(names):')[0],__file__,'exec'))
c.al_probe_player.restype=C.POINTER(C.c_ubyte)
fixture=((ROOT/'diagnostics/apple-boss-1.core').read_bytes(),
         (ROOT/'diagnostics/apple-boss-1.extra').read_bytes())

def orphaned():
    r=p.ram();owned=set()
    for i in range(32):
        a=0x7e40+i*66;ptr=int.from_bytes(r[a+42:a+46],'big')&65535
        if r[a] and ptr:owned.update(range(ptr,ptr+r[a+41]+1))
    return {a for a in range(0xf008,0xf07c) if r[a]}-owned

def before_victory():
    restore(fixture)
    assert not orphaned(), 'Old orphaned allocations were not reclaimed'
    p.write(0xf0e9,b'\0')
    for i in (0,1):c.al_probe_player(i)[0xf0e9]=0

before_victory()
for ammo in (1,3,5,6,10,99):
    p.write(0xefe0,f'{ammo:02}'.encode())
    for frame in range(16):
        step();r=p.ram();found=[]
        for a in range(0x729a,0x749a,8):
            y=int.from_bytes(r[a:a+2],'big');x=int.from_bytes(r[a+6:a+8],'big')
            if y==0x148 and x in (0x1a0,0x1a8):
                found.append(a)
                assert (int.from_bytes(r[a+2:a+4],'big')>>8)&15==0, (ammo,frame,r[a:a+8])
        assert found, (ammo,frame,'Missing apple digits')
    assert p.ram()[0xefe0:0xefe2]==f'{ammo:02}'.encode()
p.write(0xefe0,b'03');step();p.screenshot(ROOT/'diagnostics/verified-low-apples.png')

before_victory();p.write(0xefe0,b'99');throws=failures=0
for cycle in range(12):
    c.al_probe_start();step(20,one=2,two=2);step(4)
    ptr=C.POINTER(C.c_uint)();n=c.al_probe_stop(C.byref(ptr));assert n<2000000
    pcs=list(ptr[:n]);throws+=pcs.count(0x1b0360);failures+=pcs.count(0x1ad406)
assert throws==24 and failures==0 and p.ram()[0xefe0:0xefe2]==b'75',(throws,failures)
assert not orphaned()
assert c.al_coop_level()==12 and c.al_coop_ready(), 'Live arena completed without victory'
mid=save();step(80);expected=status(),hashlib.sha256(p.frame[0]).hexdigest()
restore(mid);step(80);assert (status(),hashlib.sha256(p.frame[0]).hexdigest())==expected

stage(12)
for cycle in range(8):
    step(128);assert not orphaned(), (cycle,orphaned())

# This fixture records the actual defeated boss, with players 137 pixels apart.
restore(fixture);step(3);assert not c.al_coop_ready(), 'Victory still requires proximity'
bonus=save()
def finish_bonus():
    for frame in range(2400):
        p.run(1,{0,8,3} if frame%30==0 else set())
        if c.al_coop_ready() and c.al_coop_level()==11:break
    else:raise AssertionError('Native bonus/story did not reach Jafar')
    return status(),hashlib.sha256(p.frame[0]).hexdigest()
a=finish_bonus();restore(bonus);assert finish_bonus()==a
p.screenshot(ROOT/'diagnostics/verified-iago-to-jafar.png')
print('PASS: low/high ammo digits; 24 simultaneous-player throws; old tile leak repaired;')
print('      1024-frame arena has no leak; real Iago victory advances; saved bonus replays')

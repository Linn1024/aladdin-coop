"""Stage-load and behavior checks. This is not a complete campaign playthrough."""
from probe import *
import json
p=Probe();c=p.core;seed=(ROOT/'first-level.state').read_bytes();results=[]
names=['Rooftops','Agrabah','Abu Market','Desert','Dungeon','Cave of Wonders',
       'Abu Cave','The Escape','Rug Ride','Inside the Lamp','Sultan Palace','Jafar','Iago']
def status():
    s=(C.c_uint*7)();d=(C.c_uint*6)();c.al_coop_status(s);c.al_coop_details(d)
    return list(s),list(d)
def step(n=1,one=0,two=0):
    c.al_coop_buttons(0,one);c.al_coop_buttons(1,two)
    p.run(n)
def stage(level):
    c.al_coop_enable(0);p.restore(seed);c.al_coop_enable(1);step(10)
    assert c.al_coop_debug_stage(level)
    for n in range(2400):
        p.run(1,{3} if n%90==0 else set())
        if n>1 and c.al_coop_ready() and c.al_coop_level()==level:break
    else:raise AssertionError(('Stage did not load',level,status()))
    assert c.al_coop_debug(1);step(4)
def save():
    b=C.create_string_buffer(c.al_coop_state_size());assert c.al_coop_save(b,len(b))
    return p.save(),b.raw
def restore(s):
    p.restore(s[0]);b=C.create_string_buffer(s[1]);assert c.al_coop_restore(b,len(s[1]))

for level,name in enumerate(names):
    stage(level);s,d=status();r=p.ram()
    assert r[0x7e40]==r[0x863e]==0x83,(level,s,d)
    assert d[:2]==[8,8]
    base=save();before=s
    if level==8:
        step(10,two=1<<4);s,_=status()
        assert s[6]<before[6] and s[4]==before[4] and 40<=s[3]-s[5]<=60
    else:
        step(15,two=1<<7);s,_=status()
        assert s[5]!=before[5] or s[6]!=before[6],(level,'P2 did not move',before,s)
    p.screenshot(ROOT/f'diagnostics/campaign-{level:02}.png')
    def replay():
        step(10,one=1<<4 if level==8 else 1<<8,two=1<<7)
        step(30);return status(),hashlib.sha256(p.frame[0]).hexdigest()
    restore(base);a=replay();restore(base);b=replay();assert a==b,(level,'Replay diverged')
    restore(base)
    # Standard stage respawns, including the carpet, use the native rebuild.
    # Abu rooms have their own scripted lose/return flow and are checked separately.
    respawn=None
    if level not in (2,6):
        assert c.al_coop_debug(5);step(2)
        for n in range(600):
            step();s,d=status()
            if c.al_coop_ready() and d[:2]==[8,8]:break
        else:raise AssertionError(('Team failed to respawn',level,s,d))
        assert c.al_coop_level()==level
        respawn=True
    results.append({'id':level,'name':name,'loaded':True,'p2_moves':True,
                    'save_replay_matches':True,'checkpoint_respawn':respawn})
    print('PASS:',level,name,flush=True)
(ROOT/'diagnostics/campaign-verification.json').write_text(json.dumps({
 'stages':results,'limitation':'Direct stage loads and short behavior checks; not a complete level-by-level playthrough.'
},indent=2)+'\n')

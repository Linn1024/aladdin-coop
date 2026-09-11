"""Exercise native checkpoint contact, team death, save/load, and HUD sprite output.

Checkpoint objects are injected collision fixtures, not a claim of a full playthrough.
"""
from probe import *
import json

p=Probe()
p.core.al_probe_player.restype=C.c_void_p
seed=(ROOT/'first-level.state').read_bytes()
def fresh():
    p.core.al_coop_enable(0);p.restore(seed);p.core.al_coop_enable(1);p.run(10)
def details():
    d=(C.c_uint*6)();p.core.al_coop_details(d);return list(d)
def write_player(who,a,data):
    if who==0:p.write(a,data)
    else:C.memmove(p.core.al_probe_player(1)+a,data,len(data))
def place(who,x):
    for a in (0x7dfa,0x7e02,0x7e42):write_player(who,a,x.to_bytes(2,'big'))
def checkpoint(who,x):
    place(who,x)
    # A checkpoint collision object with valid existing sprite bounds. The ROM
    # handles contact, activation animation, and checkpoint coordinate storage.
    obj=bytearray(p.ram()[0x7e40:0x7e82]);obj[0]=0x43
    obj[2:4]=x.to_bytes(2,'big');obj[0x2a:0x32]=bytes(8)
    p.write(0x7e82,obj);p.run(3)
    ram=p.ram();u=lambda a:int.from_bytes(ram[a:a+2],'big')
    assert ram[0x7e82]==0x8a and u(0x7e0a)+u(0x7e0e)==x
def save():
    extra=C.create_string_buffer(p.core.al_coop_state_size())
    assert p.core.al_coop_save(extra,len(extra));return p.save(),extra.raw
def restore(s):
    p.restore(s[0]);b=C.create_string_buffer(s[1]);assert p.core.al_coop_restore(b,len(s[1]))
def die():
    for who in (0,1):write_player(who,0xeffa,b'\0')
    p.run(12) # Deliberately save during the multi-frame native world rebuild.
def revived(x):
    p.run(100);s=(C.c_uint*7)();p.core.al_coop_status(s)
    assert s[0] and s[3]==s[5]==x and details()[:2]==[8,8],(list(s),details())
    assert p.ram()[0x7e3c]==ord('3'),'Shared retries must not consume native lives'
    return hashlib.sha256(p.frame[0]).hexdigest()

for who in (0,1):
    fresh();place(1-who,103);checkpoint(who,240)
    activated=save();die();mid=save();a=revived(240)
    restore(mid);b=revived(240);assert a==b
    # Load the activated checkpoint after changing the shared checkpoint words.
    p.write(0x7e0a,bytes(8));restore(activated);die();revived(240)
    p.screenshot(ROOT/f'diagnostics/checkpoint-player-{who+1}.png')
    print(f'PASS: P{who+1} activates shared checkpoint; both revive there; save/load during respawn replays exactly')

fresh();write_player(0,0xeffa,b'\x06');write_player(1,0xeffa,b'\x03');p.run(3)
ram=p.ram();sprites=[];index=0
for _ in range(80):
    a=0x729a+index*8;s=ram[a:a+8];sprites.append(s);index=s[3]&127
    if not index:break
smoke=[s for s in sprites if int.from_bytes(s[:2],'big')==0x8c]
# Native smoke has one cap sprite plus one animated sprite per health point.
assert sum(int.from_bytes(s[6:8],'big')<0x140 for s in smoke)==7
assert sum(int.from_bytes(s[6:8],'big')>=0x140 for s in smoke)==4
assert not any(0xe7c0<=int.from_bytes(s[4:6],'big')<=0xe7e4 for s in sprites)
assert details()[:2]==[6,3]
p.screenshot(ROOT/'diagnostics/verified-independent-health.png')
print('PASS: Separate native health meters show 6 and 3 segments; score sprites removed; rendering preserves health')
(ROOT/'diagnostics/checkpoint-hud-verification.json').write_text(json.dumps({
    'both_players_activate_checkpoint':True,'team_respawn_at_checkpoint':True,
    'mid_respawn_save_replay_matches':True,'independent_health_meters':True,
    'score_removed':True,'unlimited_shared_retries':True,
    'method':'Injected checkpoint collision fixtures and health values; native ROM activation and world rebuild.'
},indent=2)+'\n')

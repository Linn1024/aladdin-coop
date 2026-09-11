"""User ghost save, real water hazards, invincibility and checkpoint recovery."""
exec(compile(open(__file__.replace('verify_drowning.py','verify_campaign.py')).read().split('for level,name in enumerate(names):')[0],__file__,'exec'))
c.al_probe_player.restype=C.POINTER(C.c_ubyte)
fixture=((ROOT/'diagnostics/drowning-user.core').read_bytes(),
         (ROOT/'diagnostics/drowning-user.extra').read_bytes())
restore(fixture)
assert c.al_coop_debug_flags()&1 and p.ram()[0x7e40]==0
old=status();step(80);s,d=status()
assert d[:2]==[8,8] and d[2]==old[1][2]+1 and s[3:5]==s[5:7]
assert p.ram()[0x7e40]==p.ram()[0x863e]==0x83
p.screenshot(ROOT/'diagnostics/verified-drowning-recovery.png')
safe=save()

def water(player):
    # Position a live player on a real Cave water tile, then let native
    # collision dispatch execute the drowning routine at 1B53B0.
    r=p.ram();cx=int.from_bytes(r[0x7df6:0x7df8],'big');cy=int.from_bytes(r[0x7df8:0x7dfa],'big')
    mem=c.al_probe_player(player)
    def write(a,b):
        if player==0:p.write(a,b)
        else:
            for i,v in enumerate(b):mem[a+i]=v
    for a,v in [(0x7e42,1440),(0x7e02,1440),(0x7dfa,1440-cx),
                (0x7e44,1200),(0x7e04,1200),(0x7dfc,1200-cy),(0x7e5a,0)]:
        write(a,v.to_bytes(2,'big'))
    write(0xf0c1,b'\0')

for protection in (True,False):
    for player in (0,1):
        restore(safe)
        if not protection:assert c.al_coop_debug(1)
        before=status()[1][2+player]
        water(player);c.al_probe_start();step(5)
        trace=C.POINTER(C.c_uint)();n=c.al_probe_stop(C.byref(trace))
        assert 0x1b53b0 in trace[:n], 'Native water hazard was not exercised'
        assert status()[1][player]==0,'Water death should remain visible before rescue'
        step(80)
        s,d=status();assert d[:2]==[8,8] and d[2+player]==before+1,(protection,player,s,d)
        assert s[3:5]==s[5:7]
        assert p.ram()[0x7e40]==p.ram()[0x863e]==0x83

restore(safe);water(0);water(1);step(65)
assert not c.al_coop_ready(), status()
pending=save()
def replay():
    step(200);s,d=status()
    assert c.al_coop_ready() and c.al_coop_level()==5 and d[:2]==[8,8],(s,d)
    assert p.ram()[0x7e40]==p.ram()[0x863e]==0x83
    assert c.al_coop_debug_flags()&1
    return s,d,hashlib.sha256(p.frame[0]).hexdigest()
a=replay();restore(pending);assert replay()==a
print('PASS: old drowning save recovered; both players drown/rescue with god mode on/off;')
print('      simultaneous drowning returns to checkpoint; mid-respawn save replays exactly')

"""Check scripted deaths that do not set HP, plus airborne carpet rescue."""
exec(compile(open(__file__.replace('verify_campaign_events.py','verify_campaign.py')).read().split('for level,name in enumerate(names):')[0],__file__,'exec'))
stage(8);assert c.al_coop_debug(1) # Turn off the test's initial protection.
before=status()[1][2]
p.write(0xf0e6,b'\x20');step(2)
s,d=status();assert d[:2]==[8,8] and d[2]>before,(s,d)
c.al_probe_player.restype=C.c_void_p
p.write(0xf0e6,b'\x20')
C.c_ubyte.from_address(c.al_probe_player(1)+0xf0e6).value=0x20
step(3);assert not c.al_coop_ready()
mid=save()
def replay():
    step(150);s,d=status();assert c.al_coop_level()==8 and c.al_coop_ready() and d[:2]==[8,8]
    return hashlib.sha256(p.frame[0]).hexdigest()
a=replay();restore(mid);b=replay();assert a==b
(ROOT/'diagnostics/campaign-event-verification.json').write_text(json.dumps({
 'scripted_death_with_nonzero_hp_handled':True,'carpet_partner_rescue':True,
 'carpet_team_respawn':True,'mid_respawn_replay_matches':True
},indent=2)+'\n')
print('PASS: Scripted carpet deaths, partner rescue, and saved team respawn')

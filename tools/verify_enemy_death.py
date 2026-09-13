"""Actual guard attacks against either player and visible, saved fatal-hit timing."""
exec(compile(open(__file__.replace('verify_enemy_death.py','verify_campaign.py')).read().split('for level,name in enumerate(names):')[0],__file__,'exec'))
c.al_probe_player.restype=C.POINTER(C.c_ubyte)
c.al_coop_enable(0);p.restore(seed);c.al_coop_enable(1);step(155,one=1<<7,two=1<<7);step(15)
base=save()
# Personal coal flames can occupy different slots before the guard spawns.
guards=[a for a in range(0x7e82,0x863e,0x42) if p.ram()[a]==31]
assert len(guards)==1,guards
guard=guards[0]

def position(who,x):
 cx=int.from_bytes(p.ram()[0x7df6:0x7df8],'big')
 for a,v in ((0x7e42,x),(0x7e02,x),(0x7dfa,x-cx)):
  data=v.to_bytes(2,'big')
  if who==0:p.write(a,data)
  else:
   for i,b in enumerate(data):c.al_probe_player(1)[a+i]=b

def set_byte(who,a,v):
 if who==0:p.write(a,bytes([v]))
 else:c.al_probe_player(1)[a]=v

animations=[]
for who in (0,1):
 restore(base);position(who,700);position(1-who,560)
 before=status()[1][who];seen=set()
 for _ in range(100):
  step();r=p.ram();seen.add(int.from_bytes(r[guard+32:guard+36],'big'))
 assert status()[1][who]<before,'Guard did not hurt selected player'
 assert any(0x12396c<=a<=0x123992 for a in seen),'Guard did not enter sword attack'
 animations.append(seen)
assert animations[0]==animations[1],'Guard attack selection differs by player identity'
print('PASS: guard attacks and damages either nearest player with matching animations')

for who in (0,1):
 restore(base);position(who,700);position(1-who,560)
 set_byte(who,0xeffa,1);set_byte(who,0xf0f2,0);p.write(0x7e3c,b'3')
 for _ in range(180):
  step()
  if not status()[1][who]:break
 else:raise AssertionError('Guard did not inflict fatal damage')
 assert c.al_probe_player(who)[0]==1 and p.ram()[0x7e3c]==ord('3')
 # No immediate respawn, life deduction, or escape with rejoin.
 for _ in range(25):step(one=(1<<10) if who==0 else 0,two=(1<<10) if who==1 else 0)
 assert status()[1][who]==0 and p.ram()[0x7e3c]==ord('3')
 snapshot=c.al_probe_player(who)
 assert 0x1226ce<=int.from_bytes(bytes(snapshot[0x7e60:0x7e64]),'big')<=0x1226e0
 p.screenshot(ROOT/f'diagnostics/fatal-hit-p{who+1}.png')
 mid=save()
 def finish():
  step(30,one=(1<<6) if who==1 else 0,two=(1<<6) if who==0 else 0)
  step(100)
  assert status()[1][who]>0 and p.ram()[0x7e3c]==ord('2'), (who,status(),p.ram()[0x7e3c],c.al_probe_player(who)[0])
  assert c.al_probe_player(who)[0]==0
  return status(),hashlib.sha256(p.frame[0]).hexdigest()
 expected=finish();restore(mid);assert finish()==expected
 print('PASS: P'+str(who+1)+' fatal-hit pose, no early charge/rejoin, mid-death save and one-life recovery')

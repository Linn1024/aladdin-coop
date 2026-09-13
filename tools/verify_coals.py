"""Delayed coal flames must not burn a running partner; stopping remains unsafe."""
from probe_new_bugs import *
def fresh(reverse=False):
 c.al_coop_enable(0);p.restore(seed);c.al_coop_enable(1);step(10)
 if reverse:
  s,_=status();position(0,s[5],s[6]);position(1,s[3],s[4])
for reverse in (False,True):
 fresh(reverse);step(170,one=128,two=128)
 assert status()[1][:2]==[8,8],('Running partners burned',reverse,status())
 base=save();step(100);stopped=status()
 assert all(h<8 for h in stopped[1][:2]),('Standing on coals did not hurt both players',reverse,stopped)
 restore(base);step(100);assert status()==stopped,'Coal ownership did not survive save/replay'
 print('PASS: running safe, both stationary players hurt, save replay; P'+str(1 if reverse else 2)+' leading')
# One stops while the other continues: only the stationary player is burned.
for stopped in (0,1):
 fresh();step(125,one=128,two=128);step(40 if stopped==0 else 65,one=0 if stopped==0 else 128,two=0 if stopped==1 else 128)
 health=status()[1][:2]
 assert health[stopped]<8 and health[1-stopped]==8,('Mixed moving/stationary coal contact',stopped,health)
 print('PASS: only stationary P'+str(stopped+1)+' burns')

"""Shared lives, both death policies, delayed rescue and save-state replay."""
exec(compile(open(__file__.replace('verify_death_options.py','verify_campaign.py')).read().split('for level,name in enumerate(names):')[0],__file__,'exec'))
c.al_probe_player.restype=C.POINTER(C.c_ubyte)
def fresh(mode):
 c.al_coop_enable(0);p.restore(seed);c.al_coop_enable(1);step(30)
 if mode:assert c.al_coop_debug(10)
 p.write(0x7e3c,b'3')
def kill(who):
 if who==0:p.write(0xeffa,b'\0');p.write(0xf0e6,b'\xff')
 else:c.al_probe_player(1)[0xeffa]=0;c.al_probe_player(1)[0xf0e6]=255
for mode in (0,1):
 for dead in ((0,),(1,),(0,1)):
  fresh(mode);step(25,one=1<<7,two=1<<7);step(20)
  for who in dead:kill(who)
  initial=save()
  def replay():
   step(180);s,d=status()
   assert d[:2]==[8,8],(mode,dead,s,d)
   assert p.ram()[0x7e3c]==ord('2'),(mode,dead,p.ram()[0x7e3c])
   if mode or len(dead)==2:assert s[3]==s[5]==103,(s,d)
   else:assert d[2+dead[0]]==1,(s,d)
   assert bool(c.al_coop_debug_flags()&8)==bool(mode)
   return status(),hashlib.sha256(p.frame[0]).hexdigest()
  result=replay();restore(initial);assert replay()==result
  print('PASS:',mode,dead,'one life and deterministic recovery')
fresh(0);step(10,two=1<<8);kill(0);step(2)
assert p.ram()[0x7e3c]==ord('3') and status()[1][0]==0,'Charged before safe rescue'
step(100);assert p.ram()[0x7e3c]==ord('2') and status()[1][:2]==[8,8]
# One last spare life permits recovery at zero; the next death enters native continue.
fresh(0);p.write(0x7e3c,b'1');kill(1);step(90);assert p.ram()[0x7e3c]==ord('0')
kill(1);c.al_probe_start();step(100);trace=C.POINTER(C.c_uint)();n=c.al_probe_stop(C.byref(trace))
assert 0x1a9088 in trace[:n] and 0x1b080e in trace[:n],'Native continue flow not entered'
assert p.ram()[0x7e3c]==ord('0'),'Lives wrapped'
print('PASS: safe landing wait; zero lives uses original continue flow')

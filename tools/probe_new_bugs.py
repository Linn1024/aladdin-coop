from probe import *
exec(compile(open(__file__.replace('probe_new_bugs.py','verify_campaign.py')).read().split('for level,name in enumerate(names):')[0],__file__,'exec'))
c.al_probe_player.restype=C.POINTER(C.c_ubyte)
def put(who,a,data):
 if who==0:p.write(a,data)
 else:
  for i,b in enumerate(data):c.al_probe_player(1)[a+i]=b

def word(who,a,v):put(who,a,(v&65535).to_bytes(2,'big'))
def position(who,x,y):
 r=p.ram();cx=int.from_bytes(r[0x7df6:0x7df8],'big');cy=int.from_bytes(r[0x7df8:0x7dfa],'big')
 for a,v in ((0x7e42,x),(0x7e02,x),(0x7dfa,x-cx),(0x7e44,y),(0x7e04,y),(0x7dfc,y-cy)):word(who,a,v)
def warp(x,y):
 assert c.al_coop_debug(8);step();position(0,x,y);step(700);assert c.al_coop_debug(8);step(5)
def dump():
 print(status())
 for i in range(32):
  a=0x7e40+66*i;o=p.ram()[a:a+66]
  if o[0]:print(i,o.hex())
if __name__=='__main__':
 stage(10);warp(1696,940);p.screenshot(ROOT/'diagnostics/palace-cage-near.png');dump()
 s=save();(ROOT/'diagnostics/palace-cage.core').write_bytes(s[0]);(ROOT/'diagnostics/palace-cage.extra').write_bytes(s[1])

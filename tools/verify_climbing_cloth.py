"""Vertical climbing cuffs/folds remain red, including isolated highlights."""
from audit_sprite_art import *
p.restore((ROOT/'first-level.state').read_bytes());p.write(0x863e,b'\x83');p.write(0x866c,(0x8000).to_bytes(4,'big'))
p.core.al_probe_vram.restype=C.POINTER(C.c_ubyte)
cloth=steel=0
reported={0x1e6b9a:[(137,137)],0x1e6bdc:[(135,129),(136,129),(137,129),(138,130)],0x1e6c36:[(139,127),(140,128)],0x1e6c90:[(125,136),(139,130)],0x1e6cf6:[(128,132)]}
for a in range(0x7ba,0x7da,4):
 f=int.from_bytes(rom[a:a+4],'big');pcs,px,size=decode(f)
 p.write(0x8652,f.to_bytes(4,'big'));p.write(0x8667,bytes([(size+127)//128-1]));p.core.al_probe_recolor();v=p.core.al_probe_vram()
 def value(q):
  ink,o,s=px[q];return (v[0x8000+(o^1)]>>s)&15
 for q,(ink,o,s) in px.items():
  if q[1]>=114 and ink in (1,2,14):
   assert value(q)==(8 if ink==14 else 7),('White climbing fabric',hex(f),q,ink,value(q));cloth+=1
  if ink in (12,13) and value(q)==ink:steel+=1
 for q in reported.get(f,[]):assert value(q) in (7,8),('Reported cuff/fold',hex(f),q)
assert cloth>500 and steel>100,(cloth,steel)
print('PASS: 8 vertical-rope poses;',cloth,'cloth pixels;',steel,'native steel pixels; 10 reported fragments')

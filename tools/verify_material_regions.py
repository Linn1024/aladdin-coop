"""Semantic checks for the complete idle patch, folds and narrow vest panels."""
from audit_sprite_art import *
p.restore((ROOT/'first-level.state').read_bytes());p.write(0x863e,b'\x83');p.write(0x866c,(0x8000).to_bytes(4,'big'));p.core.al_probe_vram.restype=C.POINTER(C.c_ubyte)
patches=folds=vests=poses=0
for f in sorted(frames):
 if not 0x1ec27c<=f<=0x1ec6b4:continue
 pieces,px,size=decode(f);p.write(0x8652,f.to_bytes(4,'big'));p.write(0x8667,bytes([(size+127)//128-1]));p.core.al_probe_recolor();v=p.core.al_probe_vram();poses+=1
 def value(q):
  ink,offset,shift=px[q];return (v[0x8000+(offset^1)]>>shift)&15
 # Hand-labelled torso strips across the entire apple-toss cycle. These
 # occupy different ROM pieces as the arm moves; checking two tile sources
 # alone previously missed most of the animation.
 for q,(ink,_,__) in px.items():
  x,y=q
  if ink==11 and ((127<=x<=131 and 101<=y<=113) or q==(121,100)):
   assert value(q)==10,('Purple idle vest strip',hex(f),q);vests+=1
  if ink==11 and ((y<99) or x>=138 or x<=116):
   assert value(q)==11,('Face, hand or sword shadow became blue',hex(f),q)
 # Includes the cream centre, not just the tan border tested previously.
 for y,(lo,hi) in {132:(126,129),133:(124,129),134:(125,129),135:(126,128),136:(127,127)}.items():
  for x in range(lo,hi+1):
   if (x,y) in px and 1<=px[x,y][0]<=4:
    assert value((x,y))==px[x,y][0],('Hollow/partial patch',hex(f),x,y);patches+=1
 # The native warm fold strokes are inside the trousers, above the patch.
 for q,(ink,_,__) in px.items():
  x,y=q
  if 124<=x<=134 and 118<=y<=128 and 1<=ink<=4:
   assert value(q) in (7,8),('Yellow trouser fold outside patch',hex(f),q,ink,value(q));folds+=1
 for offset,n,source,*_ in pieces:
  if source in (0x7d780,0x93880):
   for j in range(n):
    for shift in (0,4):
     if (rom[source+j]>>shift)&15==11:
      assert (v[0x8000+((offset+j)^1)]>>shift)&15==10,('Purple vest fragment',hex(f),hex(source+j));vests+=1
assert poses>=12 and patches>=200 and folds>=200 and vests>=20,(poses,patches,folds,vests)
print('PASS:',poses,'idle poses;',patches,'full-patch pixels;',folds,'fold pixels;',vests,'narrow vest pixels')

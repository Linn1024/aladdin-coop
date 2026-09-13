from audit_sprite_art import *
p.restore((ROOT/'first-level.state').read_bytes());p.write(0x863e,b'\x83');p.write(0x866c,(0x8000).to_bytes(4,'big'));p.core.al_probe_vram.restype=C.POINTER(C.c_ubyte)
frames_to_check=(0x1ec3cc,0x1ec41a,0x1ec468,0x1ec4c2,0x1ec51c,0x1ec582,0x1ec5dc,0x1ec636)
apples=folds=0
for f in frames_to_check:
 pieces,px,size=decode(f);p.write(0x8652,f.to_bytes(4,'big'));p.write(0x8667,bytes([(size+127)//128-1]));p.core.al_probe_recolor();v=p.core.al_probe_vram()
 for offset,n,source,*_ in pieces:
  if 711072<=source<=711168:
   actual=bytes(v[0x8000+((offset+j)^1)] for j in range(n))
   assert actual==rom[source:source+n],('Idle apple differs from original',hex(f));apples+=1
  elif source==711200:
   for j in range(n):
    for shift in (0,4):
     if (rom[source+j]>>shift)&15==8:assert (v[0x8000+((offset+j)^1)]>>shift)&15==8,'Caught apple is not red'
   apples+=1
 if f==0x1ec5dc:
  for (x,y),(ink,offset,shift) in px.items():
   if 144<=x<=148 and 93<=y<=97:assert (v[0x8000+(offset^1)]>>shift)&15==ink,'Packed descending apple recolored'
  apples+=1
 # The common trouser piece has cream fold strokes throughout these frames.
 for (x,y),(ink,offset,shift) in px.items():
  if ink==1 and 115<=y<=139:
   actual=(v[0x8000+(offset^1)]>>shift)&15
   if actual==7:folds+=1
assert apples==8 and folds>=40,(apples,folds)
print('PASS: all 8 idle apple poses retain native reds; preserved',folds,'dark-red fold pixels')

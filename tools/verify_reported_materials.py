from audit_sprite_art import *
p.restore((ROOT/'first-level.state').read_bytes());p.write(0x863e,b'\x83');p.write(0x866c,(0x8000).to_bytes(4,'big'));p.core.al_probe_vram.restype=C.POINTER(C.c_ubyte)
pal=[0x1c7,0xf7,0x6f,0xa6,0x5d,0x14,0xb,0x2,0x44,0x1e3,0x19a,0x82,0x124,0x92,0x1ff,0];colors=[tuple(((v>>s)&7)*255//7 for s in (0,3,6)) for v in pal]
checked=0
for f in (0x1ec114,0x1ea3c2,0x1ec27c,0x1ec2ca,0x1ec330,0x1ec396):
 pcs,px,size=decode(f);p.write(0x8652,f.to_bytes(4,'big'));p.write(0x8667,bytes([(size+127)//128-1]));p.core.al_probe_recolor();v=p.core.al_probe_vram();im=Image.new('RGB',(256,256),(100,110,110))
 for q,(ink,offset,shift) in px.items():im.putpixel(q,colors[(v[0x8000+(offset^1)]>>shift)&15])
 def actual(q):
  ink,offset,shift=px[q];return (v[0x8000+(offset^1)]>>shift)&15
 if f==0x1ec114:
  assert actual((144,110))==10,'Vest did not use darker blue'
  for q in ((139,95),(143,99),(146,99),(147,99),(148,99)):
   assert px[q][0]==11 and actual(q)==11,('Blue face shadow',hex(f),q);checked+=1
  for q in ((127,133),(123,134),(122,135),(121,136),(122,137),(124,138),(124,134),(125,133),(126,133),(127,134),(122,136),(123,135),(123,137),(124,137),(125,137),(126,136),(127,135)):
   assert actual(q)==px[q][0],('Missing native knee patch',hex(f),q);checked+=1
  for q,(ink,_,__) in px.items():
   x,y=q
   if ink in (3,4) and ((x>=139 and 95<=y<=103) or y>=140 or (x<=128 and 106<=y<=118)):
    assert actual(q)=={3:2,4:3}[ink],('Face/hand/foot recolored',q);checked+=1
 if f==0x1ec27c:
  assert actual((128,97))==11,'Blue face shadow in apple-toss pose'
  for q in ((128,102),(128,103),(128,104),(129,105),(129,106),(130,108),(130,111),(130,112)):
   assert px[q][0]==11 and actual(q)==10,('Purple front vest in apple-toss pose',q);checked+=1
  assert actual((141,106))==11,'Apple-toss hand shadow recolored as vest'
  for q in ((125,133),(126,132),(126,134),(127,135),(128,132),(128,135),(129,133),(129,134)):
   assert actual(q)==px[q][0],('Missing native trouser patch',q);checked+=1
 box=(min(x for x,y in px),min(y for x,y in px),max(x for x,y in px)+1,max(y for x,y in px)+1);im=im.crop(box);im.resize((im.width*5,im.height*5),Image.Resampling.NEAREST).save(ROOT/f'diagnostics/material-fixed-{f:x}.png')

print('PASS:',checked,'hand-labelled face, trousers, hands and feet landmarks in reported poses')

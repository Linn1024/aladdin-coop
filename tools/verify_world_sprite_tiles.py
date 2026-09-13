from probe_new_bugs import *
c.al_probe_vram.restype=C.POINTER(C.c_ubyte);rom=p.rom_path.read_bytes();checks=0;bad=[]
for level in range(13):
 stage(level);previous={}
 for n in range(240):
  step(one=(128 if n<50 else 0),two=(1 if n%30<15 else 0));r=p.ram();v=c.al_probe_vram()
  for a in range(0x7e40,0x863e,66):
   if not r[a]:continue
   f=int.from_bytes(r[a+20:a+24],'big');start=int.from_bytes(r[a+46:a+50],'big');key=(f,start)
   if previous.get(a)!=key:previous[a]=key;continue
   if not f or not start or f>0x1ffff0:continue
   pieces=int.from_bytes(rom[f:f+2],'big')+1
   if pieces>32:continue
   offset=0
   for i in range(pieces):
    d=f+6+i*12;shape=int.from_bytes(rom[d:d+2],'big');size=int.from_bytes(rom[shape+4:shape+6],'big');source=(rom[d+5]|rom[d+7]<<8|(rom[d+9]&127)<<16)*2
    actual=bytes(v[(start+offset+j)^1] for j in range(size));wanted=rom[source:source+size]
    if actual!=wanted:bad.append((level,hex(a),hex(f),n));break
    offset+=size
   else:checks+=1
 print(level,'checked',checks,'bad',bad[-2:] if bad else [])
assert not bad,bad[:20]
print('PASS:',checks,'stable P1/world sprite uploads match original ROM tiles in all 13 stages')

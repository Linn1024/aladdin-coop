"""Skin and vest materials stay the same through standing, movement and climbing."""
exec(compile(open(__file__.replace('verify_outfit_materials.py','verify_campaign.py')).read().split('for level,name in enumerate(names):')[0],__file__,'exec'))
c.al_probe_vram.restype=C.POINTER(C.c_ubyte)
rom=p.rom_path.read_bytes();frames=set();checked=0

def check():
 global checked
 r=p.ram();a=0x863e;frame=int.from_bytes(r[a+20:a+24],'big');start=int.from_bytes(r[a+46:a+50],'big')
 if not frame or not start:return
 frames.add(frame);v=c.al_probe_vram();offset=0
 for piece in range(int.from_bytes(rom[frame:frame+2],'big')+1):
  d=frame+6+piece*12;shape=int.from_bytes(rom[d:d+2],'big');size=int.from_bytes(rom[shape+4:shape+6],'big')
  source=(rom[d+5]|rom[d+7]<<8|(rom[d+9]&127)<<16)*2
  for i in range(size):
   original=rom[source+i];actual=v[start+((offset+i)^1)]
   for shift in (0,4):
    ink=original>>shift&15
    if ink in (3,4,11):
     expected={3:(2,3,7),4:(3,4,7),11:(10,11)}[ink]
     assert actual>>shift&15 in expected,(hex(frame),hex(source+i),ink,actual>>shift&15)
     checked+=1
  offset+=size

def checked_step(**buttons):
 before=p.ram()[0x8652:0x8656];step(**buttons)
 # A new descriptor can be queued just before the frame boundary, before DMA.
 # A stable descriptor on consecutive updates has completed its tile upload.
 if before==p.ram()[0x8652:0x8656]:check()

c.al_coop_enable(0);p.restore(seed);c.al_coop_enable(1);step(30)
for n in range(180):
 checked_step(two=(1<<7 if n<90 else 0)|(1<<8 if 40<=n<55 else 0)|(1 if n%32<16 else 0))
restore(((ROOT/'diagnostics/appearance-rope.core').read_bytes(),(ROOT/'diagnostics/appearance-rope.extra').read_bytes()))
for n in range(60):checked_step(one=1<<4,two=1<<4)
assert len(frames)>20 and checked>10000,(len(frames),checked)
print('PASS:',len(frames),'animation frames,',checked,'material pixels; native tan trouser patches retained')

# Walking frame 1EA3C2 had isolated white knee/cuff fragments below the sword.
# These native VRAM pixel offsets are the previously missed fabric, not skin.
c.al_coop_enable(0);p.restore(seed);c.al_coop_enable(1);step(14,two=1<<7)
r=p.ram();assert int.from_bytes(r[0x8652:0x8656],'big')==0x1ea3c2
start=int.from_bytes(r[0x866c:0x8670],'big');v=c.al_probe_vram()
fold_pixels=[(402,0),(402,4),(406,0),(406,4),(407,0),(410,0),(410,4),
 (411,0),(414,0),(414,4),(423,4),(424,0),(465,4),(469,0),(469,4),
 (473,0),(473,4),(492,0),(497,0)]
assert all((v[start+i]>>shift&15)==8 for i,shift in fold_pixels)
assert any((v[start+i]>>shift&15)==14 for i in range((r[0x8667]+1)*128) for shift in (0,4)), 'Sword highlights were lost'
print('PASS: reported walking-frame fragments are red; silver highlights remain')

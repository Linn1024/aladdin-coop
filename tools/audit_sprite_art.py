"""Decode native ROM sprite descriptors into diagnostic contact sheets."""
from probe import *
import json
p=Probe();rom=p.rom_path.read_bytes()
def decode(f):
 pieces=[];pixels={};size=0
 for i in range(int.from_bytes(rom[f:f+2],'big')+1):
  a=f+6+i*12;shape=int.from_bytes(rom[a:a+2],'big');w,h=rom[shape+8:shape+10];n=int.from_bytes(rom[shape+4:shape+6],'big');assert n==w*h//2
  source=(rom[a+5]|rom[a+7]<<8|(rom[a+9]&127)<<16)*2;x0,y0=rom[a+2:a+4];pieces.append((size,n,source,x0,y0,w,h))
  for x in range(w):
   for y in range(h):
    offset=((x//8)*(h//8)+y//8)*32+(y%8)*4+(x%8)//2;ink=(rom[source+offset]>>(0 if x%2 else 4))&15
    if ink:pixels[((x0+x)&255,(y0+y)&255)]=(ink,size+offset,0 if x%2 else 4)
  size+=n
 return pieces,pixels,size
frames={}
for a in range(0,0x6000,2):
 f=int.from_bytes(rom[a:a+4],'big')
 if not 0x1e8034<=f<=0x1ee088:continue
 try:
  n=int.from_bytes(rom[f:f+2],'big')+1
  if not 1<=n<=32:continue
  pieces,px,size=decode(f)
  if size>4096:continue
 except (IndexError,AssertionError):continue
 frames.setdefault(f,a)
# Vertical-rope art predates the main Aladdin descriptor block. Include the
# eight frames referenced by the native climbing animation table as well.
for a in range(0x7ba,0x7da,4):
 f=int.from_bytes(rom[a:a+4],'big');decode(f);frames.setdefault(f,a)
if __name__=='__main__':
 from PIL import ImageDraw
 p.restore((ROOT/'first-level.state').read_bytes());p.write(0x863e,b'\x83');p.write(0x866c,(0x8000).to_bytes(4,'big'));p.core.al_probe_vram.restype=C.POINTER(C.c_ubyte)
 # Native palette values, packed BGR 3-bit channels.
 pal=[0x1c7,0xf7,0x6f,0xa6,0x5d,0x14,0xb,0x2,0x44,0x1e3,0x19a,0x82,0x124,0x92,0x1ff,0]
 colors=[tuple(((v>>s)&7)*255//7 for s in (0,3,6)) for v in pal]
 checked_pixels=0
 for page in range((len(frames)+23)//24):
  sheet=Image.new('RGB',(800,720),(100,110,110));draw=ImageDraw.Draw(sheet)
  for j,f in enumerate(sorted(frames)[page*24:page*24+24]):
   pieces,px,size=decode(f);xs=[q[0] for q in px];ys=[q[1] for q in px];x0,y0=min(xs),min(ys);im=Image.new('RGB',(max(xs)-x0+1,max(ys)-y0+1),(100,110,110))
   for (x,y),(ink,_,__) in px.items():im.putpixel((x-x0,y-y0),colors[ink])
   p.write(0x8652,f.to_bytes(4,'big'));allocation=(size+127)//128*128;p.write(0x8667,bytes([allocation//128-1]));v=p.core.al_probe_vram()
   v[0x7ffe]=0x5a;v[0x8000+allocation]=0xa5
   p.core.al_probe_recolor();expected=bytes(v[0x8000:0x8000+allocation]);after=im.copy()
   assert v[0x7ffe]==0x5a and v[0x8000+allocation]==0xa5,('VRAM overrun',hex(f))
   # Stale recolored VRAM in an old save must not affect rebuilt art.
   for k in range(allocation):v[0x8000+k]=0x55
   p.core.al_probe_recolor();assert bytes(v[0x8000:0x8000+allocation])==expected,('Recolor depends on old VRAM',hex(f))
   for offset,n,source,_,__,___,____ in pieces:
    for k in range(n):
     actual=v[0x8000+((offset+k)^1)];native=rom[source+k]
     if 0x1ed230<=f<=0x1ed2e4:assert actual==native,('Teleport sparkle recolored as clothing',hex(f))
     for shift in (0,4):
      if not ((native>>shift)&15):assert not ((actual>>shift)&15),('Transparency changed',hex(f))
      checked_pixels+=1
   for (x,y),(ink,offset,shift) in px.items():after.putpixel((x-x0,y-y0),colors[(v[0x8000+(offset^1)]>>shift)&15])
   col,row=j%4,j//4;sheet.paste(im,(col*200,row*120+18));sheet.paste(after,(col*200+100,row*120+18));draw.text((col*200,row*120),hex(f),fill='white')
  sheet.save(ROOT/f'diagnostics/audit-sprites-{page}.png')
 (ROOT/'diagnostics/sprite-art-audit.json').write_text(json.dumps({'frames':len(frames),'pixel_checks':checked_pixels,'descriptors':[hex(f) for f in sorted(frames)],'scope':'Aladdin descriptors and body fragments 1E8034..1EE088; visual contact sheets plus transparency, allocation guards and stale-VRAM replay'},indent=2))
 print('PASS:',len(frames),'frames;',checked_pixels,'pixels; transparency, VRAM guards, stale-tile replay')

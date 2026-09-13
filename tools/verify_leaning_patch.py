"""Check native patch outlines and neighboring folds through the full bend cycle."""
from audit_sprite_art import *
p.restore((ROOT/'first-level.state').read_bytes())
p.write(0x863e,b'\x83');p.write(0x866c,(0x8000).to_bytes(4,'big'))
p.core.al_probe_vram.restype=C.POINTER(C.c_ubyte)
folds=patches=poses=0
for f in sorted(frames):
 if not 0x1ec8e8<=f<=0x1ecbac:continue
 pieces,px,size=decode(f);poses+=1
 p.write(0x8652,f.to_bytes(4,'big'));p.write(0x8667,bytes([(size+127)//128-1]))
 p.core.al_probe_recolor();v=p.core.al_probe_vram()
 patch_rows={129:(127,128),130:(125,129),131:(125,130),132:(125,130),133:(127,129)}
 if f==0x1ec8e8:patch_rows={130:(127,129),131:(126,130),132:(126,131),133:(126,131),134:(127,130)}
 if f==0x1ec936:patch_rows={130:(126,129),131:(125,130),132:(125,130),133:(126,130)}
 if f==0x1ecbac:patch_rows={130:(127,128),131:(125,130),132:(125,130),133:(125,130),134:(127,129)}
 for (x,y),(ink,o,s) in px.items():
  actual=(v[0x8000+(o^1)]>>s)&15
  patch=y in patch_rows and patch_rows[y][0]<=x<=patch_rows[y][1]
  if patch and 1<=ink<=4:
   assert actual==ink,('Damaged knee patch',hex(f),x,y,ink,actual);patches+=1
  elif 121<=x<=130 and 129<=y<=137 and 1<=ink<=4:
   assert actual in (7,8),('Yellow knee fold',hex(f),x,y,ink,actual);folds+=1
assert poses==9 and folds>=100 and patches>=180,(poses,folds,patches)
print('PASS:',poses,'bend/recovery poses;',folds,'fold pixels;',patches,'patch pixels')

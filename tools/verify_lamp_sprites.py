"""Two full health meters must leave scanline sprite slots for both players."""
from probe_new_bugs import *
c.al_coop_enable(0);p.restore(seed);c.al_coop_enable(1);step(30)
assert c.al_coop_sprite_budget()==1
base=save();exercised=False
for hp in range(1,9):
 restore(base);p.write(0xeffa,bytes([hp]));c.al_probe_player(1)[0xeffa]=hp
 position(0,200,740);position(1,250,740);step(2)
 r=p.ram();sprites=[]
 for a in range(0x729a,0x751a,8):
  y=int.from_bytes(r[a:a+2],'big')-128;shape=r[a+2];w=((shape>>2)+1)*8;h=((shape&3)+1)*8
  sprites.append((y,h,w,int.from_bytes(r[a+4:a+6],'big')&2047))
  if not r[a+3]:break
 for y in range(12,28):
  row=[s for s in sprites if s[0]<=y<s[0]+s[1]]
  exercised |= len(row)>20 or sum(s[2] for s in row)>320
  assert len(row)<=80,(hp,y,'Sprite scanline overflow',len(row))
  assert sum(s[2] for s in row)<=80*32,(hp,y,'Pixel scanline overflow')
 for a in (0x7e40,0x863e):
  tile=int.from_bytes(r[a+46:a+50],'big')//32;last=tile+(r[a+41]+1)*4
  assert any(tile<=s[3]<last and s[0]<28 and s[0]+s[1]>12 for s in sprites),'Player did not exercise HUD overlap'
 if hp==8:p.screenshot(ROOT/'diagnostics/lamps-players-fixed.png')
assert exercised,'Did not reproduce the native hardware limit'
c.al_coop_enable(0);assert c.al_coop_sprite_budget()==0
print('PASS: both players overlap HUD within sprite and pixel limits at health 1..8')

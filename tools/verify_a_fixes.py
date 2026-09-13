"""Regression checks for the seven issues reported in the local a checklist."""
exec(compile(open(__file__.replace('verify_a_fixes.py','verify_campaign.py')).read().split('for level,name in enumerate(names):')[0],__file__,'exec'))
c.al_probe_player.restype=C.POINTER(C.c_ubyte)
def put(who,a,data):
 if who==0:p.write(a,data)
 else:
  for i,b in enumerate(data):c.al_probe_player(1)[a+i]=b

def word(who,a,v):put(who,a,(v&65535).to_bytes(2,'big'))
def position(who,x,y):
 r=p.ram();cx=int.from_bytes(r[0x7df6:0x7df8],'big');cy=int.from_bytes(r[0x7df8:0x7dfa],'big')
 for a,v in ((0x7e42,x),(0x7e02,x),(0x7dfa,x-cx),(0x7e44,y),(0x7e04,y),(0x7dfc,y-cy)):word(who,a,v)
def fresh():
 c.al_coop_enable(0);p.restore(seed);c.al_coop_enable(1);step(30)

# SAT entries must place P2 ahead of all ordinary world objects and blink using
# its own hurt timer. Tile ownership identifies sprites independently of pose.
def entries():
 r=p.ram();out=[]
 for a in range(0x729a,0x751a,8):
  y=int.from_bytes(r[a:a+2],'big');tile=int.from_bytes(r[a+4:a+6],'big')&2047
  if y>1:out.append(tile)
  if not r[a+3]:break
 return out

def player_tiles(who):
 r=p.ram();a=0x7e40 if who==0 else 0x863e
 start=int.from_bytes(r[a+46:a+50],'big')//32
 return set(range(start,start+(r[a+41]+1)*4))
fresh();put(1,0xf0f2,b'\x20');seen=set()
for n in range(22):
 step();tiles=entries();visible=bool(set(tiles)&player_tiles(1));seen.add(visible)
 assert set(tiles)&player_tiles(0),'P2 hurt timer hid P1'
assert seen=={False,True},'P2 does not blink'
print('PASS: P2 independently blinks during hurt immunity')
fresh();step(155,one=1<<7,two=1<<7);step(15)
for who in (0,1):put(who,0xf0f2,b'\0')
step();tiles=entries();p2=[i for i,t in enumerate(tiles) if t in player_tiles(1)]
r=p.ram();guard=next(a for a in range(0x7e82,0x85fc,66) if r[a]==31);gstart=int.from_bytes(r[guard+46:guard+50],'big')//32;gt=set(range(gstart,gstart+(r[guard+41]+1)*4));enemy=[i for i,t in enumerate(tiles) if t in gt]
assert p2 and enemy and max(p2)<min(enemy),(p2,enemy)
print('PASS: P2 renders before world enemies in the sprite chain')

# Native scripted duck signal must affect both carpet riders.
stage(8);p.write(0xf10b,b'\1');seen=[set(),set()]
for n in range(60):
 step();r=p.ram()
 for who,a in enumerate((0x7e60,0x865e)):seen[who].add(int.from_bytes(r[a:a+4],'big'))
assert all(any(0x122370<=v<0x122392 for v in poses) for poses in seen),seen
p.screenshot(ROOT/'diagnostics/task-a-rug-duck-fixed.png')
print('PASS: shared obstacle cue animates both riders ducking')

# Each spring family must launch a follower during the leader's recoil.
rom=p.rom_path.read_bytes();spring=0x7e40+15*66
for template,typ,lead in ((t,k,l) for t,k in ((0x1b7a30,1),(0x1b7f80,0x4e),(0x1b7f94,0x4f),(0x1b7e54,0x65)) for l in (0,1)):
 fresh();q=rom[template:template+20];o=bytearray(66)
 o[:2]=q[:2];o[6:10]=q[2:6];o[10:14]=q[6:10];o[30:32]=q[10:12];o[32:36]=q[12:16];o[41]=q[16];o[53]=q[17];o[60]=q[18]
 o[2:4]=(300).to_bytes(2,'big');o[4:6]=(848).to_bytes(2,'big');p.write(spring,o);position(0,200,848);position(1,150,848);step(2)
 def land(who):
  position(who,300,847);word(who,0x7e5a,0x100);put(who,0xf0be,b'\xff');put(who,0xf0c0,b'\xff');put(who,0xf0c1,b'\0')
 def velocity(who):return int.from_bytes(bytes(c.al_probe_player(who)[0x7e5a:0x7e5c]),'big',signed=True)
 land(lead);step();assert velocity(lead)<0,hex(typ)
 land(1-lead);mid=save()
 def follow():
  step();v=velocity(1-lead)
  assert v<0,(hex(typ),v)
  return status(),hashlib.sha256(p.frame[0]).hexdigest()
 expected=follow();restore(mid);assert follow()==expected
 land(lead);step();assert velocity(lead)>=0,'Same player bypassed its own spring cooldown'
 position(0,100,848);position(1,150,848)
 step(40);land(lead);step();assert velocity(lead)<0,('Personal spring cooldown did not expire',hex(typ),lead,velocity(lead),p.ram()[spring:spring+66].hex(),bytes(c.al_probe_player(lead)[0x200+15*8:0x208+15*8]).hex())
 print('PASS: independent spring cooldown and saved replay',hex(typ),'leader P'+str(lead+1))

# A dead player below the survivor must not cap an upward jump or the camera.
for dead in (0,1):
 fresh();alive=1-dead;position(dead,240,900);put(dead,0xeffa,b'\0');put(dead,0xf0e6,b'\xff')
 position(alive,240,648);word(alive,0x7e5a,-0x700);put(alive,0xf0be,b'\xff');put(alive,0xf0c0,b'\0');put(alive,0xf0c1,b'\0')
 before=int.from_bytes(p.ram()[0x7df8:0x7dfa],'big');mid=save()
 def rise():
  step(18);y=status()[0][4+alive*2];cy=int.from_bytes(p.ram()[0x7df8:0x7dfa],'big')
  assert y<620 and cy<before,(dead,y,cy,before)
  return status(),hashlib.sha256(p.frame[0]).hexdigest()
 expected=rise();restore(mid);assert rise()==expected
 print('PASS: camera and upward motion ignore dead P'+str(dead+1))

# The real Genie bonus save waits for one native A/B/C press.
slot_paths=[ROOT/'diagnostics/task-a-slot.core',ROOT/'diagnostics/task-a-slot.extra']
if all(f.exists() for f in slot_paths):
 slot=tuple(f.read_bytes() for f in slot_paths)
 for button in (1<<0,1<<1,1<<8):
  tracks=[]
  for who in (0,1):
   restore(slot);step(2);tokens=p.ram()[0xf003];step(3,one=button if who==0 else 0,two=button if who==1 else 0)
   assert p.ram()[0xf003]<tokens,(who,button,tokens,p.ram()[0xf003])
   tracks.append((p.ram()[0xf003],hashlib.sha256(p.frame[0]).hexdigest()))
  assert tracks[0]==tracks[1],(button,tracks)
 print('PASS: either player can stop the Genie slot machine with A/B/C')

# Abu gets a dedicated darker tan ramp, preserving bright eye/clothing inks.
for level in (2,6):
 stage(level);step(12,two=1<<7);p.screenshot(ROOT/f'diagnostics/task-a-abu-{level}-fixed.png')
 r=p.ram();a=0x863e;frame=int.from_bytes(r[a+20:a+24],'big');start=int.from_bytes(r[a+46:a+50],'big')
 c.al_probe_vram.restype=C.POINTER(C.c_ubyte);vram=c.al_probe_vram();count=int.from_bytes(rom[frame:frame+2],'big')+1;offset=0;changed=0
 for piece in range(count):
  q=rom[frame+6+piece*12:frame+18+piece*12];shape=int.from_bytes(q[:2],'big');size=int.from_bytes(rom[shape+4:shape+6],'big');source=(q[5]|q[7]<<8|(q[9]&127)<<16)*2
  for i,b in enumerate(rom[source:source+size]):
   for shift in (0,4):
    ink=(b>>shift)&15;expect=ink+1 if 1<=ink<=6 else ink;actual=(vram[start+((offset+i)^1)]>>shift)&15
    assert actual==expect,(level,hex(frame),ink,actual,expect)
    changed+=actual!=ink
  offset+=size
 assert changed>20
 print('PASS: darker P2 Abu source-tile mapping in bonus stage',level)

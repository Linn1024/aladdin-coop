"""Native rope pacing, either-player look-up and shared scripted rides."""
from probe_new_bugs import *
stage(0);warp(200,496);base=save();tracks=[]
for one,two,who in ((128,0,0),(0,128,1),(128,128,0),(128,128,1)):
 restore(base);track=[]
 for n in range(40):
  step(one=one,two=two);q=c.al_probe_player(who);track.append((q[0xf16a],bytes(q[0x7e60:0x7e64])))
 tracks.append(track)
assert tracks[0]==tracks[2] and tracks[1]==tracks[3] and tracks[0][1:]==tracks[1][1:],'Two climbers changed animation pacing'
print('PASS: either/both players have the same horizontal-rope animation pace')
c.al_coop_enable(0);p.restore(seed);c.al_coop_enable(1);step(40);base=save();ys=[]
for who in (0,1):
 restore(base);step(100,one=16 if who==0 else 0,two=16 if who==1 else 0);ys.append(int.from_bytes(p.ram()[0x7df8:0x7dfa],'big'))
 up=ys[-1];step(100);assert int.from_bytes(p.ram()[0x7df8:0x7dfa],'big')>up,'Look-up stuck after release'
assert ys[0]==ys[1],ys
print('PASS: P2 look-up scroll matches P1 and releases cleanly')
rom=p.rom_path.read_bytes()
def spawn(slot,template,x,y):
 q=rom[template:template+20];o=bytearray(66);o[:2]=q[:2];o[6:10]=q[2:6];o[10:14]=q[6:10];o[30:32]=q[10:12];o[32:36]=q[12:16];o[41]=q[16];o[53]=q[17];o[60]=q[18];o[2:4]=x.to_bytes(2,'big');o[4:6]=y.to_bytes(2,'big');a=0x7e40+slot*66;p.write(a,o);return a
# Run the native optional snake branch with a real flute pickup. P2 picks it
# up while P1 is the snake rider, so player-local state must not hide the flag.
stage(0);warp(200,496);position(0,200,500);position(1,260,500)
# Match the optional flute callback and native spawner 1B70B0.
flute_type=next(t for t in range(127) if int.from_bytes(rom[0x1cbe+4*t:0x1cc2+4*t],'big')==0x1af060)
template=0x1b79b8
flute=spawn(15,template,260,470);p.write(flute,bytes([flute_type]));p.write(flute+32,(0x123e36).to_bytes(4,'big'));p.write(flute+41,b'\x01');step(4)
assert p.ram()[0xf116]==255,'P2 flute pickup not retained by shared world'
snake=spawn(16,0x1b7904,200,500);p.write(snake,b'\x71');p.write(snake+10,(0x12070e).to_bytes(4,'big'))
p.write(0xf0d3,b'\x71');base=save()
def route():
 step(4);return int.from_bytes(p.ram()[snake+10:snake+14],'big')
secret=route();restore(base);p.write(0xf116,b'\0');normal=route();assert secret!=normal,(hex(secret),hex(normal))
print('PASS: P2 optional flute changes the native snake route',hex(secret),hex(normal))
# Scripted carpet and its paired invisible route controller.
rides=[]
for rider in (0,1):
 c.al_coop_enable(0);p.restore(seed);c.al_coop_enable(1);step(30)
 carpet=spawn(15,0x1b78a0,300,780);control=spawn(16,0x1b78c8,332,716)
 p.write(carpet+62,(0xff0000+control).to_bytes(4,'big'));p.write(control+62,(0xff0000+carpet).to_bytes(4,'big'))
 p.write(0xf094,(300).to_bytes(2,'big')+(780).to_bytes(2,'big'))
 position(rider,300,780);position(1-rider,180,848);base=save()
 def ride():
  track=[]
  for n in range(25):
   step();r=p.ram();xy=tuple(int.from_bytes(r[carpet+k:carpet+k+2],'big') for k in (2,4))
   track.append((xy,status()[0][3+2*rider:5+2*rider]))
  return track
 track=ride();restore(base);assert ride()==track,'Carpet save replay diverged'
 assert track[-1][0]==(360,734) and track[-1][1]==[360,734],track[-1]
 rides.append(track)
 p.screenshot(ROOT/f'diagnostics/scripted-carpet-p{rider+1}.png')
assert [v[0] for v in rides[0]]==[v[0] for v in rides[1]] and rides[0][2:]==rides[1][2:],'P2 boarding changed the scripted carpet path'
print('PASS: either rider stays aboard the same native carpet route; saved replay matches')
# Exact local user save: P2 collected the key, but the passage carpet remained.
blocked=((ROOT/'diagnostics/blocked-cage.core').read_bytes(),(ROOT/'diagnostics/blocked-cage.extra').read_bytes())
restore(blocked);assert p.ram()[0xf11c]==255
base=save()
def descend():
 step(60);assert p.ram()[0x7e40+18*66]==0,'Locked passage carpet survived the key'
 assert status()[0][6]>800,'P2 did not fall through the opened passage'
 return status(),hashlib.sha256(p.frame[0]).hexdigest()
expected=descend();p.screenshot(ROOT/'diagnostics/blocked-cage-fixed.png');restore(base);assert descend()==expected
print('PASS: old P2 key save opens the palace passage; saved replay matches')
for collector in (0,1):
 restore(blocked)
 p.write(0xf11c,b'\0')
 for who in (0,1):c.al_probe_player(who)[0xf11c]=0
 position(collector,2927,596);position(1-collector,2800,596)
 step(2);assert p.ram()[0x7e40+18*66]==0x5f,'Passage opened without key'
 spawn(15,0x1b7b70,2927,566);step(5)
 assert p.ram()[0xf11c]==255 and p.ram()[0x7e40+18*66]==0,('Key pickup failed',collector)
 print('PASS: native key pickup by P'+str(collector+1)+' removes the loaded passage carpet')

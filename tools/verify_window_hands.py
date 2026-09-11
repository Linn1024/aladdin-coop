"""Native hidden window hands must detect P2, without doubling their attacks."""
exec(compile(open(__file__.replace('verify_window_hands.py','verify_campaign.py')).read().split('for level,name in enumerate(names):')[0],__file__,'exec'))
c.al_probe_player.restype=C.POINTER(C.c_ubyte)
rom=p.rom_path.read_bytes();hand=0x7e40+15*66

def fresh():
 c.al_coop_enable(0);p.restore(seed);c.al_coop_enable(1);step(30);c.al_coop_debug(1);step(2)
 q=rom[0x1b7c88:0x1b7c88+20];o=bytearray(66)
 o[:2]=q[:2];o[6:10]=q[2:6];o[10:14]=q[6:10];o[30:32]=q[10:12];o[32:36]=q[12:16]
 o[41]=q[16];o[53]=q[17];o[60]=q[18];o[2:4]=(280).to_bytes(2,'big');o[4:6]=(848).to_bytes(2,'big');p.write(hand,o)

def position(who,x):
 cx=int.from_bytes(p.ram()[0x7df6:0x7df8],'big')
 for a,v in ((0x7e42,x),(0x7e02,x),(0x7dfa,x-cx)):
  data=v.to_bytes(2,'big')
  if who==0:p.write(a,data)
  else:
   for i,b in enumerate(data):c.al_probe_player(1)[a+i]=b

tracks=[]
for who in (0,1):
 fresh();position(who,240);position(1-who,100);base=save()
 def replay(preview=False):
  track=[]
  for n in range(240):
   step();r=p.ram();track.append((r[hand],r[hand+32:hand+36],r[hand+55]))
   if preview and r[hand]==14:p.screenshot(ROOT/'diagnostics/window-hand-p2-attack.png');preview=False
  assert any(t[0]==14 for t in track),'Window hand never entered its native attack'
  return track,hashlib.sha256(p.frame[0]).hexdigest()
 a=replay(who==1);restore(base);assert replay()==a,'Window-hand save replay diverged'
 tracks.append(a[0]);print('PASS: hidden native hand activates for P'+str(who+1))
assert tracks[0]==tracks[1],'Player identity changes window attack timing'
fresh();position(0,100);position(1,150)
for _ in range(240):step();assert p.ram()[hand]!=14,'Out-of-range player triggered hand'
print('PASS: matching single attack timeline, range gate and deterministic saves')

# Actual reported rooftop save: three hidden knife-throwing window enemies.
reported=(ROOT/'diagnostics/hands-qs1.core',ROOT/'diagnostics/hands-qs1.extra')
if all(f.exists() for f in reported):
 base=tuple(f.read_bytes() for f in reported)
 def check_reported():
  restore(base);attacks=set()
  for n in range(180):
   step();r=p.ram()
   for a in (0x8260,0x8326,0x8368):
    if r[a]==6:attacks.add(a)
   if n==30:p.screenshot(ROOT/'diagnostics/window-qs1-fixed.png')
  assert 0x8326 in attacks,'Window directly above P2 did not activate'
  return attacks,hashlib.sha256(p.frame[0]).hexdigest()
 assert check_reported()==check_reported(),'Reported save replay diverged'
 print('PASS: actual QuickSave1 window above P2 activates and replays')

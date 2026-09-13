"""A partner descending The Escape must not drag an idle player through terrain."""
exec(compile(open(__file__.replace('verify_escape_separation.py','verify_campaign.py')).read().split('for level,name in enumerate(names):')[0],__file__,'exec'))
c.al_probe_player.restype=C.POINTER(C.c_ubyte)
for leader in (0,1):
 stage(7);step(20);follower=1-leader
 initial=status()[0];x,y=initial[3+2*follower:5+2*follower];mid=save()
 def descend(preview=False):
  max_gap=0
  for n in range(100):
   step(one=(1<<7) if leader==0 else 0,two=(1<<7) if leader==1 else 0)
   s,d=status();fx,fy=s[3+2*follower:5+2*follower]
   assert (fx,fy)==(x,y),(leader,n,'Idle player moved through terrain',(x,y),(fx,fy))
   assert d[follower]==8
   max_gap=max(max_gap,s[4+2*leader]-fy)
  assert max_gap>120,'Did not exercise the old vertical-separation clamp'
  # Trying to jump once already separated must not snap below the ledge.
  for n in range(8):
   step(one=(1<<8) if follower==0 else 0,two=(1<<8) if follower==1 else 0)
   assert status()[0][4+2*follower]<=y,(leader,'Jump snapped through upper ledge',status())
  if preview:p.screenshot(ROOT/f'diagnostics/escape-separation-p{leader+1}-fixed.png')
  return status(),hashlib.sha256(p.frame[0]).hexdigest()
 expected=descend(True);restore(mid);assert descend()==expected
 print('PASS: P'+str(leader+1)+' descends; idle partner stays on slope; saved replay matches')
